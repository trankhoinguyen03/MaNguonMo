import socket
import threading

class Client:
    """ Class representing a client """
    def __init__(self):
        self.host = '127.0.0.1'  # Địa chỉ IP
        self.port = 5500  # Cổng

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        print(f"Đã kết nối đến {self.host}:{self.port}")

        self.send_messages()

    def send_messages(self):
        while True:
            message = input("Nhập tin nhắn: ")

            # Gửi tin nhắn đến server
            self.client_socket.send(message.encode())

if __name__ == '__main__':
    client = Client()
