import tkinter as Tk
import socket

class ClientGui:
    def __init__(self, root, game):
        self.root = root
        self.root.title("Puissance 4")
        self.root.resizable(0, 0)
        self.root.geometry("700x650")

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

        self.turnText = Tk.StringVar()
        self.endGameText = Tk.StringVar()

        self.mainFrame = Tk.Frame(self.root)
        self.mainTurnLabel = Tk.Label(self.mainFrame, text=self.turnText)
        self.mainCanvas = Tk.Canvas(self.mainFrame, height=600, width=700)

        self.endGameFrame = Tk.Frame(self.root)
        self.endGameMessageLabel = Tk.Label(self.endGameFrame, text = self.endGameText)
        self.backButton = Tk.Button(self.endGameFrame, text = "Retour au menu", command = self.backToMenu)

        self.name = ""
        self.opponentName = ""
        self.opponents = []
        self.lastMouseX = Tk.IntVar()
        self.lastPlayedValue = Tk.IntVar()

        self.game = game
        
        self.connectionLabel.pack()
        self.connectionTextField.pack()
        self.connectionValidateButton.pack()

        self.chooseOpponentLabel.pack()
        self.chooseOpponentList.pack()
        self.chooseOpponentValidateButton.pack()
        self.chooseOpponentWaitButton.pack()

        self.waitLabel.pack()

        self.mainTurnLabel.pack()
        self.mainCanvas.pack()

        self.endGameMessageLabel.pack()
        self.backButton.pack()	

        self.displayConnection()
    
    def displayConnection(self):
        self.mainFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.endGameFrame.pack_forget()
        self.connectionFrame.pack()
        self.root.title("Puissance 4 - Connexion")
        self.unBindMouse()
    
    def displayCanvas(self):
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.endGameFrame.pack_forget()
        self.mainFrame.pack()
        self.root.title("Puissance 4 - {} vs {}".format(self.name, self.opponentName))
        self.bindMouse()
    
    def displayChooseOpponent(self):
        self.mainFrame.pack_forget()
        self.connectionFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.endGameFrame.pack_forget()
        self.chooseOpponentFrame.pack()
        self.root.title("Puissance 4 - Choix de l'adversaire")
        self.addOpponents()
        self.unBindMouse()
    
    def displayWait(self):
        self.mainFrame.pack_forget()
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.endGameFrame.pack_forget()
        self.root.title("Puissance 4 - En attente d'un adversaire")
        self.waitFrame.pack()
        self.unBindMouse()
    
    def displayNulEndGame(self):
        self.mainFrame.pack_forget()
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.root.title("Puissance 4 - Partie nulle")
        self.endGameFrame.pack()
        self.endGameText.set("Partie nulle")
        self.unBindMouse()

    def displayWinEndGame(self, numPlayer):
        self.mainFrame.pack_forget()
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.root.title("Puissance 4 - {}".format("Partie gagnée" if numPlayer == self.game.player else "Partie perdue"))
        self.endGameFrame.pack()
        self.endGameText.set("Vous avez gagné" if numPlayer == self.game.player else "Vous avez perdu")
        self.unBindMouse()
    
    def displayPlayerDisconnected(self):
        self.mainFrame.pack_forget()
        self.connectionFrame.pack_forget()
        self.chooseOpponentFrame.pack_forget()
        self.waitFrame.pack_forget()
        self.root.title("Puissance 4 - Joueur déconnecté")
        self.endGameFrame.pack()
        self.endGameText.set("{} s'est déconnecté(e)".format(self.opponentName))
        self.unBindMouse()

    def onClosing(self):
        self.root.deletefilehandler(self.socket)
        self.unBindMouse()
        self.socket.close()
        self.root.destroy()
        exit(0)
    
    def bindMouse(self):
        self.root.bind("<Button 1>",self.updateMouseCoord)
    
    def unBindMouse(self):
        self.root.unbind("<Button 1>")

    def bindWindowDestroyed(self):
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
    
    def connection(self):
        data = self.connectionTextField.get()
        if (data != ""):
            self.name = data
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', 12345))
            self.socket.send(self.name.encode('utf-8'))
            data = self.socket.recv(255).decode('utf-8')
            print(data)
            if data.find("/names") != -1:
                self.opponents.clear()
                data = data.replace("/names ", "")
                data = data[1:-1].split(",")
                for d in data:
                    i, name = d[1:-1].split("; ")
                    self.opponents.append((int(i), name))
            elif data.find("/noNames") != -1:
                self.opponents.clear()
            self.bindWindowDestroyed()
            self.displayChooseOpponent()
    
    def chooseopponent(self):
        print(self.chooseOpponentList.curselection())
        opponent = self.opponents[self.chooseOpponentList.curselection()[0]]
        self.socket.send(bytes("/opp ({}, {})".format(*opponent), 'utf-8'))
        data = self.socket.recv(255).decode('utf-8')
        if (data.find("/con") != -1) :
            self.game.player = int(data.split()[1])
            self.opponentName = data.split()[2]
            self.displayCanvas()
            self.play()
    
    def wait(self):
        self.displayWait()
        self.root.update()
        self.socket.send(b"/wait")
        data = self.socket.recv(255).decode('utf-8')
        if (data.find("/con") != -1):
            self.game.player = int(data.split()[1])
            self.opponentName = data.split()[2]
            self.displayCanvas()
            self.play()
    
    def backToMenu(self):
        self.socket.send(self.name.encode('utf-8'))
        data = self.socket.recv(255).decode('utf-8')
        print(data)
        if data.find("/names") != -1:
            self.opponents.clear()
            data = data.replace("/names ", "")
            data = data[1:-1].split(",")
            for d in data:
                i, name = d[1:-1].split("; ")
                self.opponents.append((int(i), name))
        elif data.find("/noNames") != -1:
            self.opponents.clear()
        self.displayChooseOpponent()

    def addOpponents(self):
        self.chooseOpponentList.delete(0, Tk.END)
        for _, n in self.opponents:
            self.chooseOpponentList.insert(Tk.END, n)
    
    def addCoin(self, column, line, player):
        color = "red" if player == 1 else "yellow"

        x,y=(column)*100, (line) * 100 +50

        self.mainCanvas.create_oval(x,y,x+100,y+100, fill=color)
    
    def sendPlayedColumn(self, column):
        self.socket.send(bytes("/play " + str(column), 'utf-8'))

    def updateMouseCoord(self, eventorigin):
        x = int(eventorigin.x/100)
        self.lastMouseX.set(x)

    def updatePlayedValue(self, sock, mask):
        data = sock.recv(255).decode('utf-8')
        print(data)
        if data.find("/play") != -1:
            self.lastPlayedValue.set(int(data.split()[1]))
        elif data.find("/full") != -1:
            self.game.continuePlaying = False
            self.game.playedTurn = False
            self.lastPlayedValue.set(-1)
        elif data.find("/win") != -1:
            self.game.continuePlaying = False
            self.game.playedTurn = False
            self.lastPlayedValue.set(-1)
        elif data.find("/dis") != -1:
            self.game.continuePlaying = False
            self.game.playedTurn = False
            self.lastPlayedValue.set(-1)

    def play(self):
        print("Playing")
        isCorrectPlay = False
        while self.game.continuePlaying:
            print(self.game.isPlayerTurn())
            if (self.game.isPlayerTurn()):
                self.turnText.set("A votre tour de jouer")
                while not isCorrectPlay:
                    self.root.wait_variable(self.lastMouseX)
                    print(self.lastMouseX.get())
                    isCorrectPlay = self.game.isCorrectPlay(self.lastMouseX.get())
                playedColumn = self.lastMouseX.get()
                isCorrectPlay = False
                self.sendPlayedColumn(playedColumn)
            else :
                self.turnText.set("En attente de {} pour jouer")
                self.root.createfilehandler(self.socket, Tk.READABLE, self.updatePlayedValue)
                print("Waiting for socket")
                self.root.wait_variable(self.lastPlayedValue)
                playedColumn = self.lastPlayedValue.get()
                self.root.deletefilehandler(self.socket)

            if self.game.playedTurn:
                self.addCoin(playedColumn, self.game.getLastIndexWithoutCoin(playedColumn), self.game.numPlayer)
                self.game.addCoin(playedColumn)
                self.game.testGameEnd()
                self.game.nextPlayer()

        if (self.game.testGridFull()):
            if self.game.playedTurn:
                self.socket.send(b"/full")
            self.displayNulEndGame()
        elif (self.game.testVictory()):
            if self.game.playedTurn:
                self.socket.send(b"/win")
            self.displayWinEndGame(self.game.numPlayer)
        else :
            if not self.game.playedTurn:
                self.displayPlayerDisconnected()
        
    
