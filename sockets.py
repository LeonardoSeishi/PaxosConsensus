import sys
import socket
import select
import queue
import errno

#cliente socket
class ClientSocket:
    def __init__(self, mode, port, received_bytes=2048):
        self.connect_ip = mode

        self.connect_port = port
        if type(self.connect_port) != int:
            print("port must be an integer", file=sys.stderr)
            raise ValueError

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_bytes = received_bytes
        self._socket.connect((self.connect_ip, self.connect_port))
        self.closed = False

    def get_port(self):
        return self.connect_port

    def get_ip(self):
        return self.connect_ip

    def send(self, data):
        if type(data) == str:
            data = bytes(data, "UTF-8")

        if type(data) != bytes:
            print("data must be a string or bytes", file=sys.stderr)
            raise ValueError

        self._socket.send(data)
        response = self._socket.recv(self.received_bytes)
        return response

    def close(self):
        if not self.closed:
            self._socket.close()
            self.closed = True




#servidos de comunicação entre os sockets clientes
class ServerSocket:
    def __init__(
            self,
            read_callback,
            max_connections,
            received_bytes):

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.bind(('', 0))
        self.ip = self._socket.getsockname()[0]
        self.port = self._socket.getsockname()[1]
        self.callback = read_callback
        self._max_connections = max_connections
        self.received_bytes = received_bytes

    def run(self):
        self._socket.listen(self._max_connections)

        readers = [self._socket]
        writers = []

        queues = dict()
        IPs = dict()

        while readers:
            #Bloqueia até um socket estar pronto para processar
            read, write, err = select.select(readers, writers, readers)

            for sock in read:
                if sock is self._socket:

                    client_socket, client_ip = self._socket.accept()

                    client_socket.setblocking(False)

                    readers.append(client_socket)

                    queues[client_socket] = queue.Queue()

                    IPs[client_socket] = client_ip
                else:

                    try:
                        data = sock.recv(self.received_bytes)
                    except socket.error as e:
                        if e.errno is errno.ECONNRESET:
                            data = None
                        else:
                            raise e
                    if data:

                        self.callback(IPs[sock], queues[sock], data)

                        if sock not in writers:
                            writers.append(sock)
                    else:

                        if sock in writers:
                            writers.remove(sock)

                        readers.remove(sock)

                        sock.close()

                        del queues[sock]

            for sock in write:
                try:
                    data = queues[sock].get_nowait()
                except queue.Empty:
                    writers.remove(sock)
                else:
                    sock.send(data)

            for sock in err:
                readers.remove(sock)
                if sock in writers:
                    writers.remove(sock)
                sock.close()
                del queues[sock]
