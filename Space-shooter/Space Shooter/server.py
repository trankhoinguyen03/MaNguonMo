import socket
import threading

class Server:
    def __init__(self, max_connections_callback=None):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 5500
        self.max_connections = 2
        self.current_connections = 0
        self.max_connections_reached = False

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server dang lang nghe tren {self.host}:{self.port}")

        self.clients = []
        self.max_connections_callback = max_connections_callback

        self.accept_connections()

    def accept_connections(self):
        while True:
            if self.current_connections < self.max_connections:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Ket noi tu {client_address} duoc chap nhan")

                    self.clients.append(client_socket)
                    self.current_connections += 1

                    threading.Thread(target=self.handle_client, args=[client_socket]).start()

                    # Kiem tra neu da du ket noi, gui thong bao den tat ca client
                    if self.current_connections == self.max_connections:
                        print("Da du ket noi, gui thong bao den tat ca client")
                        for client in self.clients:
                            try:
                                client.send("ready_to_start".encode())
                            except Exception as e:
                                print(f"Loi khi gui thong bao den client: {e}")
                except Exception as e:
                    print(f"Loi khi chap nhan ket noi: {e}")

            elif not self.max_connections_reached:
                print("Da dat den so luong ket noi toi da, tu choi ket noi moi.")
                self.max_connections_reached = True
                if self.max_connections_callback:
                    self.max_connections_callback()  # Goi ham callback

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode()

                if not message:
                    break

                print(f"Nhan duoc tu {client_socket.getpeername()}: {message}")

                for client in self.clients:
                    if client is not client_socket and isinstance(client, socket.socket):
                        try:
                            client.send(message.encode())
                        except Exception as e:
                            print(f"Loi khi gui thong diep den client: {e}")

        except ConnectionResetError:
            print(f"Client {client_socket.getpeername()} da dong ket noi mot cach bat ngo.")
        except Exception as e:
            print(f"Loi khi xu ly client {client_socket.getpeername()}: {e}")
        finally:
            client_socket.close()  # Dong ket noi voi client
            self.clients.remove(client_socket)
            self.current_connections -= 1


def max_connections_reached_callback():
    # Thong bao cho main khi may chu dat den so luong ket noi toi da
    print("May chu da dat den so luong ket noi toi da.")

# Tao mot bien global de luu tru thong tin may chu
server_instance = Server(max_connections_callback=max_connections_reached_callback)
