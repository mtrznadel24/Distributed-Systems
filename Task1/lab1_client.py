import socket
import threading
from contextlib import contextmanager

ASCII_ART = (
    " __         __\n"
    "/  \\.-\"\"\"-./  \\\n"
    "\\    -   -    /\n"
    " |   o   o   |\n"
    " \\  .-'''-.  /\n"
    "  '-\\__Y__/-'\n"
    "     `---`\n"
)

@contextmanager
def dual_socket_client(ip: str, port: int):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((ip, port))

    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'):
        udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    udp_client.bind(('', port))

    try:
        yield tcp_client, udp_client
    finally:
        tcp_client.close()
        udp_client.close()

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

def handle_tcp_receive(client_socket):
    """Handle a TCP socket message"""
    try:
        for message in receive_messages(client_socket):
            print(f"{message}\n# ", end="")
    except Exception as e:
        print(f"Error: {e}")

def handle_udp_receive(client_socket):
    """Handle a UDP socket message"""
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"{message}\n# ", end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    IP = "127.0.0.1"
    PORT = 12345
    NICKNAME = input("Enter Nickname: ")

    try:
        with dual_socket_client(IP, PORT) as (tcp_client, udp_client):

            tcp_client.sendall((NICKNAME + '\n').encode('utf-8'))

            threading.Thread(
                target=handle_tcp_receive,
                args=(tcp_client,),
                daemon=True
            ).start()

            threading.Thread(
                target=handle_udp_receive,
                args=(udp_client,),
                daemon=True
            ).start()

            while True:
                data = input("# ")
                if data == "U":
                    message = f"{NICKNAME}\n{ASCII_ART}".encode('utf-8')
                    udp_client.sendto(message, (IP, PORT))
                else:
                    message = f"{data}\n".encode("utf-8")
                    tcp_client.sendall(message)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
