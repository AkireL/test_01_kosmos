import socket
import signal

SERVER_IP = 'localhost'
PORT = 50000

def graceful_exit(signum, frame):

    print("\nClosing connection due to interrupt signal...")
    if 'client_socket' in globals() and client_socket.fileno() != -1:
        client_socket.close()
    exit(0)

# Configurar manejo de señales
signal.signal(signal.SIGINT, graceful_exit)

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Connecting to server at {SERVER_IP}:{PORT}...")
            client_socket.connect((SERVER_IP, PORT))
            print("Connected to server. Type your messages below.")
            
            while True:
                try:
                    message = input("Message ('DESCONEXION' to exit): ")
                    if not message:
                        continue
                    
                    client_socket.sendall(message.encode())
                    
                    response = client_socket.recv(1024)
                    if not response:
                        print("Server closed the connection")
                        break
                    
                    print(f"Server response: {response.decode()}")

                    if message.upper() == "DESCONEXION":
                        print("Closing connection with the server...")
                        break

                except ConnectionResetError:
                    print("Connection reset by server")
                    break
                except ConnectionAbortedError:
                    print("Connection aborted")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break

    except ConnectionRefusedError:
        print("Could not connect to the server. Is it running?")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Client terminated")

if __name__ == "__main__":
    main()