import socket
import threading

class Server:

    def __init__(self):
        self.host = 'localhost'  # Địa chỉ IP
        self.port = 5500  # Cổng

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server đang lắng nghe trên {self.host}:{self.port}")

        self.clients = []

        self.accept_connections()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Kết nối từ {client_address} được chấp nhận")

            self.clients.append(client_socket)

            # Tạo luồng mới cho mỗi kết nối
            threading.Thread(target=self.handle_client, args=[client_socket]).start()

    def handle_client(self, client_socket):
        while True:
            try:
                # Nhận tin nhắn từ client
                message = client_socket.recv(1024).decode()

                # In tin nhắn
                print(f"Nhận được từ {client_socket.getpeername()}: {message}")

                # Gửi tin nhắn đến tất cả các client
                for client in self.clients:
                    if client != client_socket:
                        client.send(message.encode())
            except Exception as e:
                print(f"Lỗi: {e}")
                client_socket.close()
                self.clients.remove(client_socket)
                break

if __name__ == '__main__':
    server = Server()
