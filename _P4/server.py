import socket
import threading

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.clients = {}
        self.clientThreads = {}
        self.waitingClient = []
        self.playingThreads = {}
        self.stop = False

    def listen(self):
        self.sock.listen(5)
        i = 0
        while not self.stop:
            client, address = self.sock.accept()
            print('Accepted client')
            self.clients[i] = [client, address, "", False]
            #client.settimeout(60)
            self.clientThreads[i] = (threading.Thread(target = self.listenToClient,args = self.clients[i][:-2] + [i]))
            self.clientThreads[i].start()
            i+=1
        self.sock.close()
        for i,t in self.clientThreads.items():
            t.join()
        for i,t in self.playingThreads.items():
            t.join()
    
    def getClientsNames(self):
        if len(self.waitingClient) == 0:
            return "/noNames"
        out = "/names ["
        for i in self.waitingClient:
            out += "({}; {}),".format(i, self.clients[i][2])
        return out[:-1]+"]"

    def listenToClient(self, client, address, i):
        print('Launched thread')
        data = client.recv(255).decode('utf-8')
        if not data:
            client.close()
            self.clients.pop(i)
            return
        elif data.find("/quit") != -1:
            client.close()
            self.stop = True
            return
        self.clients[i][2] = data
        client.send(self.getClientsNames().encode('utf-8'))
        while not self.clients[i][3]:
            data = ""
            data = client.recv(255).decode('utf-8')
            if not data:
                self.clients.pop(i)
                return
            elif data.find("/up") != -1:
                client.send(self.getClientsNames().encode('utf-8'))
            elif data.find("/wait") != -1:
                self.waitingClient.append(i)
            elif data.find("/opp") != -1:
                id, oppName = data[6:-1].split(", ")
                print(data, id, oppName, self.clients[int(id)][2])
                if self.clients[int(id)][2] == oppName:
                    self.clients[int(id)][0].send(("/con 2 {}".format(self.clients[i][2])).encode('utf-8'))
                    client.send(("/con 1 {}".format(self.clients[int(id)][2])).encode('utf-8'))
                    self.waitingClient.remove(int(id))
                    self.clients[i][3] = True
                    self.clients[int(id)][3] = True
                    self.playingThreads[(i, int(id))] = (threading.Thread(target = self.play,args = (i,int(id))))
                    self.playingThreads[(i, int(id))].start()
        
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
        while continueGame and not self.stop:
            if numPlayer == 1:
                data = self.clients[firstClientId][0].recv(255).decode('utf-8')
                print(data)
                if not data:
                    self.clients[firstClientId][0].close()
                    self.clients[secondClientId][0].send(b"/dis")
                    self.clients.pop(firstClientId)
                    self.clientThreads.pop(firstClientId)
                    break
                elif data.find("/play") != -1:
                    #columnPlayed = int(data[6:])
                    self.clients[secondClientId][0].send(data.encode('utf-8'))
                elif data.find("/full") != -1:
                    self.clients[secondClientId][0].send(data.encode('utf-8'))
                    continueGame = False
                elif data.find("/win") != -1:
                    self.clients[secondClientId][0].send(data.encode('utf-8'))
                    continueGame = False

            else:
                data = self.clients[secondClientId][0].recv(255).decode('utf-8')
                if not data:
                    self.clients[secondClientId][0].close()
                    self.clients[firstClientId][0].send(b"/dis")
                    self.clients.pop(secondClientId)
                    self.clientThreads.pop(secondClientId)
                    break
                if data.find("/play") != -1:
                    #columnPlayed = int(data[6:])
                    self.clients[firstClientId][0].send(data.encode('utf-8'))
                elif data.find("/full") != -1:
                    self.clients[firstClientId][0].send(data.encode('utf-8'))
                    continueGame = False
                elif data.find("/win") != -1:
                    self.clients[firstClientId][0].send(data.encode('utf-8'))
                    continueGame = False
            
            numPlayer = 3 - numPlayer
        
        if self.clientThreads.get(firstClientId):
            print("Relauching firstThread")
            self.clients[firstClientId][3] = False
            self.clientThreads[firstClientId] = (threading.Thread(target = self.listenToClient,args = self.clients[firstClientId][:-1] + [firstClientId]))
            self.clientThreads[firstClientId].start()
        if self.clientThreads.get(secondClientId):
            print("Relauching seconThread")
            self.clients[secondClientId][3] = False
            self.clientThreads[secondClientId] = (threading.Thread(target = self.listenToClient,args = self.clients[secondClientId][:-1] + [secondClientId]))
            self.clientThreads[secondClientId].start()


if __name__ == "__main__":
    print('Listening')
    
    ThreadedServer('',12345).listen()
