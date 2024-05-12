import socket
import threading

class Client:
    """ Class representing a person  """

    def __init__(self, host, port):
        self.host = host  # Địa chỉ IP
        self.port = port

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Đã kết nối đến {self.host}:{self.port}")
            self.send_messages()
        except ConnectionRefusedError:
            print("Không thể kết nối đến server. Server đã từ chối kết nối.")

    def send_messages(self):
        while True:
            message = input("Nhập tin nhắn: ")

            # Gửi tin nhắn đến server
            self.client_socket.send(message.encode())

if __name__ == '__main__':
    host = 'localhost'
    port = 5500
    client = Client(host, port)


