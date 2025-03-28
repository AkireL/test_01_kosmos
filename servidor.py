import socket
import select

HOST = '0.0.0.0'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

clients = []
print("---------------------------------------")
print(f"Server listening on {HOST}:{PORT}...")
print("---------------------------------------")

while True:
    ready_sockets, _, _ = select.select([server_socket] + clients, [], [])

    for s in ready_sockets:
        if s == server_socket:
            client_socket, client_address = server_socket.accept()
            print(f"New client connected: {client_address}")
            clients.append(client_socket)
        else:
            try:
                message = s.recv(1024).decode().strip()
                
                if not message:
                    raise ConnectionResetError

                print(f"A new message of {s.getpeername()}: {message}")
                s.sendall(message.upper().encode())

                if message == "DESCONEXION":
                    print(f"Closing connection with {s.getpeername()}")
                    clients.remove(s)
                    s.close()
            except:
                print(f"Client {s.getpeername()} disconnected.")
                clients.remove(s)
                s.close()
