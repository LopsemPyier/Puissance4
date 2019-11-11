def getDefaultGrid():
    return [[0 for _ in range(7)] for _ in range(6)]


class Game:
    def __init__(self, grid, player):
        self.grid = grid
        self.player = player
        self.numPlayer = 1
        self.continuePlaying = True
        self.playedTurn = True
    
    def isPlayerTurn(self):
        return self.player == self.numPlayer
    
    def isCorrectPlay(self, column):
        return self.getLastIndexWithoutCoin(column) != -1
    
    def addCoin(self, column):
        line = self.getLastIndexWithoutCoin(column)
        self.grid[line][column] = self.numPlayer
    
    def getLastIndexWithoutCoin(self, column):
        max_L = -1
        for i, line in enumerate(self.grid):
            if line[column] == 0:
                max_L = max(i, max_L)
        return max_L
    
    def nextPlayer(self):
        self.numPlayer = 3 - self.numPlayer
    
    def testGameEnd(self):
        self.continuePlaying = self.testGridFull() or self.testVictory()

    def testGridFull(self):
        return not(all([all(line) for line in self.grid]))
        
    def testVictory(self):
        return self.testVictoireDiagonal() or self.testVictoryColumn() or self.testVictoireLine()
        
    def testVictoryColumn(self):
        for L in range(len(self.grid)):
            for i in range(len(self.grid[L])-3):
                if self.grid[L][i:i+4] == [self.numPlayer]*4:
                    return True
        return False
        
    def testVictoireLine(self):
        for i in range(len(self.grid)-3):
            for L in range(len(self.grid[i])):
                if self.grid[i][L] + self.grid[i+1][L] + self.grid[i+2][L] + self.grid[i+3][L] == [self.numPlayer]*4:
                    return True
        return False


    def testVictoireDiagonal(self):
        for i in range(len(self.grid)-3):
            for L in range(len(self.grid[i])-3):
                if self.grid[i][L] + self.grid[i+1][L+1] + self.grid[i+2][L+2] + self.grid[i+3][L+3] == [self.numPlayer]*4:
                    return True
        return False
