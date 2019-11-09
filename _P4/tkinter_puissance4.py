import tkinter as Tk
import socket

class ClientGui:
    def __init__(self, root, game):
        self.root = root
        self.root.title("Puissance 4")

        self.connectionFrame = Tk.Frame(self.root)
        self.connectionLabel = Tk.Label(self.connectionFrame, text="Entrez un nom d'utilisateur")
        self.connectionTextField = Tk.Entry(self.connectionFrame)
        self.connectionValidateButton = Tk.Button(self.connectionFrame, text="Se connecter", command=self.connection)

        self.chooseOpponentFrame = Tk.Frame(self.root)
        self.chooseOpponentLabel = Tk.Label(self.chooseOpponentFrame, text="Choisisez un adversaire")
        self.chooseOpponentList = Tk.Listbox(self.chooseOpponentFrame)
        self.chooseOpponentValidateButton = Tk.Button(self.chooseOpponentFrame, text="Affronter", command=self.chooseopponent)
        self.chooseOpponentWaitButton = Tk.Button(self.chooseOpponentFrame, text="Attendre un adversaire", command=self.wait)

        self.waitFrame = Tk.Frame(self.root)
        self.waitLabel = Tk.Label(self.waitFrame, text="Dans l'attente d'un adversaire...")

        self.mainCanvas = Tk.Canvas(self.root, height=600, width=700)

        self.name = ""
        self.opponents = []
        self.lastMouseX = Tk.IntVar()

        self.game = game
        
        self.connectionLabel.pack()
        self.connectionTextField.pack()
        self.connectionValidateButton.pack()

        self.chooseOpponentLabel.pack()
        self.chooseOpponentList.pack()
        self.chooseOpponentValidateButton.pack()
        self.chooseOpponentWaitButton.pack()

        self.waitLabel.pack()

        self.displayConnection()
    
    def displayConnection(self):
        self.mainCanvas.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.connectionFrame.pack()
        self.unBindMouse()
    
    def displayCanvas(self):
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.mainCanvas.pack()
        self.bindMouse()
    
    def displayChooseOpponent(self):
        self.mainCanvas.pack_forget()
        self.connectionFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.chooseOpponentFrame.pack()
        self.addOpponents()
        self.unBindMouse()
    
    def displayWait(self):
        self.mainCanvas.pack_forget()
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack()
        self.unBindMouse()
    
    def bindMouse(self):
        self.root.bind("<Button 1>",self.updateMouseCoord)
    
    def unBindMouse(self):
        self.root.unbind("<Button 1>")
    
    def connection(self):
        data = self.connectionTextField.get()
        if (data != ""):
            self.name = data
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('localhost', 12345))
            self.socket.send(self.name.encode('utf-8'))
            data = self.socket.recv(255)
            if data.find("/names") != -1:
                self.opponents.clear()
                data = data.replace("/names ", "")
                data = data[1:-2].split(",")
                for d in data:
                    i, name = d[1:-2].split("; ")
                    self.opponents.append((int(i), name))
            self.displayChooseOpponent()
    
    def chooseopponent(self):
        opponent = self.opponents[self.chooseOpponentList.curselection()]
        self.socket.send(bytes("/opp ({}, {})".format(*opponent), 'utf-8'))
        data = self.socket.recv(255)
        if (data.find("/con")) :
            self.game.player = int(data.split()[1])
            self.displayCanvas()
    
    def wait(self):
        data = self.socket.recv(255)
        if (data.find("/con") != -1):
            self.game.player = int(data.split()[1])
            self.displayCanvas()

    def addOpponents(self):
        self.chooseOpponentList.delete(0, Tk.END)
        self.chooseOpponentList.insert(Tk.END, self.opponents)
    
    def addCoin(self, column, line, player):
        color = "red" if player == 1 else "yellow"

        x,y=(column)*100, (line) * 100 

        self.mainCanvas.create_oval(x,y,x+100,y+100, fill=color)
    
    def sendPlayedColumn(self, column):
        self.socket.send(bytes(str(column), 'utf-8'))

    def updateMouseCoord(self, eventorigin):
        x = int(eventorigin.x/100)
        self.lastMouseX.set(x)

    def play(self):
        isCorrectPlay = False
        while self.game.continuePlaying:
            if (self.game.isPlayerTurn):
                while not isCorrectPlay:
                    self.root.wait_variable(self.lastMouseX)
                    isCorrectPlay = self.game.isCorrectPlay(self.lastMouseX.get())
                playedColumn = self.lastMouseX.get()
                isCorrectPlay = False
                self.sendPlayedColumn(playedColumn)
            else :
                playedColumn = 0

            self.game.addCoin(playedColumn)
            self.game.testGameEnd()
            self.game.nextPlayer()
    