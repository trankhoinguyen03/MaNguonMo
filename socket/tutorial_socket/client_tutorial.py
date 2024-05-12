# Import thư viện cần thiết
import socket
import threading

# Khai báo IP và port
host = '127.0.0.1'
port = 5500

# Tạo socket client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Kết nối đến server
client.connect((host, port))

# Gửi nickname cho server
nickname = input("Nhập nickname của bạn: ")
client.send(nickname.encode('ascii'))

# Định nghĩa hàm nhận thông tin từ server
def receive():
    while True:
        try:
            # nhận dữ liệu từ server
            message=client.recv(1024).decode('ascii')
            # nếu message nhận là NICK thì gửi server tên nickname của mình
            if(message=='NICK'):
                client.send(nickname.encode('ascii'))
            else:
            # ngược lại in message
                print(message)
        except:
            print('An error occurred!')
            client.close()
            break

# Định nghĩa hàm viết dữ liệu (chat)
def write():
    while True:
        #Nhập dữ liệu cần gửi
        message=f'{nickname}: {input("")}'
        #gửi dữ liệu
        client.send(message.encode('ascii'))

#tạo thread nhận dữ liệu
receive_thread=threading.Thread(target=receive)
receive_thread.start()
#tạo thread viết dữ liệu (chat)
write_thread=threading.Thread(target=write)
write_thread.start()


# # Nhận thông báo từ server
# message = client.recv(1024).decode('ascii')
# print(message)

# # Vòng lặp để liên tục nhận và gửi tin nhắn
# while True:
#     # Nhập tin nhắn
#     message = input("")

#     # Gửi tin nhắn cho server
#     client.send(message.encode('ascii'))

#     # Nhận tin nhắn từ server
#     message = client.recv(1024).decode('ascii')

#     # In ra tin nhắn
#     print(message)

# # Đóng kết nối với server
# client.close()
