import socket
import threading
import tkinter

# Khởi tạo socket client
host = '127.0.0.1'
port = 5500
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Hàm nhận tin nhắn từ server
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            msg_list.insert(tkinter.END, message)
        except:
            print('An error occurred!')
            client.close()
            break

# Hàm gửi tin nhắn tới server
def send(event=None):
    message = my_msg.get()
    my_msg.set('')
    client.send(message.encode('utf-8'))
    if message == '{quit}':
        client.close()
        top.quit()

# Hàm xử lý sự kiện đóng cửa sổ
def on_closing(event=None):
    my_msg.set('{quit}')
    send()

# Giao diện người dùng
top = tkinter.Tk()
top.title('Chat Room')

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # Để lưu trữ tin nhắn được gửi
my_msg.set('Nhập tin nhắn của bạn tại đây...')
scrollbar = tkinter.Scrollbar(messages_frame)  # Cuộn tin nhắn

# Danh sách hiển thị tin nhắn
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

# Khung nhập tin nhắn
entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind('<Return>', send)
entry_field.pack()
send_button = tkinter.Button(top, text='Gửi', command=send)
send_button.pack()

# Thực thi giao diện người dùng
top.protocol('WM_DELETE_WINDOW', on_closing)

# Bắt đầu nhận tin nhắn từ server
receive_thread = threading.Thread(target=receive)
receive_thread.start()
tkinter.mainloop()
