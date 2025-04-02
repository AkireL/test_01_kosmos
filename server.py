import asyncio
import signal
from typing import Set

class Server:
    def __init__(self):
        self.clients: Set[asyncio.StreamWriter] = set()
        self.server = None
        self.shutdown_event = asyncio.Event()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        print(f"New client connected: {addr}")
        self.clients.add(writer)

        try:
            while not self.shutdown_event.is_set():
                data = await reader.read(1024)
                if not data:
                    break

                message = data.decode().strip()
                print(f"Message from {addr}: {message}")

                response = message.upper().encode()
                writer.write(response)
                await writer.drain()

                if message == "DESCONEXION":
                    print(f"Closing connection with {addr}")
                    break

        except (ConnectionResetError, ConnectionError, asyncio.CancelledError):
            print(f"Client {addr} disconnected unexpectedly.")
        
        finally:
            if writer in self.clients:
                self.clients.remove(writer)
            if not writer.is_closing():
                writer.close()
                try:
                    await writer.wait_closed()
                    print(f"Connection with {addr} closed properly.")
                except Exception as e:
                    print(f"Error closing connection with {addr}: {e}")

    async def shutdown(self, signal=None):
        if self.shutdown_event.is_set():
            return
            
        print(f"\nShutting down server{' (signal '+str(signal)+')' if signal else ''}...")
        self.shutdown_event.set()

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self.clients:
            print(f"Closing {len(self.clients)} client connections...")
            close_tasks = []
            for writer in self.clients.copy():
                if not writer.is_closing():
                    writer.close()
                    close_tasks.append(writer.wait_closed())
            
            try:
                await asyncio.wait_for(asyncio.gather(*close_tasks), timeout=5.0)
                print("All client connections closed successfully.")
            except asyncio.TimeoutError:
                print("Warning: Some connections didn't close gracefully")

        print("Server shutdown complete.")

    async def start(self):
        """Inicia el servidor."""
        self.server = await asyncio.start_server(self.handle_client, HOST, PORT)
        addr = self.server.sockets[0].getsockname()
        print(f"Server listening on {addr}... Press Ctrl+C to stop")

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, 
                lambda s=sig: asyncio.create_task(self.shutdown(s)))
        
        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if self.server and self.server.is_serving():
                await self.shutdown()

HOST = 'localhost'
PORT = 50000

async def main():
    server = Server()
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        print("Server process terminated.")