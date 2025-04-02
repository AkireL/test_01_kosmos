import asyncio

HOST = 'localhost'
PORT = 50000
clients = set()  # Conjunto para almacenar clientes activos

async def handle_client(reader, writer):
    """Maneja un cliente de forma asíncrona."""
    addr = writer.get_extra_info('peername')
    print(f"New client connected: {addr}")
    clients.add(writer)

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                raise ConnectionResetError

            message = data.decode().strip()
            print(f"Message from {addr}: {message}")

            response = message.upper().encode()
            writer.write(response)
            await writer.drain()

            if message == "DESCONEXION":
                print(f"Closing connection with {addr}")
                break

    except ConnectionResetError:
        print(f"Client {addr} disconnected unexpectedly.")
    
    finally:
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()
        print(f"Connection with {addr} closed.")

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}...")

    async with server:
        await server.serve_forever()

asyncio.run(main())
