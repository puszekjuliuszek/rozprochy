import socket
import struct
import threading
from math import ceil,log10


class Client:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 9011
        self.MCAST_GRP = '224.1.1.1'
        self.MCAST_PORT = 5007
        self.MULTICAST_TTL = 2

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.tcp_socket:
            self.tcp_socket.connect((self.HOST, self.PORT))

            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.sendto(bytes("-", 'cp1250'), (self.HOST, self.PORT))

            multicast_listen_thread = threading.Thread(target=self.listen_multicast)
            multicast_listen_thread.start()

            send_tcp_thread = threading.Thread(target=self.send_tcp, args=())
            send_tcp_thread.start()

            udp_listen_thread = threading.Thread(target=self.listen_udp, args=())
            udp_listen_thread.start()
            while True:
                data = self.tcp_socket.recv(1024)
                if not data:
                    break
                print(f"\r{data.decode('cp1250')}")
                print("Type message:", end="")

    def send_tcp(self):
        while True:
            msg = input("Type message: ")
            if msg.lower() == "u":
                self.send_udp()
            elif msg.lower() == "m":
                self.send_multicast()
            else:
                self.tcp_socket.sendall(bytes(f"user{self.tcp_socket.getsockname()[1]}: {msg}", 'cp1250'))

    def send_udp(self):
        image_data = input()
        self.udp_socket.sendto(bytes(f"user{self.tcp_socket.getsockname()[1]}:\n" + image_data, 'cp1250'), (self.HOST, self.PORT))
        print("Message sent via udp to server")

    def listen_udp(self):
        while True:
            buff, address = self.udp_socket.recvfrom(1024)
            print(f"\r{str(buff, 'cp1250')}")
            print("Type message:", end="")

    def listen_multicast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            msg = sock.recv(10240)
            if str(msg[4:ceil(log10(self.tcp_socket.getsockname()[1]))+4], "cp1250") != str(self.tcp_socket.getsockname()[1]):
                print(f"\r{str(msg, 'cp1250')}")
                print("Type message:", end="")

    def send_multicast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MULTICAST_TTL)

        image_data = input()
        sock.sendto(bytes(f"user{self.tcp_socket.getsockname()[1]}:\n" + image_data, 'cp1250'), (self.MCAST_GRP, self.MCAST_PORT))
        print("Message sent via udp multicast")


if __name__ == "__main__":
    client = Client()