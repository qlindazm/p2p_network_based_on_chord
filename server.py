

class Server(object):
    def __init__(self):
        self.file_list = []

    def put_file(self, file):
        ''' TODO: store a true file in the future'''
        self.file_list.append(file)
    
    def get_file(self, file):
         ''' return a bool to check if this file is on the server, return the true file in the future '''
         return file in self.file_list


if __name__ == '__main__':
    server = Server()
    server.put_file('test1')
    print('get test1:', server.get_file('test1'))
    print('get test2:', server.get_file('test2'))
