import zmq
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('CommunicationComp')

class CommunicationComponent(object):
    '''Communication support for servers.

    Listening on port, exec commands, send commands, ...

    Attributes:
        ip: A str
        server: A Server() who actually execute commands
    '''
    def __init__(self, ip: str, port: str, server):
        self.ip = ip
        self.port = port
        self.server = server

    def run(self):
        log.info('listening at ' + self.ip + ':' + self.port)
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind('tcp://*:' + self.port)
        while True:
            m = socket.recv().decode('utf-8')
            log.debug("receive command: " + m)
            command = m.strip().split(' ')[0]
            # if command == 'shutdown':
            #     break
            request = m[len(command) + 1:]
            try:
                if len(request) > 0:
                    results = getattr(self.server, command)(request)
                else:
                    results = getattr(self.server, command)()
            except AttributeError:
                log.debug("command not found")
                results = "command NOT found"
            socket.send(results.encode('utf-8'))

    def send(self, message: str, addr: str):
        '''
        :param message: message
        :param addr: in form of "ip:port"
        :return: None
        '''
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://"+ addr)
        log.debug("Connecting to server: " + addr)
        socket.send(message.encode('utf-8'))
        m = socket.recv()
        log.debug("Received from " + addr + ':' + m.decode('utf-8'))


# if __name__ == '__main__':
#     cc = CommunicationComponent()