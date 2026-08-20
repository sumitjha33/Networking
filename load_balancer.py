import socket
import threading
import time
from queue import Queue

q = Queue()

HOST = "127.0.0.1"
PORT = 8080

BACKEND_HOST = "127.0.0.1"
BACKEND_PORTS = [5001, 5002, 5003]

info = {}

def checking_the_health():

    while True:

        print(info)

        time.sleep(5)

        for port in BACKEND_PORTS:

            backend_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            backend_socket.settimeout(1)

            try:

                backend_socket.connect(
                    (BACKEND_HOST, port)
                )

                backend_socket.sendall(
                    b"GET / HTTP/1.1\r\n"
                    b"Host: localhost\r\n"
                    b"Connection: close\r\n"
                    b"\r\n"
                )

                response = backend_socket.recv(4096)

                if response:
                    info[port] = "Healthy"
                else:
                    info[port] = "Unhealthy"

            except Exception as e:

                info[port] = "Unhealthy"

            finally:

                backend_socket.close()

threading.Thread(
    target=checking_the_health,
    daemon=True
).start()


for port in BACKEND_PORTS:
    q.put(port)


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (HOST, PORT)
)

server.listen(5)

print(
    f"Server running at http://{HOST}:{PORT}"
)


def processing_the_client(client_socket, addr):

    try:

        print("Processing:", addr)

        request = client_socket.recv(4096).decode(
            "utf-8"
        )

        BACKEND_PORT = None

        for _ in range(len(BACKEND_PORTS)):

            port = q.get()

            if info.get(port) == "Healthy":

                BACKEND_PORT = port

                q.put(port)

                break

            q.put(port)

        if BACKEND_PORT is None:

            response = (
                b"HTTP/1.1 503 Service Unavailable\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: 20\r\n"
                b"Connection: close\r\n"
                b"\r\n"
                b"No healthy backend"
            )

            client_socket.sendall(response)

            return

        print(
            f"{addr} -> Backend {BACKEND_PORT}"
        )

        backend_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        backend_socket.settimeout(5)

        try:

            backend_socket.connect(
                (BACKEND_HOST, BACKEND_PORT)
            )

            # Forward client request
            backend_socket.sendall(
                request.encode("utf-8")
            )

            # Receive backend response
            response = backend_socket.recv(4096)

            while response:

                client_socket.sendall(response)

                response = backend_socket.recv(4096)

        except Exception as e:

            print(
                f"Backend {BACKEND_PORT} error: {e}"
            )

        finally:

            backend_socket.close()

    except Exception as e:

        print(
            f"Client {addr} error: {e}"
        )

    finally:

        client_socket.close()


def handling():

    while True:

        client_socket, addr = server.accept()

        print(
            "Connected:",
            addr
        )

        threading.Thread(
            target=processing_the_client,
            args=(client_socket, addr),
            daemon=True
        ).start()


handling()