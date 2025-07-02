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
        self.castlingRights={'wK':True,'bK':True,'wR0':True,'wR7':True,'bR0':True,'bR7':True}
        self.enPassant=(False,-1)
         

    def makeMove(self,move):

        self.board[move.startRow][move.startCol]="--"
        self.board[move.endRow][move.endCol]=move.pieceMoved

        if move.pieceMoved=='wK':
            self.whiteKingPos=(move.endRow,move.endCol)

            if self.castlingRights[move.pieceMoved]:

                if move.endCol==6:                  #King side castle
                    self.board[7][7]='--'
                    self.board[7][5]='wR'

                elif move.endCol==2:                #Queen side castle
                    self.board[7][0]='--'
                    self.board[7][3]='wR'

                self.castlingRights[move.pieceMoved]=False

        elif move.pieceMoved=='bK':
            self.blackKingPos=(move.endRow,move.endCol)

            if self.castlingRights[move.pieceMoved]:

                if move.endCol==6:                  #King side castle
                    self.board[0][7]='--'
                    self.board[0][5]='bR'

                elif move.endCol==2:                #Queen side castle
                    self.board[0][0]='--'
                    self.board[0][3]='bR'

                self.castlingRights[move.pieceMoved]=False

        if move.pieceMoved[1]=='R' and (move.startCol==0 or move.startCol==7) and self.castlingRights[move.pieceMoved+str(move.startCol)]:
            self.castlingRights[move.pieceMoved+str(move.startCol)]=False
        
        if self.enPassant[0]:
            if move.pieceMoved[1]=='p' and move.endCol==self.enPassant[1] and move.startRow in (3,4):
                if self.whiteToMove and move.startRow==3:
                    self.board[3][self.enPassant[1]]='--'
                elif not(self.whiteToMove) and move.startRow==4:
                    self.board[4][self.enPassant[1]]='--'
            self.enPassant=(False,-1)
        
        if move.pieceMoved[1]=='p' and (move.startRow-move.endRow==2 or move.endRow-move.startRow==2):
            self.enPassant=(True,move.endCol)
        
        if move.pieceMoved=='wp' and move.endRow==0:
            self.board[0][move.endCol]='wQ'
        if move.pieceMoved=='bp' and move.endRow==7:
            self.board[7][move.endCol]='bQ'

        self.moveLog.append(move)
        self.whiteToMove=not(self.whiteToMove)


    def getValidMoves(self):

        self.pins,self.checks=self.pinsAndChecks()
        self.checkNum=len(self.checks)
        moves=self.getAllPossibleMoves()

        endSqInCheck=[]
        if len(self.checks)==1:
            checkRow=self.checks[0][0]
            checkCol=self.checks[0][1]
            checkDirection=self.checks[0][2]
            r=self.kingRow+checkDirection[0]
            c=self.kingCol+checkDirection[1]

            if self.board[checkRow][checkCol][1]=='N':
                endSqInCheck.append((checkRow,checkCol))

            else:
                while not(r==checkRow+checkDirection[0] and c==checkCol+checkDirection[1]):
                    endSqInCheck.append((r,c))
                    r+=checkDirection[0]
                    c+=checkDirection[1]

            for i in range(len(moves)-1,-1,-1):
                if (moves[i].endRow,moves[i].endCol) not in endSqInCheck and moves[i].pieceMoved[1]!='K':
                    moves.remove(moves[i])
 
        return moves
    


    def pinsAndChecks(self):

        pins=[] #[(startRow,startCol,(rowDirection,colDirection)),...]
        checks=[] #[(startRow,startCol,Direction),...]
        directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

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
        
        for d in directions:
            r=self.kingRow + d[0]
            c=self.kingCol + d[1]
            possiblePin=()
            pawnDist=True
            sameColorFlag=False

            while -1<r<8 and -1<c<8:

                if self.board[r][c][0]==self.frndColor:
                    if sameColorFlag:
                        break
                    possiblePin=(r,c,d)
                    sameColorFlag=True
                    r+=d[0]
                    c+=d[1]
                    pawnDist=False

                elif self.board[r][c][0]==self.enemyColor:
                    if 0<=directions.index(d)<=3 and self.board[r][c][1] in 'RQ':
                        if sameColorFlag:
                            pins.append(possiblePin)
                            break
                        else:
                            checks.append((r,c,d))
                            break

                    elif 4<=directions.index(d)<=7 and self.board[r][c][1] in 'BQ':
                        if sameColorFlag:
                            pins.append(possiblePin)
                            break
                        else:
                            checks.append((r,c,d))
                            break

                    elif pawnDist and self.board[r][c][1]=='p' and self.frndColor=='b' and 4<=directions.index(d)<=5:
                        checks.append((r,c,d))
                        break

                    elif pawnDist and self.board[r][c][1]=='p' and self.frndColor=='w' and 6<=directions.index(d)<=7:
                        checks.append((r,c,d))
                        break

                    else:
                        break

                else:
                    r+=d[0]
                    c+=d[1]
                    pawnDist=False


        knightDirections=[(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        for d in knightDirections:
            r,c=self.kingRow+d[0],self.kingCol+d[1]
            if 0<=r<=7 and 0<=c<=7 and self.board[r][c]==self.enemyColor+'N':
                checks.append((r,c,d))
                break

        return pins,checks     
    


    def willBeCheck(self,r,c):
        directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

        for d in directions:
            x=r+d[0]
            y=c+d[1]
            pawnDist=True

            while -1<x<8 and -1<y<8:

                if self.board[x][y][0]==self.frndColor:
                    break

                elif self.board[x][y][0]==self.enemyColor:
                    if 0<=directions.index(d)<=3 and self.board[x][y][1] in 'RQ':
                        return True

                    elif 4<=directions.index(d)<=7 and self.board[x][y][1] in 'BQ':
                        return True

                    elif pawnDist and self.board[x][y][1]=='p' and self.frndColor=='b' and 4<=directions.index(d)<=5:
                        return True

                    elif pawnDist and self.board[x][y][1]=='p' and self.frndColor=='w' and 6<=directions.index(d)<=7:
                        return True

                    elif pawnDist and self.board[x][y][1]=='K':
                        return True

                    else:
                        break
                    
                else:
                    x+=d[0]
                    y+=d[1]
                    pawnDist=False
    

        knightDirections=[(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        for d in knightDirections:
            x,y=r+d[0],c+d[1]
            if 0<=x<=7 and 0<=y<=7 and self.board[x][y]==self.enemyColor+'N':
                return True

        else:
            return False


    
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


    def getPawnMoves(self,r,c,moves):

        if self.checkNum==2:
            doubleCheck=True
        else:
            doubleCheck=False

        if not(doubleCheck):
            piecePinned=False
            pinnedDirection=()
            for i in range(len(self.pins)-1,-1,-1):
                if r==self.pins[i][0] and c==self.pins[i][1]:
                    piecePinned=True
                    pinnedDirection=self.pins[i][2]
                    self.pins.remove(self.pins[i])
                    break

            if self.board[r][c][0]=='w': #White's turn

                if c!=0 and self.board[r-1][c-1][0]=='b':
                    if piecePinned:
                        if pinnedDirection==(-1,-1):
                            moves.append(Move((r,c),(r-1,c-1),self.board))
                    else:
                        moves.append(Move((r,c),(r-1,c-1),self.board))

                if c!=7 and self.board[r-1][c+1][0]=='b':
                    if piecePinned:
                        if pinnedDirection==(-1,1):
                            moves.append(Move((r,c),(r-1,c+1),self.board))
                    else:
                        moves.append(Move((r,c),(r-1,c+1),self.board))

                if self.board[r-1][c][0]=='-':
                    if piecePinned:
                        if pinnedDirection in [(-1,0),(1,0)]:
                            moves.append(Move((r,c),(r-1,c),self.board))
                    else:
                        moves.append(Move((r,c),(r-1,c),self.board))
                    if r==6 and self.board[4][c][0]=='-':
                        if piecePinned:
                            if pinnedDirection in [(-1,0),(1,0)]:
                                moves.append(Move((r,c),(4,c),self.board))
                        else:
                            moves.append(Move((r,c),(4,c),self.board))

                if self.enPassant[0] and r==3 and c in (self.enPassant[1]-1,self.enPassant[1]+1):
                    if piecePinned:
                        if c==self.enPassant[1]-1 and pinnedDirection==(-1,-1):
                            moves.append(Move((3,c),(2,self.enPassant[1]),self.board))
                        elif c==self.enPassant[1]+1 and pinnedDirection==(-1,1):
                            moves.append(Move((3,c),(2,self.enPassant[1]),self.board))
                    else:
                        moves.append(Move((3,c),(2,self.enPassant[1]),self.board))

            elif self.board[r][c][0]=='b': #Black's turn

                if c!=0 and self.board[r+1][c-1][0]=='w':
                    if piecePinned:
                        if pinnedDirection==(1,-1):
                            moves.append(Move((r,c),(r+1,c-1),self.board))
                    else:
                        moves.append(Move((r,c),(r+1,c-1),self.board))

                if c!=7 and self.board[r+1][c+1][0]=='w':
                    if piecePinned:
                        if pinnedDirection==(1,1):
                            moves.append(Move((r,c),(r+1,c+1),self.board))
                    else:
                        moves.append(Move((r,c),(r+1,c+1),self.board))

                if self.board[r+1][c][0]=='-':
                    if piecePinned:
                        if pinnedDirection in [(-1,0),(1,0)]:
                            moves.append(Move((r,c),(r+1,c),self.board))
                    else:
                        moves.append(Move((r,c),(r+1,c),self.board))

                    if r==1 and self.board[3][c][0]=='-':
                        if piecePinned:
                            if pinnedDirection in [(-1,0),(1,0)]:
                                moves.append(Move((r,c),(3,c),self.board))
                        else:
                            moves.append(Move((r,c),(3,c),self.board))

                if self.enPassant[0] and r==4 and c in (self.enPassant[1]-1,self.enPassant[1]+1):
                    if piecePinned:
                        if c==self.enPassant[1]-1 and pinnedDirection==(1,-1):
                            moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                        elif c==self.enPassant[1]+1 and pinnedDirection==(1,1):
                            moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                    else:
                        moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                            

    def getRookMoves(self,r,c,moves):

        if self.checkNum==2:
            doubleCheck=True
        else:
            doubleCheck=False
            
        if not(doubleCheck):
            piecePinned=False
            directionFlag=True
            pinnedDirection=()
            for i in range(len(self.pins)-1,-1,-1):
                if r==self.pins[i][0] and c==self.pins[i][1]:
                    piecePinned=True
                    pinnedDirection=self.pins[i][2]
                    if self.board[r][c][1]!='Q':
                        self.pins.remove(self.pins[i])
                    break

            if pinnedDirection in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                directionFlag=False
            
            if directionFlag:
                if piecePinned:
                    if pinnedDirection in [(1,0),(-1,0)]:

                        for x in range(r-1,-1,-1):
                            if self.board[x][c][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,c),self.board))
                                break
                            elif self.board[x][c][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,c),self.board))

                        for x in range(r+1,8):
                            if self.board[x][c][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,c),self.board))
                                break
                            elif self.board[x][c][0]==self.frndColorColor:
                                break
                            moves.append(Move((r,c),(x,c),self.board))

                    else:

                        for x in range(c-1,-1,-1):
                            if self.board[r][x][0]==self.enemyColor:
                                moves.append(Move((r,c),(r,x),self.board))
                                break
                            elif self.board[r][x][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(r,x),self.board))

                        for x in range(c+1,8):
                            if self.board[r][x][0]==self.enemyColor:
                                moves.append(Move((r,c),(r,x),self.board))
                                break
                            elif self.board[r][x][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(r,x),self.board))

                else:

                    for x in range(r-1,-1,-1):
                            if self.board[x][c][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,c),self.board))
                                break
                            elif self.board[x][c][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,c),self.board))

                    for x in range(r+1,8):
                        if self.board[x][c][0]==self.enemyColor:
                            moves.append(Move((r,c),(x,c),self.board))
                            break
                        elif self.board[x][c][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(x,c),self.board))

                    for x in range(c-1,-1,-1):
                            if self.board[r][x][0]==self.enemyColor:
                                moves.append(Move((r,c),(r,x),self.board))
                                break
                            elif self.board[r][x][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(r,x),self.board))

                    for x in range(c+1,8):
                        if self.board[r][x][0]==self.enemyColor:
                            moves.append(Move((r,c),(r,x),self.board))
                            break
                        elif self.board[r][x][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(r,x),self.board))


    def getNightMoves(self,r,c,moves):       

        knightDirections=[(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        if self.checkNum==2:
            doubleCheck=True
        else:
            doubleCheck=False
            
        if not(doubleCheck):
            piecePinned=False
            for i in range(len(self.pins)-1,-1,-1):
                if r==self.pins[i][0] and c==self.pins[i][1]:
                    piecePinned=True
                    break

            if not(piecePinned):
                for d in knightDirections:
                    x,y=r+d[0],c+d[1]
                    if 0<=x<=7 and 0<=y<=7 and self.board[x][y][0]!=self.frndColor:
                        moves.append(Move((r,c),(x,y),self.board))


    def getBishopMoves(self,r,c,moves):

        if self.checkNum==2:
            doubleCheck=True
        else:
            doubleCheck=False
            
        if not(doubleCheck):
            piecePinned=False
            directionFlag=True
            pinnedDirection=()
            for i in range(len(self.pins)-1,-1,-1):
                if r==self.pins[i][0] and c==self.pins[i][1]:
                    piecePinned=True
                    pinnedDirection=self.pins[i][2]
                    self.pins.remove(self.pins[i])
                    break

            if pinnedDirection in [(1,0),(-1,0),(0,1),(0,-1)]:
                directionFlag=False
            
            if directionFlag:
                if piecePinned:
                    if pinnedDirection in [(-1,-1),(1,1)]:

                        x,y=r-1,c-1
                        while x!=-1 and y!=-1:
                            if self.board[x][y][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,y),self.board))
                                break
                            elif self.board[x][y][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,y),self.board))
                            x-=1
                            y-=1

                        x,y=r+1,c+1
                        while x!=8 and y!=8:
                            if self.board[x][y][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,y),self.board))
                                break
                            elif self.board[x][y][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,y),self.board))
                            x+=1
                            y+=1

                    else:

                        x,y=r-1,c+1
                        while x!=-1 and y!=8:
                            if self.board[x][y][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,y),self.board))
                                break
                            elif self.board[x][y][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,y),self.board))
                            x-=1
                            y+=1
                        
                        x,y=r+1,c-1
                        while x!=8 and y!=-1:
                            if self.board[x][y][0]==self.enemyColor:
                                moves.append(Move((r,c),(x,y),self.board))
                                break
                            elif self.board[x][y][0]==self.frndColor:
                                break
                            moves.append(Move((r,c),(x,y),self.board))
                            x+=1
                            y-=1

                else:

                    x,y=r-1,c-1
                    while x!=-1 and y!=-1:
                        if self.board[x][y][0]==self.enemyColor:
                            moves.append(Move((r,c),(x,y),self.board))
                            break
                        elif self.board[x][y][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(x,y),self.board))
                        x-=1
                        y-=1

                    x,y=r+1,c+1
                    while x!=8 and y!=8:
                        if self.board[x][y][0]==self.enemyColor:
                            moves.append(Move((r,c),(x,y),self.board))
                            break
                        elif self.board[x][y][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(x,y),self.board))
                        x+=1
                        y+=1

                    x,y=r-1,c+1
                    while x!=-1 and y!=8:
                        if self.board[x][y][0]==self.enemyColor:
                            moves.append(Move((r,c),(x,y),self.board))
                            break
                        elif self.board[x][y][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(x,y),self.board))
                        x-=1
                        y+=1
                    
                    x,y=r+1,c-1
                    while x!=8 and y!=-1:
                        if self.board[x][y][0]==self.enemyColor:
                            moves.append(Move((r,c),(x,y),self.board))
                            break
                        elif self.board[x][y][0]==self.frndColor:
                            break
                        moves.append(Move((r,c),(x,y),self.board))
                        x+=1
                        y-=1
                    

    def getQueenMoves(self,r,c,moves):

        if self.checkNum==2:
            doubleCheck=True
        else:
            doubleCheck=False
            
        if not(doubleCheck):

            self.getRookMoves(r,c,moves)

            self.getBishopMoves(r,c,moves)


    def getKingMoves(self,r,c,moves):

        kingDirections=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
        for d in kingDirections:
            x,y=r+d[0],c+d[1]
            if 0<=x<=7 and 0<=y<=7 and self.board[x][y][0]!=self.frndColor and not(self.willBeCheck(x,y)):
                moves.append(Move((r,c),(x,y),self.board))

        if self.castlingRights[self.frndColor+'K'] and self.checkNum==0:
            if self.whiteToMove:
                if self.castlingRights['wR0'] and (self.board[7][5],self.board[7][6],self.willBeCheck(7,5),self.willBeCheck(7,6))==('--','--',False,False):
                    moves.append(Move((7,4),(7,6),self.board))
                if self.castlingRights['wR7'] and (self.board[7][3],self.board[7][2],self.board[7][1],self.willBeCheck(7,3),self.willBeCheck(7,2))==('--','--','--',False,False):
                    moves.append(Move((7,4),(7,2),self.board))
            else:
                if self.castlingRights['bR0'] and (self.board[0][5],self.board[0][6],self.willBeCheck(0,5),self.willBeCheck(0,6))==('--','--',False,False):
                    moves.append(Move((0,4),(0,6),self.board))
                if self.castlingRights['bR7'] and (self.board[0][3],self.board[0][2],self.board[0][1],self.willBeCheck(0,3),self.willBeCheck(0,2))==('--','--','--',False,False):
                    moves.append(Move((0,4),(0,2),self.board))




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
