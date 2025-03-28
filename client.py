import socket

SERVER_IP = '127.0.0.1'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

while True:
    message = input("Type your message ('DESCONEXION' to exit): ")
    client_socket.sendall(message.encode())
    
    response = client_socket.recv(1024)
    print(f"Server response: {response.decode()}")

    if message == "DESCONEXION":
        print("Closing connection with the server...")
        client_socket.close()
        break
