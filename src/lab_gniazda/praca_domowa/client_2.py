import socket
import threading


class Client:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 9011

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.sendto(bytes("-", 'cp1250'), (self.HOST, self.PORT))
            self.tcp_socket = s
            x = threading.Thread(target=self.speak, args=(s,))
            x.start()
            udp_listen_thread = threading.Thread(target=self.listen_udp, args=(self.udp_socket, ))
            udp_listen_thread.start()
            while True:
                data = s.recv(1024)
                if not data:
                    break
                print(f"\r{data.decode('cp1250')}")
                print("Type message:", end="")

    def speak(self,s):
        while True:
            msg = input("Type message: ")
            if msg.lower() == "u":
                self.send_random_image(self.udp_socket)
            else:
                s.sendall(bytes(f"user{s.getsockname()[1]}: {msg}", 'cp1250'))

    def send_random_image(self, udp_socket):
            image_data = input()
            udp_socket.sendto(bytes(f"user{self.tcp_socket.getsockname()[1]}:\n" + image_data, 'cp1250'), (self.HOST, self.PORT))
            print("Image sent successfully!")

    def listen_udp(self, udp_socket):
        while True:
            buff, address = udp_socket.recvfrom(1024)
            print(f"\r{str(buff, 'cp1250')}")
            print("Type message:", end="")


if __name__ == "__main__":
    client = Client()