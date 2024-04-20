import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5555))  # Bind địa chỉ IP và port
    server_socket.listen()

    print("Server started, waiting for connections...")
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected by {addr}")

        # Bắt đầu một luồng mới để xử lý kết nối với client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()



import threading

def handle_client(client_socket, address):
    # Xử lý kết nối với client
    print(f"Connected with {address}")

    # Hàm để gửi tin nhắn từ server tới client
    def send_message(message):
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to {address}: {e}")

    # Hàm con để nhận tin nhắn từ client
    def receive_messages():
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"Received message from {address}: {message}")
                    # Xử lý tin nhắn nhận được ở đây (nếu cần)
                else:
                    break
        except Exception as e:
            print(f"Error receiving message from {address}: {e}")
        finally:
            client_socket.close()

    # Khởi tạo và bắt đầu luồng để nhận tin nhắn từ client
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    # Gửi tin nhắn từ server tới client (ví dụ)
    send_message("Welcome to the chat room!")

    # Thực hiện việc gửi tin nhắn từ server tới client ở đây (tuỳ theo logic của ứng dụng)

    # Đợi cho đến khi luồng nhận tin nhắn từ client kết thúc
    receive_thread.join()

    # Đóng kết nối với client khi luồng nhận tin nhắn kết thúc
    print(f"Disconnected from {address}")


# Chạy máy chủ trong một thread riêng
import threading
thread = threading.Thread(target=start_server)
thread.start()
