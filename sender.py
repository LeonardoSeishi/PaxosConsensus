import json
from sockets import ClientSocket
from threading import Timer

#Mensagem para comunicação entre os Nodos
class Message:
    def __init__(self, type, ticket, value, nid):
        self.type = type
        self.value = value
        self.nid = nid
        self.ticket = ticket

    def __str__(self):
        return "type: " + str(self.type) + ", nid: " + str(self.nid) + ", ticket: " + str(self.ticket) + ", value: " + str(self.value)


def make_msg(type, ticket, value, nid):
    message = Message(type, ticket, value, nid)
    return json.dumps(message.__dict__).encode('utf-8')



#Classe responsável por enviar mensagens
#Recebe o endereço do server para enviar a mensagem
class Sender:
    def __init__(self, server_address, delay=0):
        self.server_ip = Sender.parse_ip(server_address[0])
        self.server_port = Sender.parse_port(server_address[1])
        self.out_buff = []
        self.delay = delay

        try:
            self.client = ClientSocket(mode=self.server_ip, port=int(self.server_port))
        except Exception:
            self.out_buff.clear()
            raise ConnectionError('Client socket cannot be initialized')

        print("Connected to Server Address: ", server_address)

    def __str__(self):
        return "ip: " + self.server_ip + \
               "\nport: " + self.server_port + \
               "\ndelay: " + str(self.delay) + \
               "buffer: " + str(self.out_buff)

    def send_message(self):
        for data in self.out_buff:
            t = Timer(float(self.delay), self.client.send, args=[data])
            t.start()
        self.out_buff.clear()

    def add_message_to_out_buff(self, message):
        self.out_buff.append(message)

    def close(self):
        self.client.close()

    def get_server_address(self):
        return self.server_ip, self.server_port

    @staticmethod
    def parse_ip(ip):
        return '.'.join(str(int(part)).zfill(3) for part in ip.split('.'))

    @staticmethod
    def parse_port(port):
        return str(int(port)).zfill(5)

    @staticmethod
    def parse_address(address):
        return Sender.parse_ip(address[0]), Sender.parse_port(str(address[1]))