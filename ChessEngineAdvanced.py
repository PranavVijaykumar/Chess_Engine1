import random

random.seed(42)

PIECES = ['wK','wQ','wR','wB','wN','wp',
          'bK','bQ','bR','bB','bN','bp']

ROOK_DIR=[(1,0),(0,1),(-1,0),(0,-1)]
BISHOP_DIR=[(1,1),(1,-1),(-1,1),(-1,-1)]
KNIGHT_DIR=[(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]

ZOBRIST = {}

for piece in PIECES:
    for r in range(8):
        for c in range(8):
            ZOBRIST[(piece, r, c)]=random.getrandbits(64)

SIDE_TO_MOVE = random.getrandbits(64)
EN_PASSANT = random.getrandbits(64)
CASTLING_RIGHTS={'wK':random.getrandbits(64),'bK':random.getrandbits(64),'wR0':random.getrandbits(64),'wR7':random.getrandbits(64),'bR0':random.getrandbits(64),'bR7':random.getrandbits(64)}


def startingMoves(board,turn):
    moveSet=[]
    for c in range(8):
        moveSet.append(Move((6 if turn else 1, c),(5 if turn else 2, c),board))
        moveSet.append(Move((6 if turn else 1, c),(4 if turn else 3, c),board))
    
    moveSet.append(Move((7 if turn else 0, 1),(5 if turn else 2, 0),board))
    moveSet.append(Move((7 if turn else 0, 1),(5 if turn else 2, 2),board))
    moveSet.append(Move((7 if turn else 0, 6),(5 if turn else 2, 5),board))
    moveSet.append(Move((7 if turn else 0, 6),(5 if turn else 2, 7),board))

    return moveSet



def zobristHash(gs):
    h = 0

    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != '--':
                h ^= ZOBRIST[(piece, r, c)]
    
    for piece in CASTLING_RIGHTS:
        h^= CASTLING_RIGHTS[piece]

    h ^= SIDE_TO_MOVE

    return h


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
        self.whiteMoveSet=startingMoves(self.board,True)
        self.blackMoveSet=startingMoves(self.board,False)
        self.whiteKingPos=(7,4)
        self.blackKingPos=(0,4)
        self.checkmate=False
        self.stalemate=False
        self.draw=False
        self.fiftyMoveCounter=0
        self.castleStatus={'wK':False,'bK':False}
        self.castlingRights={'wK':True,'bK':True,'wR0':True,'wR7':True,'bR0':True,'bR7':True}
        self.enPassant=(False,-1)
        self.zobrist=zobristHash(self)
        self.hashTable={self.zobrist:1}
        self.pinnedPieces=[]
        self.checks=[]
         


    def makeMove(self,move):

        self.board[move.startRow][move.startCol]="--"
        self.board[move.endRow][move.endCol]=move.pieceMoved
        move.prevFiftyMoveCounter=self.fiftyMoveCounter

        self.zobrist ^= SIDE_TO_MOVE
        self.zobrist ^= ZOBRIST[(move.pieceMoved, move.startRow, move.startCol)]

        if move.pieceCaptured != '--':
            self.zobrist ^= ZOBRIST[(move.pieceCaptured, move.endRow, move.endCol)]

        self.zobrist ^= ZOBRIST[(move.pieceMoved, move.endRow, move.endCol)]

        if self.enPassant[0]:  #Terminate EnPassant
            if move.moveType[0]=='EnPassant':
                self.zobrist ^= ZOBRIST[(self.board[move.startRow][move.endCol], move.startRow, move.endCol)]
                self.board[move.startRow][move.endCol]='--'
            
            self.zobrist^=EN_PASSANT
            self.enPassant=(False,-1)
        
        if move.pieceMoved=='wK':
            self.whiteKingPos=(move.endRow,move.endCol)

            if move.moveType[0]=='Castling':

                if move.endCol==6:                  #King side castle
                    self.zobrist^=CASTLING_RIGHTS['wR7']
                    self.castlingRights['wR7']=False
                    self.board[7][7]='--'
                    self.board[7][5]='wR'
                    self.zobrist ^= ZOBRIST[('wR', 7, 7)]
                    self.zobrist ^= ZOBRIST[('wR', 7, 5)]

                elif move.endCol==2:                #Queen side castle
                    self.zobrist^=CASTLING_RIGHTS['wR0']
                    self.castlingRights['wR0']=False
                    self.board[7][0]='--'
                    self.board[7][3]='wR'
                    self.zobrist ^= ZOBRIST[('wR', 7, 0)]
                    self.zobrist ^= ZOBRIST[('wR', 7, 3)]

                self.zobrist^=CASTLING_RIGHTS['wK']
                self.castlingRights['wK']=False
                self.castleStatus['wK']=True
            
            elif self.castlingRights['wK']:         #Restrict King Castling Rights
                self.zobrist^=CASTLING_RIGHTS['wK']
                self.castlingRights['wK']=False
                move.moveType=['KingRightLost']

        elif move.pieceMoved=='bK':
            self.blackKingPos=(move.endRow,move.endCol)

            if move.moveType[0]=='Castling':

                if move.endCol==6:
                    self.zobrist^=CASTLING_RIGHTS['bR7']
                    self.castlingRights['bR7']=False
                    self.board[0][7]='--'
                    self.board[0][5]='bR'
                    self.zobrist ^= ZOBRIST[('bR', 0, 7)]
                    self.zobrist ^= ZOBRIST[('bR', 0, 5)]

                elif move.endCol==2:
                    self.zobrist^=CASTLING_RIGHTS['bR0']
                    self.castlingRights['bR0']=False
                    self.board[0][0]='--'
                    self.board[0][3]='bR'
                    self.zobrist ^= ZOBRIST[('bR', 0, 0)]
                    self.zobrist ^= ZOBRIST[('bR', 0, 3)]

                self.zobrist^=CASTLING_RIGHTS['bK']
                self.castlingRights['bK']=False
                self.castleStatus['bK']=True
            
            elif self.castlingRights['bK']:
                self.zobrist^=CASTLING_RIGHTS['bK']
                self.castlingRights['bK']=False
                move.moveType=['KingRightLost']
        
        elif move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:   #Initiate EnPassant
            self.enPassant=(True,move.endCol)
            self.zobrist^=EN_PASSANT
            move.moveType=['EnPassantInitiated']
        
        elif move.pieceMoved=='wp' and move.endRow==0:     #Promotion
            self.board[0][move.endCol]='wQ'
            self.zobrist ^= ZOBRIST[('wp', 0, move.endCol)]
            self.zobrist ^= ZOBRIST[('wQ', 0, move.endCol)]
            move.moveType=['Promotion']
        
        elif move.pieceMoved=='bp' and move.endRow==7:
            self.board[7][move.endCol]='bQ'
            self.zobrist ^= ZOBRIST[('bp', 7, move.endCol)]
            self.zobrist ^= ZOBRIST[('bQ', 7, move.endCol)]
            move.moveType=['Promotion']
        
        elif move.pieceMoved[1]=='R' and move.startCol in (0,7) and self.castlingRights[move.pieceMoved+str(move.startCol)]:     #Restrict rook castling rights
            self.zobrist^=CASTLING_RIGHTS[move.pieceMoved+str(move.startCol)]
            self.castlingRights[move.pieceMoved+str(move.startCol)]=False
            move.moveType=['RookRightLost']

        if move.pieceCaptured[1]=='R' and move.endCol in (0,7) and self.castlingRights[move.pieceCaptured+str(move.endCol)]:
            self.zobrist^=CASTLING_RIGHTS[move.pieceCaptured+str(move.endCol)]
            self.castlingRights[move.pieceCaptured+str(move.endCol)]=False
            move.moveType.append('RookRightCaptured')
        

        if move.pieceMoved[1]=='p' or move.pieceCaptured!='--':
            self.fiftyMoveCounter=0
        
        else:
            self.fiftyMoveCounter+=1
            if self.fiftyMoveCounter==50:
                self.draw=True
        

        self.updateMoveSet(move)

        self.moveLog.append(move)
        
        self.whiteToMove=not(self.whiteToMove)

        if self.zobrist in self.hashTable:
            self.hashTable[self.zobrist]+=1
            if self.hashTable[self.zobrist]==3:
                self.draw=True

        else:
            if self.whiteToMove:
                self.whiteMoveSet
            self.hashTable[self.zobrist]=1



    def updateMoveSet(self,move):

        updatedWhiteMoveSet=[]
        updatedBlackMoveSet=[]
        deletedMoves={}
        deletedBlackMoves=[]
        deletedWhiteMoves=[]
        startRow,startCol,endRow,endCol=move.startRow,move.startCol,move.endRow,move.endCol
        frndColor=move.pieceMoved[0]

        dr,dc=endRow-startRow,endCol-startCol
        moveDir= ((dr>0)-(dr<0),(dc>0)-(dc<0)) if move.pieceMoved[1]!='N' else (2,1)
        dirFlag=0

        piecePinned=False
        if move.pieceCaptured=='--':
            for piece in self.pinnedPieces:
                if piece[0]==(startRow,startCol):
                    piecePinned=True
                    pinDir=piece[1]
                    break


        for dir in KNIGHT_DIR:

            if self.board[startRow+dir[0]][startCol+dir[1]][1]=='N':

                addMove=Move((startRow+dir[0],startCol+dir[1]),(startRow,startCol),self.board)

                if frndColor=='w':
                        updatedWhiteMoveSet.append(addMove)
                else:
                    updatedBlackMoveSet.append(addMove)

                if self.board[startRow+dir[0]][startCol+dir[1]][0]!=frndColor:
                    deletedMoves[addMove.getMoveID()]=1
        

        for directions in (ROOK_DIR,BISHOP_DIR):

            for dir in directions:
                
                if dir==moveDir:
                    r,c=endRow+dir[0],endCol+dir[1]
                else:
                    r,c=startRow+dir[0],startCol+dir[1]

                while -1<r<8 and -1<c<8:

                    if self.board[r][c]!='--':

                        if (not(dirFlag) and self.board[r][c][1] in ('R','Q')) or (dirFlag and self.board[r][c][1] in ('B','Q')):

                            if dir==moveDir:
                                x,y=startRow+moveDir[0],startCol+moveDir[1]

                                while x!=endRow-moveDir[0] and y!=endCol-moveDir[1]:

                                    deletedMoves[r*1000+c*100+x*10+y]=1
                                    x+=moveDir[0]
                                    y+=moveDir[1]

                                if frndColor==self.board[r][c][0]:
                                    deletedMoves[r*1000+c*100+endRow*10+endCol]=1

                                else:
                                    deletedMoves[r*1000+c*100+startRow*10+startCol]=1
                                    deletedMoves[r*1000+c*100+endRow*10+endCol]=1
                                    addMove=Move((r,c),(endRow,endCol),self.board)

                                    if self.board[r][c][0]=='w':
                                        updatedWhiteMoveSet.append(addMove)
                                    else:
                                        updatedBlackMoveSet.append(addMove)
                            
                            else:

                                if frndColor!=self.board[r][c][0]:
                                    deletedMoves[r*1000+c*100+startRow*10+startCol]=1

                                x,y=startRow,startCol

                                if self.board[r][c][0]=='w':

                                    while -1<x<8 and -1<y<8:

                                        if self.board[x][y]=='--':
                                            updatedWhiteMoveSet.append(Move((r,c),(x,y),self.board))

                                        elif self.board[x][y][0]=='b':
                                            updatedWhiteMoveSet.append(Move((r,c),(x,y),self.board))

                                            xp=x-dir[0]
                                            yp=y-dir[1]

                                            while -1<xp<8 and -1<yp<8:

                                                if self.board[x][y]=='bK':
                                                    self.pinnedPieces.append(((x,y),(r,c),dir))
                                                    break

                                                elif self.board[x][y]!='--':
                                                    break

                                                xp-=dir[0]
                                                yp-=dir[1]
                                        
                                        else:
                                            break

                                        x-=dir[0]
                                        y-=dir[1]
            
                                else:

                                    while -1<x<8 and -1<y<8:

                                        if self.board[x][y]=='--':
                                            updatedBlackMoveSet.append(Move((r,c),(x,y),self.board))

                                        elif self.board[x][y][0]=='b':
                                            updatedBlackMoveSet.append(Move((r,c),(x,y),self.board))

                                            xp=x-dir[0]
                                            yp=y-dir[1]

                                            while -1<xp<8 and -1<yp<8:

                                                if self.board[x][y]=='wK':
                                                    self.pinnedPieces.append(((x,y),(r,c),dir))
                                                    break

                                                elif self.board[x][y]!='--':
                                                    break

                                                xp-=dir[0]
                                                yp-=dir[1]
                                        
                                        else:
                                            break

                                        x-=dir[0]
                                        y-=dir[1]
                                        
                        break
                        
                    r+=dir[0]
                    c+=dir[1]
            
            dirFlag+=1
        

        for dir in KNIGHT_DIR:

            if self.board[endRow+dir[0]][endCol+dir[1]][1]=='N':

                addMove=Move((startRow+dir[0],startCol+dir[1]),(startRow,startCol),self.board)
                if frndColor=='w':
                        updatedWhiteMoveSet.append(addMove)
                else:
                    updatedBlackMoveSet.append(addMove)

                if self.board[startRow+dir[0]][startCol+dir[1]][0]!=frndColor:
                    deletedMoves[addMove.getMoveID()]=1
        

        


                        



                






    def undoMove(self):

        move=self.moveLog.pop()
        self.board[move.endRow][move.endCol],self.board[move.startRow][move.startCol]=move.pieceCaptured,move.pieceMoved
        self.fiftyMoveCounter=move.prevFiftyMoveCounter
        self.hashTable[self.zobrist]-=1

        self.zobrist ^= SIDE_TO_MOVE
        self.zobrist ^= ZOBRIST[(move.pieceMoved, move.endRow, move.endCol)]

        if move.pieceCaptured != '--':
            self.zobrist ^= ZOBRIST[(move.pieceCaptured, move.endRow, move.endCol)]

        self.zobrist ^= ZOBRIST[(move.pieceMoved, move.startRow, move.startCol)]


        if move.moveType[0]=='Promotion':
            self.zobrist ^= ZOBRIST[(move.pieceMoved[0]+'Q',move.endRow,move.endCol)]
            self.zobrist ^= ZOBRIST[(move.pieceMoved, move.endRow, move.endCol)]

        elif move.moveType[0]=='EnPassant':         #Reappear EnPassanted Piece

            if move.startRow==3:
                self.board[3][move.endCol]='bp'
                self.zobrist ^= ZOBRIST[('bp', 3, move.endCol)]
            else:
                self.board[4][move.endCol]='wp'
                self.zobrist ^= ZOBRIST[('wp', 4, move.endCol)]
        

        elif move.moveType[0]=='EnPassantInitiated':

            self.enPassant=(False,-1)
            self.zobrist^=EN_PASSANT
        

        elif move.pieceMoved=='wK':

            self.whiteKingPos=(move.startRow,move.startCol)

            if move.moveType[0]=='Castling':      #Reappear Castled Rook

                if move.endCol==6:
                    self.zobrist^=CASTLING_RIGHTS['wR7']
                    self.castlingRights['wR7']=True
                    self.board[7][7]='wR'
                    self.board[7][5]='--'
                    self.zobrist ^= ZOBRIST[('wR', 7, 7)]
                    self.zobrist ^= ZOBRIST[('wR', 7, 5)]
                else:
                    self.zobrist^=CASTLING_RIGHTS['wR0']
                    self.castlingRights['wR0']=True
                    self.board[7][0]='wR'
                    self.board[7][3]='--'
                    self.zobrist ^= ZOBRIST[('wR', 7, 0)]
                    self.zobrist ^= ZOBRIST[('wR', 7, 3)]
                
                self.zobrist^=CASTLING_RIGHTS['wK']
                self.castlingRights['wK']=True
                self.castleStatus['wK']=False
            
            elif move.moveType[0]=='KingRightLost':    #Give King Castling Rights
                self.zobrist^=CASTLING_RIGHTS['wK']
                self.castlingRights['wK']=True

        
        elif move.pieceMoved=='bK':

            self.blackKingPos=(move.startRow,move.startCol)

            if move.moveType[0]=='Castling': 

                if move.endCol==6:
                        self.zobrist^=CASTLING_RIGHTS['bR7']
                        self.castlingRights['bR7']=True
                        self.board[0][7]='bR'
                        self.board[0][5]='--'
                        self.zobrist ^= ZOBRIST[('bR', 0, 7)]
                        self.zobrist ^= ZOBRIST[('bR', 0, 5)]
                else:
                    self.zobrist^=CASTLING_RIGHTS['bR0']
                    self.castlingRights['bR0']=True
                    self.board[0][0]='bR'
                    self.board[0][3]='--'
                    self.zobrist ^= ZOBRIST[('bR', 0, 0)]
                    self.zobrist ^= ZOBRIST[('bR', 0, 3)]

                self.zobrist^=CASTLING_RIGHTS['bK']
                self.castlingRights['bK']=True
                self.castleStatus['bK']=False
            
            elif move.moveType[0]=='KingRightLost':
                self.zobrist^=CASTLING_RIGHTS['bK']
                self.castlingRights['bK']=True
        
        elif move.moveType[0]=='RookRightLost':
            self.castlingRights[move.pieceMoved+str(move.startCol)]=True
            self.zobrist^=CASTLING_RIGHTS[move.pieceMoved+str(move.startCol)]
        
        if 'RookRightCaptured' in move.moveType:
            self.castlingRights[move.pieceCaptured+str(move.endCol)]=True
            self.zobrist^=CASTLING_RIGHTS[move.pieceCaptured+str(move.endCol)]
        
        if self.moveLog and self.moveLog[-1].moveType[0]=='EnPassantInitiated':
            self.enPassant=(True,self.moveLog[-1].endCol)
            self.zobrist^=EN_PASSANT

        if self.checkmate:
            self.checkmate=False

        elif self.draw:

            if self.stalemate:
                self.stalemate=False

            self.draw=False

        self.whiteToMove=not(self.whiteToMove)


    def getValidMoves(self):

        if self.whiteToMove:
            validMoves=self.whiteMoveSet
            self.kingRow=self.whiteKingPos[0]
            self.kingCol=self.whiteKingPos[1]
            self.frndColor='w'
            self.enemyColor='b'
        else:
            self.kingRow=self.blackKingPos[0]
            self.kingCol=self.blackKingPos[1]
            self.frndColor='b'
            self.enemyColor='w'

        self.pins,self.checks=self.pinsAndChecks()
        moves=[]

        if len(self.checks)==2:   #Double check
            self.getKingMoves(self.kingRow,self.kingCol,moves)

        else:

            self.generateMoves(moves)

            if self.checks:
                coverSqrs=set()

                checkRow=self.checks[0][0]
                checkCol=self.checks[0][1]
                checkDirection=self.checks[0][2]
                r=self.kingRow+checkDirection[0]
                c=self.kingCol+checkDirection[1]

                if self.board[checkRow][checkCol][1]=='N':
                    coverSqrs.add((checkRow,checkCol))

                else:
                    while (r,c)!=(checkRow+checkDirection[0],checkCol+checkDirection[1]):
                        coverSqrs.add((r,c))
                        r+=checkDirection[0]
                        c+=checkDirection[1]

                temp_moves=[]
                for i in range(len(moves)):

                    if (moves[i].endRow,moves[i].endCol) in coverSqrs:
                        temp_moves.append(moves[i])

                    elif moves[i].moveType[0]=='EnPassant' and (moves[i].startRow,moves[i].endCol)==(self.checks[0][0],self.checks[0][1]):
                        temp_moves.append(moves[i])


                moves=temp_moves

            self.getKingMoves(self.kingRow,self.kingCol,moves)
        
        if len(moves)==0:
            if len(self.checks)==0:
                self.draw=True
                self.stalemate=True
            else:
                self.checkmate=True

        return moves
    


    def pinsAndChecks(self):

        pins=[] #[(startRow,startCol,(rowDirection,colDirection)),...]
        checks=[] #[(startRow,startCol,Direction),...]
        directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for d in directions:
            if len(checks)==2:
                break
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

        if len(checks)!=2:
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

                if self.board[x][y][0]==self.frndColor and self.board[x][y][1]!='K':
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


    
    def generateMoves(self,moves):

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c][0]==self.frndColor:
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


    def getPawnMoves(self,r,c,moves):

        for i in range(len(self.pins)):
            if r==self.pins[i][0] and c==self.pins[i][1]:
                piecePinned=True
                pinnedDirection=self.pins[i][2]
                del self.pins[i]
                break
        else:
            piecePinned=False

        
        if self.frndColor=='w': 

            if piecePinned and (pinnedDirection in [(1,1),(1,-1),(0,-1),(0,1)] or self.checks):
                return
            
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
                    if (c==self.enPassant[1]-1 and pinnedDirection in [(-1,-1),(1,1)]) or (c==self.enPassant[1]+1 and pinnedDirection in [(-1,1),(1,-1)]):
                        moves.append(Move((3,c),(2,self.enPassant[1]),self.board))
                        moves[-1].moveType=['EnPassant']

                else:

                    if self.kingRow==3:
                        
                        if self.kingCol>max(c,self.enPassant[1]):
                            step=-1

                            if c<self.enPassant[1]:
                                stop=self.enPassant[1]
                                start=c-1

                            else:
                                stop=c
                                start=self.enPassant[1]-1

                        else:
                            step=1

                            if c<self.enPassant[1]:
                                stop=c
                                start=self.enPassant[1]+1

                            else:
                                stop=self.enPassant[1]
                                start=c+1

                        pieceBlock=False
                        piecePinning=False
                        for y in range(self.kingCol,stop,step):
                            if self.board[3][y]!='--':
                                pieceBlock=True
                                break
                        
                        for y in range(start,-1 if step==-1 else 8,step):
                            if self.board[3][y]!='--':
                                if self.board[3][y] in ('bR','bQ'):
                                    piecePinning=True
                                break

                        if pieceBlock or not(piecePinning):
                            moves.append(Move((3,c),(2,self.enPassant[1]),self.board))
                            moves[-1].moveType=['EnPassant']
                        
                    
                    else:
                        moves.append(Move((3,c),(2,self.enPassant[1]),self.board))
                        moves[-1].moveType=['EnPassant']


        else:

            if piecePinned and (pinnedDirection in [(-1,1),(-1,-1),(0,-1),(0,1)] or self.checks):
                return

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
                            moves.append(Move((1,c),(3,c),self.board))
                    else:
                        moves.append(Move((1,c),(3,c),self.board))


            if self.enPassant[0] and r==4 and c in (self.enPassant[1]-1,self.enPassant[1]+1):

                if piecePinned:
                    if (c==self.enPassant[1]-1 and pinnedDirection in [(1,-1),(-1,1)]) or (c==self.enPassant[1]+1 and pinnedDirection in [(1,1),(-1,-1)]):
                        moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                        moves[-1].moveType=['EnPassant']

                else:

                    if self.kingRow==4:
                        
                        if self.kingCol>max(c,self.enPassant[1]):
                            step=-1

                            if c<self.enPassant[1]:
                                stop=self.enPassant[1]
                                start=c-1

                            else:
                                stop=c
                                start=self.enPassant[1]-1

                        else:
                            step=1

                            if c<self.enPassant[1]:
                                stop=c
                                start=self.enPassant[1]+1

                            else:
                                stop=self.enPassant[1]
                                start=c+1

                        pieceBlock=False
                        piecePinning=False
                        for y in range(self.kingCol,stop,step):
                            if self.board[4][y]!='--':
                                pieceBlock=True
                                break
                        
                        for y in range(start,-1 if step==-1 else 8,step):
                            if self.board[4][y]!='--':
                                if self.board[4][y] in ('wR','wQ'):
                                    piecePinning=True
                                break

                        if pieceBlock or not(piecePinning):
                            moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                            moves[-1].moveType=['EnPassant']

                    else:
                        moves.append(Move((4,c),(5,self.enPassant[1]),self.board))
                        moves[-1].moveType=['EnPassant']
                            

    def getRookMoves(self,r,c,moves):

        for i in range(len(self.pins)):
            if r==self.pins[i][0] and c==self.pins[i][1]:
                piecePinned=True
                pinnedDirection=self.pins[i][2]
                if self.board[r][c][1]!='Q':
                    del self.pins[i]
                break
        else:
            piecePinned=False
        

        if piecePinned:

            if self.checks or pinnedDirection in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                return
            
            dr,dc=pinnedDirection[0],pinnedDirection[1]
            x,y=r-dr,c-dc
            while (x,y)!=(self.kingRow,self.kingCol):
                moves.append(Move((r,c),(x,y),self.board))
                x,y=x-dr,y-dc
            
            x,y=r+dr,c+dc
            while self.board[x][y]=='--':
                moves.append(Move((r,c),(x,y),self.board))
                x,y=x+dr,y+dc
            
            moves.append(Move((r,c),(x,y),self.board))


        else:

            rookDirections=[(1,0),(0,1),(-1,0),(0,-1)]

            for dir in rookDirections:
                x,y=r+dir[0],c+dir[1]

                while -1<x<8 and -1<y<8:

                    if self.board[x][y][0]==self.enemyColor:
                        moves.append(Move((r,c),(x,y),self.board))
                        break
                    elif self.board[x][y][0]==self.frndColor:
                        break
                    moves.append(Move((r,c),(x,y),self.board))
                    x,y=x+dir[0],y+dir[1]


    def getNightMoves(self,r,c,moves):
            
        for i in range(len(self.pins)):
            if r==self.pins[i][0] and c==self.pins[i][1]:
                del self.pins[i]
                return
            
        knightDirections=[(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]

        for d in knightDirections:
            x,y=r+d[0],c+d[1]
            if 0<=x<=7 and 0<=y<=7 and self.board[x][y][0]!=self.frndColor:
                moves.append(Move((r,c),(x,y),self.board))


    def getBishopMoves(self,r,c,moves):
        
        for i in range(len(self.pins)):
            if r==self.pins[i][0] and c==self.pins[i][1]:
                piecePinned=True
                pinnedDirection=self.pins[i][2]
                del self.pins[i]
                break
        else:
            piecePinned=False
        
        if piecePinned:

            if self.checks or pinnedDirection in [(1,0),(-1,0),(0,1),(0,-1)]:
                return
            
            dr,dc=pinnedDirection[0],pinnedDirection[1]
            x,y=r-dr,c-dc
            while (x,y)!=(self.kingRow,self.kingCol):
                moves.append(Move((r,c),(x,y),self.board))
                x,y=x-dr,y-dc
            
            x,y=r+dr,c+dc
            while self.board[x][y]=='--':
                moves.append(Move((r,c),(x,y),self.board))
                x,y=x+dr,y+dc
            
            moves.append(Move((r,c),(x,y),self.board))

        else:

            bishopDirections=[(1,1),(1,-1),(-1,1),(-1,-1)]

            for dir in bishopDirections:
                x,y=r+dir[0],c+dir[1]
                
                while -1<x<8 and -1<y<8:

                    if self.board[x][y][0]==self.enemyColor:
                        moves.append(Move((r,c),(x,y),self.board))
                        break
                    elif self.board[x][y][0]==self.frndColor:
                        break
                    moves.append(Move((r,c),(x,y),self.board))
                    x,y=x+dir[0],y+dir[1]


    def getQueenMoves(self,r,c,moves):

        self.getRookMoves(r,c,moves)

        self.getBishopMoves(r,c,moves)


    def getKingMoves(self,r,c,moves):

        kingDirections=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
        for d in kingDirections:
            x,y=r+d[0],c+d[1]
            if 0<=x<=7 and 0<=y<=7 and self.board[x][y][0]!=self.frndColor and not(self.willBeCheck(x,y)):
                moves.append(Move((r,c),(x,y),self.board))

        if self.castlingRights[self.frndColor+'K'] and len(self.checks)==0:

            if self.whiteToMove:
                if self.castlingRights['wR7'] and (self.board[7][5],self.board[7][6],self.willBeCheck(7,5),self.willBeCheck(7,6))==('--','--',False,False):
                    moves.append(Move((7,4),(7,6),self.board))
                    moves[-1].moveType=['Castling']

                if self.castlingRights['wR0'] and (self.board[7][3],self.board[7][2],self.board[7][1],self.willBeCheck(7,3),self.willBeCheck(7,2))==('--','--','--',False,False):
                    moves.append(Move((7,4),(7,2),self.board))
                    moves[-1].moveType=['Castling']
            else:
                if self.castlingRights['bR7'] and (self.board[0][5],self.board[0][6],self.willBeCheck(0,5),self.willBeCheck(0,6))==('--','--',False,False):
                    moves.append(Move((0,4),(0,6),self.board))
                    moves[-1].moveType=['Castling']

                if self.castlingRights['bR0'] and (self.board[0][3],self.board[0][2],self.board[0][1],self.willBeCheck(0,3),self.willBeCheck(0,2))==('--','--','--',False,False):
                    moves.append(Move((0,4),(0,2),self.board))
                    moves[-1].moveType=['Castling']



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
        self.moveType=['Normal']
        self.prevFiftyMoveCounter=0

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)
    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    def getMoveID(self):
        return (self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol)
