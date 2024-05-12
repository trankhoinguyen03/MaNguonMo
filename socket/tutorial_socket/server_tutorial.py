#import thư viện

import socket

import threading

#khai báo ip và port

host = '0.0.0.0'

port = 8080

#tạo socket server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind socket với ip và port

server.bind((host, port))

#cho phép server lắng nghe kết nối

server.listen()

#khai báo máng chứa danh sách clients và danh sách nicknames

clients = []

nicknames = []

#định nghĩa hàm gửi message tới tất cả client trong room

def broadcast(message):

    for client in clients:

        client.send(message)

#định nghĩa hàm điều khiến client

def handle(client):

    try:

        while True:

            #nhận message client

            message = client.recv(1024)

            #goi broadcast message

            broadcast(message)

    except:

        #nếu lỗi thì remove client ra khỏi phòng

        index = clients.index(client)

        clients.remove(client)

        client.close()

        nickname = nicknames[index]

        #broadcast thông báo client rời phòng

        broadcast(f'{nickname} left the chat!'.encode('ascii'))

        nicknames.remove(nickname)

#định nghĩa hàm nhận kết nối từ client tới server

def receive():

    while True:

        #chấp nhận kết nối

        client, address = server.accept()

        #thông báo kết nối của client từ address nào

        print(f'Connected with {str(address)}')

        #gửi chuỗi NICK xuống client để nhận tên nickname của client

        client.send('NICK'.encode('ascii'))

        #nhận tên nickname của client

        nickname = client.recv(1024).decode('ascii')

        #add nickname vào màng nicknames để quản lý

        nicknames.append(nickname)

        #add client vào màng client để quản lý

        clients.append(client)

        #in ra màn hình nickname đã join vào room

        print(f'Nickname of client is {nickname}')

        #broadcast thông báo client đã join

        broadcast(f'{nickname} joined the chat!'.encode('ascii'))

        #gửi về client trạng thái đã kết nối được với server

        client.send(b'Connected to the server')

        #tạo thread điều khiến client riêng biệt

        thread = threading.Thread(target=handle, args=(client,))

        #bắt đầu thread

        thread.start()

#gọi hàm nhận thông tin

print('Server is listening...')

receive()