import socket
import threading

# Khởi tạo socket server
host = '127.0.0.1'
port = 5500
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

# Lưu trữ danh sách các client và nickname của họ
clients = []
nicknames = []

# Hàm broadcast tin nhắn đến tất cả client
def broadcast(message):
    """ """
    for client in clients:
        client.send(message)

# Hàm xử lý kết nối từ client
def handle(client):
    while True:
        try:
            # Nhận tin nhắn từ client
            message = client.recv(1024)
            # Gửi tin nhắn đến tất cả client khác
            broadcast(message)
        except:
            # Xử lý khi client rời khỏi phòng chat
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Hàm nhận kết nối từ client
def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f'Nickname of client is {nickname}')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        client.send('Connected to the server'.encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Khởi động server
print('Server is listening...')
server.listen()
receive()
