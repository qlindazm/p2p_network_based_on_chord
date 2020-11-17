from communication import CommunicationComponent
from storage import StorageComponent
import utils
import settings
import threading
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('Server')

class Daemon(threading.Thread):
    def __init__(self, obj, method, argv = ""):
        threading.Thread.__init__(self)
        self.obj_ = obj
        self.method_ = method
        self.argv = argv

    def run(self):
        if self.argv == "":
            self.result = getattr(self.obj_, self.method_)()
        else:
            self.result = getattr(self.obj_, self.method_)(self.argv)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

class Server(object):
    def __init__(self, ip, port):
        self.sc = StorageComponent()
        self.cc = CommunicationComponent(ip, port, self)
        self.addr = ip + ':' + port
        self.daemons = {'run': Daemon(self.cc, 'run')}
        self.daemons['run'].start()

    def _get_ft(self) -> str:
        rep = ""
        if self.finger_table:
            for (n, succ) in self.finger_table:
                succ = utils.hash_m(succ)
                rep += str(n) + " " + str(succ) + "\n"
        return rep

    def _get_n(self) -> str:
        return str(utils.hash_m(self.addr))

    def _ls(self) -> str:
        return str(self.sc.ls())

    def _touch(self, request: str) -> str:
        self.sc.touch(request)
        return 'touch file succeed'

    def _rm(self, request: str) -> str:
        return self.sc.rm(request)

    def _cat(self, request: str) -> str:
        return self.sc.cat(request)

    def _write(self, request: str) -> str:
        request = request.strip().split()
        if(len(request) != 2):
            return "Incorrect command format, should be write filename content"
        file_name, content = request
        return self.sc.write(file_name, content)

    def find_thread(self, file):
        file = int(file)
        flag = -1
        for (i, (n, succ)) in enumerate(self.finger_table):
            if utils.in_range(file, "[" + str(utils.hash_m(succ)) + "," + str(1<<settings.__m__) + ")"):
                flag = i
        if flag == -1:
            return self.finger_table[0][1]
        else:
            cmd = "find " + str(file)
            return self.cc.send(cmd, self.finger_table[flag][1])

    def _find(self, file: str):
        log.info("find: " + file)
        f = Daemon(self, "find_thread", file)
        f.start()

        return f.get_result()

    def join_thread(self, request):
        log.debug("origin request: " + request)
        request = request.strip().split()
        log.debug("split[0] request: " + request[0])
        addr, hop, node_num = request
        _n = utils.hash_m(addr)
        hop = int(hop)
        node_num = int(node_num)
        next_addr = self.finger_table[0][1]
        # 1. modify self.finget_table
        # also used for receive exist nodes without a new cmd
        for (i, (n, succ)) in enumerate(self.finger_table):
            succ = utils.hash_m(succ)
            range = "[" + str(n) + "," + str(succ) + ")"
            if utils.in_range(_n, range):
                log.debug(str(_n) + " in range " + range + ". Modify!")
                self.finger_table[i] = (self.finger_table[i][0], addr)
        if hop <= node_num:
            # 2. send self.secuccessor the same cmd except increased hop
            cmd = "join " + addr + " " + str(hop + 1) + " " + str(node_num)
            self.cc.send(cmd, next_addr)
            # 3. let addr know self.addr
            cmd = "join " + self.addr + " " + str(node_num + 1) + " " + str(node_num)
            self.cc.send(cmd, addr)
            # TODO: 4. file transfer
        log.debug("current finger_t: ")
        for (n, addr) in self.finger_table:
            log.debug(str(n) + " " + addr + " " + str(utils.hash_m(addr)))

    def _join(self, request: str) -> str:
        log.debug("request in _join: " + request)
        if(len(request.strip().split()) != 3):
            return "Incorrect command format, should be join addr hop node_num"
        self.daemons['join'] = Daemon(self, "join_thread", request)
        self.daemons['join'].start()

        return "Received join command from " + request


    def join(self, remote_node: str, node_num: str):
        """Join a exist p2p network acording to one of node in them.

        Create a finger table when and only when the join() method was called.
        Should call the method manually.
        :param remote_node: address of the remote node.
        :param node_num: total number of nodes in the p2p network.
        :return: current finger table
        """
        _n = utils.hash_m(self.addr)

        self.finger_table = [((_n+2**i) % (1<<settings.__m__), self.addr) for i in range(settings.__m__)]  # a little diff

        if remote_node != '':
            cmd = "join " + self.addr + " 1 " + node_num
            log.info("join to p2p network " + remote_node + "with cmd: " + cmd)
            response = self.cc.send(cmd, remote_node)
            log.debug("remote: " + remote_node + "said: " + response)

    def leave_thread(self, request):
        request = request.strip().split()
        addr, succ_addr, hop, node_num = request
        hop = int(hop)
        node_num = int(node_num)
        next_addr = self.finger_table[0][1]
        # 1. modify self.finget_table
        for (i, (n, succ)) in enumerate(self.finger_table):
            if succ == addr:
                self.finger_table[i] = (self.finger_table[i][0], succ_addr)
        if hop <= node_num:
            # 2. send self.secuccessor the same cmd except increased hop
            cmd = "leave " + addr + " "  + succ_addr + " " + str(hop + 1) + " " + str(node_num)
            self.cc.send(cmd, next_addr)

        log.debug("current finger_t: ")
        for (n, addr) in self.finger_table:
            log.debug(str(n) + " " + addr + " " + str(utils.hash_m(addr)))

    def _leave(self, request: str) -> str:
        if(len(request.strip().split()) != 4):
            return "Incorrect command format, should be leave addr succ hop node_num"
        self.daemons['leave'] = Daemon(self, "leave_thread", request)
        self.daemons['leave'].start()

        return "Received leave command from " + request

    def leave(self, node_num: str):
        #1. transfer file
        #2. tell others i'm going to leave
        cmd = "leave " + self.addr + " " + self.finger_table[0][1] + " 1 " + node_num
        log.info("leave the network with cmd: " + cmd)
        self.cc.send(cmd, self.finger_table[0][1])

    def circleTest(self, addr):
        """test if there is a circle in nested call

        :param addr: self.addr
        :return: None
        """
        self.cc.send('circleTest '+self.cc.ip+':'+self.cc.port, addr)



if __name__ == '__main__':
    import sys
    # default_ip = '188.131.179.178'
    default_ip = '192.168.1.236'

    if len(sys.argv) == 6:
        server = Server(ip=sys.argv[1], port=sys.argv[2])
        server.join(sys.argv[3]+":"+sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 4:
        server = Server(ip=default_ip, port=sys.argv[1])
        server.join(default_ip+":"+sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2:
        server = Server(ip=default_ip, port=sys.argv[1])
        server.join("", "0")
    else:
        print("usage: python server.py localIp localPort remoteIp remotePort totalNodes")