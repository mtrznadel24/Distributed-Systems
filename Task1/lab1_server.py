import socket
import threading
from contextlib import contextmanager

clients = {}
clients_lock = threading.Lock()

@contextmanager
def dual_socket_server(port: int, host=''):
    """Context manager for a socket servers."""
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((host, port))
    tcp_server.listen()
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if hasattr(socket, 'SO_REUSEPORT'):
        udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    udp_server.bind(('', port))
    print(f"Server work on port: {port}")

    try:
        yield tcp_server, udp_server
    finally:
        tcp_server.close()
        udp_server.close()

def receive_messages(sock: socket.socket, chunk_size=1024):
    """Receive messages from a TCP socket"""
    buffer = ""
    while True:
        chunk = sock.recv(chunk_size)
        if not chunk:
            break

        buffer += chunk.decode('utf-8')

        while '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            yield message

def broadcast(message: str, sender_socket: socket.socket):
    """Sends a message to all clients without a sender"""
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.sendall(f"{message}\n".encode('utf-8'))
                except Exception as e:
                    print(f"Error: {e}")

def handle_tcp_client(client_socket, client_address):
    """Handle a TCP connection"""
    try:
        message_gen = receive_messages(client_socket)
        nickname = next(message_gen)
    except Exception:
        client_socket.close()
        return

    print(f"Client {nickname} joined from {client_address}")

    with clients_lock:
        clients[client_socket] = nickname

    broadcast(f"{nickname} joined a chat", client_socket)

    try:
        with client_socket:
            for message in message_gen:
                broadcast(f"{nickname}: {message}", client_socket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                del clients[client_socket]

        print(f"Client {nickname} disconnected")
        broadcast(f"Client {nickname} left chat", None)


def handle_udp_server(udp_sock):
    """Handle a UDP connection"""
    while True:
        try:
            data, addr = udp_sock.recvfrom(4096)
            payload = data.decode('utf-8')

            sender_nick, message = payload.split('\n', 1)

            with clients_lock:
                for client_sock, nick in clients.items():
                    if nick != sender_nick:
                        client_ip = client_sock.getpeername()[0]
                        udp_sock.sendto(message.encode('utf-8'), (client_ip, PORT))

        except Exception as e:
            print(f"UDP Error: {e}")


if __name__ == "__main__":
    PORT = 12345
    HOST = ''
    try:
        with dual_socket_server(PORT, HOST) as (tcp_server, udp_server):
            threading.Thread(target=handle_udp_server, args=(udp_server,), daemon=True).start()

            while True:
                client_socket, client_address = tcp_server.accept()

                thread = threading.Thread(
                    target=handle_tcp_client,
                    args=(client_socket, client_address),
                    daemon=True
                ).start()
    except KeyboardInterrupt:
        print("Server stopped")



