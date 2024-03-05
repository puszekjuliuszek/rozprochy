import socket
import threading


class Server:
    def __init__(self):
        self.HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        self.PORT = 9011  # Port to listen on (non-privileged ports are > 1023)
        self.tcp_clients = {}
        self.udp_clients = set()

        new_clients_thread = threading.Thread(target=self.connect_tcp, args=())
        new_clients_thread.start()
        self.handle_udp()


    def connect_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            while True:
                conn, addr_tcp = s.accept()
                self.tcp_clients[addr_tcp[1]] = conn
                setattr(self, f"tcp_client_{addr_tcp[1]}", threading.Thread(target=self.handle_tcp, args=(conn,)))
                getattr(self, f"tcp_client_{addr_tcp[1]}").start()

    def handle_tcp(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                for add, con in self.tcp_clients.items():
                    if con != conn:
                        con.sendall(data)

    def get_upd_addr(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.HOST, self.PORT))
            buff, addr_udp = udp_socket.recvfrom(1024)
            print(addr_udp[1])
            self.udp_clients.add(addr_udp[1])

    def handle_udp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.HOST, self.PORT))
            while True:
                buff, address = udp_socket.recvfrom(1024)
                msg = str(buff, 'cp1250')
                if msg == "-":
                    self.udp_clients.add(address[1])
                else:
                    for add in self.udp_clients:
                        if add != address[1]:
                            udp_socket.sendto(bytes(msg, 'cp1250'), (self.HOST, add))



if __name__=="__main__":
    serwer = Server()







