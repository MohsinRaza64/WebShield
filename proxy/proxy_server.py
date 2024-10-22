import socket
import threading
from urllib.parse import urlparse
from misp.misp import get_domains
from utils.file_handler import append_to_file, exclude_entries, add_blocked_websites
# blocked_websites = [
#     "example.com",
#     "httpforever.com", # http
#     "instagram.com"
#     # "youtube.com"
# ]

blocked_websites = exclude_entries(get_domains(), 'manual_data/whitelist.txt')
blocked_websites = add_blocked_websites(blocked_websites, 'manual_data/blacklist.txt')

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()

        if request:
            first_line = request.splitlines()[0]
            method = first_line.split()[0]
            url = first_line.split()[1]

            if method == "CONNECT":
                handle_https_tunnel(client_socket, first_line)
            else:
                parsed_url = urlparse(url)
                hostname = parsed_url.hostname

                if hostname and any(blocked_site in hostname for blocked_site in blocked_websites):
                    append_to_file('history/blocked_domains.txt', str(hostname))
                    response = "HTTP/1.1 403 Forbidden\r\n" \
                               "Content-Type: text/html\r\n" \
                               "\r\n" \
                               "<html><body><h1>Blocked by WebShield</h1>" \
                               "<p>This website is blocked for security reasons.</p></body></html>"
                    client_socket.send(response.encode())
                elif hostname:
                    forward_http_request(client_socket, parsed_url, request)
                else:
                    response = "HTTP/1.1 400 Bad Request\r\n" \
                               "Content-Type: text/html\r\n" \
                               "\r\n" \
                               "<html><body><h1>Bad Request</h1>" \
                               "<p>Malformed URL or missing hostname.</p></body></html>"
                    client_socket.send(response.encode())
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def forward_http_request(client_socket, parsed_url, request):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((parsed_url.hostname, parsed_url.port or 80))
        server_socket.send(request.encode())

        while True:
            response = server_socket.recv(4096)
            if not response:
                break
            client_socket.send(response)
    except Exception as e:
        print(f"Error forwarding request: {e}")
    finally:
        server_socket.close()

def handle_https_tunnel(client_socket, first_line):
    try:
        target_host, target_port = first_line.split()[1].split(':')

        if any(blocked_site in target_host for blocked_site in blocked_websites):
            append_to_file('history/blocked_domains.txt', str(target_host))
            response = "HTTP/1.1 403 Forbidden\r\n" \
                       "Content-Type: text/html\r\n" \
                       "\r\n" \
                       "<html><body><h1>Blocked by WebShield</h1>" \
                       "<p>This website is blocked for security reasons.</p></body></html>"
            client_socket.send(response.encode())
            
        else:
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_host, int(target_port)))

            client_socket.send("HTTP/1.1 200 Connection Established\r\n\r\n".encode())

            client_socket.setblocking(False)
            target_socket.setblocking(False)

            while True:
                try:
                    client_data = client_socket.recv(4096)
                    if client_data:
                        target_socket.send(client_data)
                except:
                    pass

                try:
                    target_data = target_socket.recv(4096)
                    if target_data:
                        client_socket.send(target_data)
                except:
                    pass

    except Exception as e:
        print(f"Error handling HTTPS tunnel: {e}")
    finally:
        client_socket.close()
        target_socket.close()
def start_proxy():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind(('localhost', 8888)) 
    proxy.listen(5)

    print("Proxy server running on port 8888...")

    while True:
        client_socket, client_address = proxy.accept()
        print(f"Connection from {client_address}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
