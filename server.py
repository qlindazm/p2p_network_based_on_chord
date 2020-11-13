from communication import CommunicationComponent
from storage import StorageComponent
import threading

class Daemon(threading.Thread):
    def __init__(self, obj, method):
        threading.Thread.__init__(self)
        self.obj_ = obj
        self.method_ = method

    def run(self):
        getattr(self.obj_, self.method_)()


class Server(object):
    def __init__(self, ip = '188.131.179.178', port = '5000'):
        self.sc = StorageComponent()
        self.cc = CommunicationComponent(ip, port, self)
        self.daemons = {}
        self.daemons['run'] = Daemon(self.cc, 'run')
        self.daemons['run'].start()

    def ls(self) -> str:
        return str(self.sc.ls())

    def touch(self, request: str) -> str:
        self.sc.touch(request)
        return 'touch file succeed'

    def rm(self, request: str) -> str:
        return self.sc.rm(request)

    def cat(self, request: str) -> str:
        return self.sc.cat(request)

    def write(self, request: str) -> str:
        fileName, content = request.strip().split(' ')
        return self.sc.write(fileName, content)

    def circleTest(self, addr):
        '''
        test if there is a circle in nested call
        :param addr: self.addr
        :return: None
        '''
        self.cc.send('circleTest '+self.cc.ip+':'+self.cc.port, addr)



if __name__ == '__main__':
    server = Server(ip='192.168.1.236', port='5000')
    # server.put_file('test1')
    # print('get test1:', server.get_file('test1'))
    # print('get test2:', server.get_file('test2'))
