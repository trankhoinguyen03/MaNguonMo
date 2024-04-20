import socket

def client_program():
    host = 'localhost'  # Server hostname (use the same as in your server script)
    port = 4000         # Server port (make sure it matches the server's port)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))  # Connect to the server

        # Receive any additional messages from the server
        while True:
            # Receive messages from the server
            msg = client_socket.recv(1024)
            if not msg:
                break
            print("Received:", msg.decode())
            if "bye" in msg.decode().lower():
                break

            # Get input from the client
            server_input = input("Enter your message: ")
            client_socket.send(server_input.encode())
            if "bye" in server_input.lower():
                break

    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running and listening on port 4000.")

    finally:
        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    client_program()
