import socket
import threading

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.clients = []
        self.clientThreads = []

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            self.clients.append([client, address, ""])
            client.settimeout(60)
            self.clientThreads.append(threading.Thread(target = self.listenToClient,args = self.clients[len(self.clients) - 1] + [len(self.clients) - 1]))
    
    def getClientsNames(self):
        out = "/names ["
        for i in range(self.clients):
            if self.clients[i] != "":
                out += "({}; {}),".format(i, self.clients[i][3])
        return out[:-2]+"]"

    def listenToClient(self, client, address, i):
        size = 255
        data = client.recv(255)
        self.clients[i][3] = data
        client.send(self.getClientsNames())
        data = client.recv(255)
        
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    client.send(response)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    
    ThreadedServer('',12345).listen()