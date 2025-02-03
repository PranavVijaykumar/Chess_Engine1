class GameState():
    def __init__(self):
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.moveLog=[]
        self.whiteToMove=True
        self.whiteKingPos=(7,4)
        self.blackKingPos=(0,4)
    
    def makeMove(self,move):
        self.board[move.startRow][move.startCol]="--"
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove=not(self.whiteToMove)

    def getValidMoves(self):
        return self.getAllPossibleMoves()
    
    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn=self.board[r][c][0]
                if (turn=='w' and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    if piece=='p':
                        self.getPawnMoves(r,c,moves)
                    elif piece=='R':
                        self.getRookMoves(r,c,moves)
                    elif piece=='N':
                        self.getNightMoves(r,c,moves)
                    elif piece=='B':
                        self.getBishopMoves(r,c,moves)
                    elif piece=='Q':
                        self.getQueenMoves(r,c,moves)
                    elif piece=='K':
                        self.getKingMoves(r,c,moves)
        return moves
    
    def isInCheck(self):
        if self.whiteToMove:
            self.kingRow=self.whiteKingPos[0]
            self.kingCol=self.whiteKingPos[1]
            self.frndColor='w'
            self.enemyColor='b'
        else:
            self.kingRow=self.blackKingPos[0]
            self.kingCol=self.blackKingPos[1]
            self.frndColor='b'
            self.enemyColor='w'
        
        for x in range(self.kingRow-1,-1,-1):
                if self.board[x][self.kingCol][0]==self.frndColor:
                    break
                elif self.board[x][self.kingCol][0]==self.enemyColor:
                    break
            for x in range(r+1,8):
                if self.board[x][c][0]=='b':
                    moves.append(Move((r,c),(x,c),self.board).getMoveID())
                    break
                elif self.board[x][c][0]=='w':
                    break
                moves.append(Move((r,c),(x,c),self.board).getMoveID())
            for x in range(c-1,-1,-1):
                if self.board[r][x][0]=='b':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='w':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())
            for x in range(c+1,8):
                if self.board[r][x][0]=='b':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='w':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())

    def getPawnMoves(self,r,c,moves):

        if self.board[r][c][0]=='w': #White's turn
            if c!=0 and self.board[r-1][c-1][0]=='b':
                moves.append(Move((r,c),(r-1,c-1),self.board).getMoveID())
            elif c!=7 and self.board[r-1][c+1][0]=='b':
                moves.append(Move((r,c),(r-1,c+1),self.board).getMoveID())
            if self.board[r-1][c][0]=='-':
                moves.append(Move((r,c),(r-1,c),self.board).getMoveID())
                if r==6 and self.board[4][c][0]=='-':
                    moves.append(Move((r,c),(4,c),self.board).getMoveID())

        elif self.board[r][c][0]=='b': #Blacks turn
            if c!=0 and self.board[r+1][c-1][0]=='w':
                moves.append(Move((r,c),(r+1,c-1),self.board).getMoveID())
            elif c!=7 and self.board[r+1][c+1][0]=='w':
                moves.append(Move((r,c),(r+1,c+1),self.board).getMoveID())
            if self.board[r+1][c][0]=='-':
                moves.append(Move((r,c),(r+1,c),self.board).getMoveID())
                if r==1 and self.board[3][c][0]=='-':
                    moves.append(Move((r,c),(3,c),self.board).getMoveID())

    def getRookMoves(self,r,c,moves):

        if self.board[r][c][0]=='w': #White's turn
            for x in range(r-1,-1,-1):
                if self.board[x][c][0]=='b':
                    moves.append(Move((r,c),(x,c),self.board).getMoveID())
                    break
                elif self.board[x][c][0]=='w':
                    break
                moves.append(Move((r,c),(x,c),self.board).getMoveID())
            for x in range(r+1,8):
                if self.board[x][c][0]=='b':
                    moves.append(Move((r,c),(x,c),self.board).getMoveID())
                    break
                elif self.board[x][c][0]=='w':
                    break
                moves.append(Move((r,c),(x,c),self.board).getMoveID())
            for x in range(c-1,-1,-1):
                if self.board[r][x][0]=='b':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='w':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())
            for x in range(c+1,8):
                if self.board[r][x][0]=='b':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='w':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())

        elif self.board[r][c][0]=='b': #Black's turn
            for x in range(r-1,-1,-1):
                if self.board[x][c][0]=='w':
                    moves.append(Move((r,c),(x,c),self.board).getMoveID())
                    break
                elif self.board[x][c][0]=='b':
                    break
                moves.append(Move((r,c),(x,c),self.board).getMoveID())
            for x in range(r+1,8):
                if self.board[x][c][0]=='w':
                    moves.append(Move((r,c),(x,c),self.board).getMoveID())
                    break
                elif self.board[x][c][0]=='b':
                    break
                moves.append(Move((r,c),(x,c),self.board).getMoveID())
            for x in range(c-1,-1,-1):
                if self.board[r][x][0]=='w':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='b':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())
            for x in range(c+1,8):
                if self.board[r][x][0]=='w':
                    moves.append(Move((r,c),(r,x),self.board).getMoveID())
                    break
                elif self.board[r][x][0]=='b':
                    break
                moves.append(Move((r,c),(r,x),self.board).getMoveID())


    def getNightMoves(self,r,c,moves):
        pass
    def getBishopMoves(self,r,c,moves):

        if self.board[r][c][0]=='w': #White's turn
            x,y=r-1,c-1
            while x!=-1 and y!=-1:
                if self.board[x][y][0]=='b':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='w':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x-=1
                y-=1
            x,y=r-1,c+1
            while x!=-1 and y!=8:
                if self.board[x][y][0]=='b':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='w':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x-=1
                y+=1
            x,y=r+1,c+1
            while x!=8 and y!=8:
                if self.board[x][y][0]=='b':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='w':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x+=1
                y+=1
            x,y=r+1,c-1
            while x!=8 and y!=-1:
                if self.board[x][y][0]=='b':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='w':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x+=1
                y-=1

        elif self.board[r][c][0]=='b': #Black's turn
            x,y=r-1,c-1
            while x!=-1 and y!=-1:
                if self.board[x][y][0]=='w':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='b':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x-=1
                y-=1
            x,y=r-1,c+1
            while x!=-1 and y!=8:
                if self.board[x][y][0]=='w':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='b':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x-=1
                y+=1
            x,y=r+1,c+1
            while x!=8 and y!=8:
                if self.board[x][y][0]=='w':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='b':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x+=1
                y+=1
            x,y=r+1,c-1
            while x!=8 and y!=-1:
                if self.board[x][y][0]=='w':
                    moves.append(Move((r,c),(x,y),self.board).getMoveID())
                    break
                elif self.board[x][y][0]=='b':
                    break
                moves.append(Move((r,c),(x,y),self.board).getMoveID())
                x+=1
                y-=1
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
            
    def getKingMoves(self,r,c,moves):
        if self.board[r][c][0]=='w': #White's Move
            for x in range(r-1,r+2):
                for y in range(c-1,c+2):
                    if (x!=-1 and x!=8) and (y!=-1 and y!=8) and not(x==r and y==c) and self.board[x][y][0]!='w':
                        moves.append(Move((r,c),(x,y),self.board).getMoveID())

        elif self.board[r][c][0]=='b': #Black's Move
            for x in range(r-1,r+2):
                for y in range(c-1,c+2):
                    if (x!=-1 and x!=8) and (y!=-1 and y!=8) and not(x==r and y==c) and self.board[x][y][0]!='b':
                        moves.append(Move((r,c),(x,y),self.board).getMoveID())

        
class Move():
    
    ranksToRows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks={v:k for k,v in ranksToRows.items()}

    filesToCols={"h":7,"g":6,"f":5,"e":4,"d":3,"c":2,"b":1,"a":0}
    colsToFiles={v:k for k,v in filesToCols.items()}


    def __init__(self,startSq,endSq,board):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)
    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    def getMoveID(self):
        return (self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol)
