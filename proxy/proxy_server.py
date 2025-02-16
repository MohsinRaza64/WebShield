import socket
import threading
import select
import time
from urllib.parse import urlparse
from misp.misp import get_domains
from utils.file_handler import append_to_file, exclude_entries, add_blocked_websites
import os
import sys

# Get the correct base path (for PyInstaller or normal script execution)
BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath("."))

# Define directory paths
manual_data_dir = os.path.join(BASE_PATH, "manual_data")
history_dir = os.path.join(BASE_PATH, "history")

# Ensure directories exist before using them
os.makedirs(manual_data_dir, exist_ok=True)
os.makedirs(history_dir, exist_ok=True)

# Define file paths
blacklist_file = os.path.join(manual_data_dir, "blacklist.txt")
whitelist_file = os.path.join(manual_data_dir, "whitelist.txt")
blocked_domains_file = os.path.join(history_dir, "blocked_domains.txt")
deleted_files_file = os.path.join(history_dir, "deleted_files.txt")
downloaded_files_file = os.path.join(history_dir, "downloaded_files.txt")


BUFFER_SIZE = 8192  # Increased buffer size for better performance

# Global variables
blocked_websites = set()
blocked_websites_lock = threading.Lock()
proxy_thread = None
stop_event = threading.Event()  # Used to stop threads safely

def refresh_blocked_websites():
    """Safely updates the blocked websites set from external sources."""
    global blocked_websites
    with blocked_websites_lock:
        try:
            new_blocked_websites = set(get_domains()) if get_domains() else set()
            new_blocked_websites = set(exclude_entries(new_blocked_websites, whitelist_file))
            # print(new_blocked_websites)
            new_blocked_websites = add_blocked_websites(new_blocked_websites, blacklist_file)
            # print(new_blocked_websites)
            blocked_websites = new_blocked_websites  # Atomic assignment
        except Exception as e:
            print(f"Error refreshing blocked websites: {e}")

def handle_client(client_socket, dashboard):
    """Handles incoming client requests and filters blocked websites."""
    global blocked_websites
    try:
        request = client_socket.recv(BUFFER_SIZE).decode()
        if request:
            first_line = request.splitlines()[0]
            method, url = first_line.split()[:2]
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname

            # Lock before checking blocked websites
            with blocked_websites_lock:
                print(blocked_websites)
                if hostname and any(blocked_site in hostname for blocked_site in blocked_websites):
                    append_to_file(blocked_domains_file, hostname)
                    if dashboard.winfo_exists():
                        dashboard.setup_blocked_domains_tab()
                    response = (
                        "HTTP/1.1 403 Forbidden\r\n"
                        "Content-Type: text/html\r\n"
                        "\r\n"
                        "<html><body><h1>Blocked by WebShield</h1>"
                        "<p>This website is blocked for security reasons.</p></body></html>"
                    )
                    client_socket.sendall(response.encode())
                    return

            # Handle HTTP and HTTPS requests
            if method == "CONNECT":
                handle_https_tunnel(client_socket, first_line, dashboard)
            elif hostname:
                forward_http_request(client_socket, parsed_url, request)
            else:
                client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def forward_http_request(client_socket, parsed_url, request):
    """Forwards HTTP requests and dynamically checks for new blocked websites."""
    global blocked_websites
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((parsed_url.hostname, parsed_url.port or 80))
            server_socket.sendall(request.encode())

            while True:
                response = server_socket.recv(BUFFER_SIZE)
                if not response:
                    break

                # **Dynamically check for new blocked websites**
                with blocked_websites_lock:
                    if any(blocked_site in parsed_url.hostname for blocked_site in blocked_websites):
                        print(f"Blocking {parsed_url.hostname} dynamically.")
                        append_to_file(blocked_domains_file, parsed_url.hostname)
                        client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                        return

                client_socket.sendall(response)
    except Exception as e:
        print(f"Error forwarding request: {e}")


def handle_https_tunnel(client_socket, first_line, dashboard):
    """Handles HTTPS tunneling through the proxy and dynamically checks for new blocked websites."""
    global blocked_websites
    try:
        target_host, target_port = first_line.split()[1].split(':')
        target_port = int(target_port)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target_socket:
            target_socket.connect((target_host, target_port))
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            sockets = [client_socket, target_socket]
            while True:
                readable, _, _ = select.select(sockets, [], [], 0.5)  # Add timeout for periodic checks

                # **Check if the website is now blocked during runtime**
                with blocked_websites_lock:
                    if any(blocked_site in target_host for blocked_site in blocked_websites):
                        print(f"Blocking {target_host} dynamically.")
                        append_to_file(blocked_domains_file, target_host)
                        if dashboard.winfo_exists():
                            dashboard.setup_blocked_domains_tab()
                        client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                        return  # Close the connection immediately

                for sock in readable:
                    try:
                        data = sock.recv(BUFFER_SIZE)
                        if not data:
                            return
                        (target_socket if sock is client_socket else client_socket).sendall(data)
                    except:
                        return
    except Exception as e:
        print(f"Error handling HTTPS tunnel: {e}")

def proxy_main_loop(dashboard):
    """Main loop for the proxy server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy:
        proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy.bind(('localhost', 8888))
        proxy.listen(5)
        print("Proxy server running on port 8888...")

        while not stop_event.is_set():
            proxy.settimeout(1)  # Allows checking stop_event periodically
            try:
                client_socket, client_address = proxy.accept()
                print(f"Connection from {client_address}")
                threading.Thread(target=handle_client, args=(client_socket, dashboard), daemon=True).start()
            except socket.timeout:
                continue

def start_proxy(dashboard):
    """Starts the WebShield proxy server and background refresh task."""
    global proxy_thread
    if proxy_thread and proxy_thread.is_alive():
        print("WebShield is already running!")
        return

    stop_event.clear()
    refresh_blocked_websites()  # Initial load

    # Start periodic refresh in a separate thread
    def periodic_refresh():
        while not stop_event.is_set():
            refresh_blocked_websites()
            time.sleep(1)  # Refresh every 1 seconds

    refresh_thread = threading.Thread(target=periodic_refresh, daemon=True)
    refresh_thread.start()

    # Start proxy server
    proxy_thread = threading.Thread(target=proxy_main_loop, args=(dashboard,), daemon=True)
    proxy_thread.start()

    print("WebShield started!")

def stop_proxy(dashboard):
    """Stops the WebShield proxy server."""
    global proxy_thread
    stop_event.set()  # Signal all threads to stop

    if proxy_thread and proxy_thread.is_alive():
        proxy_thread.join()  # Wait for the proxy thread to stop

    print("WebShield stopped!")
