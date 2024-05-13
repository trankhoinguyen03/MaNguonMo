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
            self.ready_from_server()
        except ConnectionRefusedError:
            print("Không thể kết nối đến server. Server đã từ chối kết nối.")

    def send_messages(self):
        while True:
            message = input("Nhập tin nhắn: ")

            # Gửi tin nhắn đến server
            self.client_socket.send(message.encode())
    def ready_from_server(self):
        try:
            # Receive message from server
            message = self.client_socket.recv(1024).decode()
            print(message)
        except Exception as e:
            print(f"Error receiving message from server: {e}")
            return None

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    port = 5500
    client = Client(host, port)


