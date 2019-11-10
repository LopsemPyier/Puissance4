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
        self.waitingClient = []
        self.playingThreads = []

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print('Accepted client')
            self.clients.append([client, address, ""])
            client.settimeout(60)
            self.clientThreads.append(threading.Thread(target = self.listenToClient,args = self.clients[len(self.clients) - 1] + [len(self.clients) - 1]))
            self.clientThreads[-1].start()
    
    def getClientsNames(self):
        out = "/names ["
        for i in self.waitingClient:
            out += "({}; {}),".format(i, self.clients[i][3])
        return out[:-2]+"]"

    def listenToClient(self, client, address, i):
        print('Launched thread')
        data = client.recv(255)
        self.clients[i][2] = data
        client.send(self.getClientsNames())
        data = client.recv(255)
        if data.find("/wait") != -1:
            self.waitingClient.append(i)
        elif data.find("/opp") != -1:
            id, oppName = data[6:-2].split(", ")
            if self.clients[int(id)][2] == oppName:
                self.clients[int(id)][0].send("/con 2")
                client.send("/con 1")
                self.waitingClient.remove((id, oppName))
                self.playingThreads.append(threading.Thread(target = self.play,args = (i,int(id))))
                self.playingThreads[-1].start()
        
        """while True:
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
                return False"""
    
    def play(self, firstClientId, secondClientId):
        self.clientThreads[firstClientId].join()
        self.clientThreads[secondClientId].join()

        continueGame = True
        numPlayer = 1
        while continueGame:
            if numPlayer == 1:
                data = self.clients[firstClientId][0].recv(255)
                if data.find("/play") != -1:
                    #columnPlayed = int(data[6:])
                    self.clients[secondClientId][0].send(data)
                elif data.find("/full") != -1:
                    self.clients[secondClientId][0].send(data)
                    continueGame = False
                elif data.find("/win") != -1:
                    self.clients[secondClientId][0].send(data)
                    continueGame = False

            else:
                data = self.clients[secondClientId][0].recv(255)
                if data.find("/play") != -1:
                    #columnPlayed = int(data[6:])
                    self.clients[firstClientId][0].send(data)
                elif data.find("/full") != -1:
                    self.clients[firstClientId][0].send(data)
                    continueGame = False
                elif data.find("/win") != -1:
                    self.clients[firstClientId][0].send(data)
                    continueGame = False
            
            numPlayer = 3 - numPlayer
        
        self.clientThreads[firstClientId].start()
        self.clientThreads[secondClientId].start()



if __name__ == "__main__":
    print('Listening')
    
    ThreadedServer('',12345).listen()