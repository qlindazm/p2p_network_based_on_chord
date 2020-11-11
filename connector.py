from socket import *
from threading import Thread

ENCODING = 'utf-8'

def message_handle(sock, addr, buffSize = 1024):
    sock.send('Hello'.encode(ENCODING))
    data = ''
    while True:
        bytes = sock.recv(buffSize)
        if not bytes:
            break
        data += bytes.decode(ENCODING)
    sock.close()
    print(addr, ' said:', data)

class Connector(object):
    def __init__(self, addr :(str, int), buffSize = 1024):
        self.addr = addr 
        self.listen = True
        self.buffSize = buffSize

    def listening(self):
        self.listen = True
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(self.addr)
        sock.listen(5)
        while self.listen:
            print(self.addr[0], 'listening at: ', self.addr[1])
            c_sock, addr = sock.accept()
            print('recieve socket from: ', addr)
            
            thread = Thread(target=message_handle, args=(c_sock, addr, buffSize,))
            thread.setDaemon(True)
            thread.start()
        sock.close()
        
    
    def no_listening(self):
        print(self.addr, 'no more listening')
        self.listen = False

    def send(self, data, addr):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(addr)
        sock.send(data.encode())
        data_r =  sock.recv(self.buffSize)
        
        if data_r: 
            print(data_r.decode('utf-8'))
        sock.close()



if __name__ == '__main__' :
    c1 = Connector(('127.0.0.1', 65301))
    c2 = Connector(('127.0.0.1', 65302))
    c1.listening()
    c2.send('hello server', ('127.0.0.1', 65301))
    c1.no_listening() 
        
        
