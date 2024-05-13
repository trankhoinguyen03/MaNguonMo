import socket
import threading
import time

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

        print(f"Server đang lắng nghe trên {self.host}:{self.port}")

        self.clients = []
        self.max_connections_callback = max_connections_callback

        self.accept_connections()

    def accept_connections(self):
        while True:
            if self.current_connections < self.max_connections:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Kết nối từ {client_address} được chấp nhận")

                    self.clients.append(client_socket)
                    self.current_connections += 1

                    threading.Thread(target=self.handle_client, args=[client_socket]).start()

                    # Kiểm tra nếu đã đủ kết nối, gửi thông báo đến tất cả client
                    if self.current_connections == self.max_connections:
                        print("Đã đủ kết nối, gửi thông báo đến tất cả client")
                        for client in self.clients:
                            try:
                                client.send("ready_to_start".encode())
                            except Exception as e:
                                print(f"Lỗi khi gửi thông báo đến client: {e}")
                except Exception as e:
                    print(f"Lỗi khi chấp nhận kết nối: {e}")

            elif not self.max_connections_reached:
                print("Đã đạt đến số lượng kết nối tối đa, từ chối kết nối mới.")
                self.max_connections_reached = True
                if self.max_connections_callback:
                    self.max_connections_callback()  # Gọi hàm callback

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode()

                if not message:
                    break

                print(f"Nhận được từ {client_socket.getpeername()}: {message}")

                for client in self.clients:
                    if client is not client_socket and isinstance(client, socket.socket):
                        try:
                            client.send(message.encode())
                        except Exception as e:
                            print(f"Lỗi khi gửi thông điệp đến client: {e}")

        except ConnectionResetError:
            print(f"Client {client_socket.getpeername()} đã đóng kết nối một cách bất ngờ.")
        except Exception as e:
            print(f"Lỗi khi xử lý client {client_socket.getpeername()}: {e}")
        finally:
            client_socket.close()  # Đóng kết nối với client
            self.clients.remove(client_socket)
            self.current_connections -= 1


def max_connections_reached_callback():
    # Thông báo cho main khi máy chủ đạt đến số lượng kết nối tối đa
    print("Máy chủ đã đạt đến số lượng kết nối tối đa.")

# Tạo một biến global để lưu trữ thông tin máy chủ
server_instance = Server(max_connections_callback=max_connections_reached_callback)
