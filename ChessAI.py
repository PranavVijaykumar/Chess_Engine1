import random,math,ChessEngine

CENTERPRESENCE=1
CHECKMATE=10000
DRAW=0
DEPTH=5
QDEPTH=1
MOBILITYFACTOR=0.5
ATTACKFACTOR=1
PROTECTFACTOR=1
ROOKMOBILITY=False
QUEENMOBILITY=False
TT={}

pieceScores = {'K':0, 'Q':90, 'R':50, 'B':30, 'N':30, 'p':10}

knightHeatMap=[[0, 1, 1, 1, 1, 1, 1, 0],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 4, 6, 6, 4, 2, 1],
               [1, 2, 4, 6, 6, 4, 2, 1],
               [0, 2, 3, 3, 3, 3, 2, 0],
               [0, 1, 2, 2, 2, 2, 1, 0],
               [0, 1, 1, 1, 1, 1, 1, 0]]

pawnHeatMap=[[-1,-1,-1,-1,-1,-1,-1,-1],
             [7, 8, 9, 9, 9, 9, 8, 7],
             [4, 4, 4, 5, 5, 4, 4, 4],
             [2, 3, 4, 4, 4, 4, 3, 2],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 1, 1, 2, 2, 1, 1, 1],
             [1, 1, 1, 0, 0, 1, 1, 1],
             [-1,-1,-1,-1,-1,-1,-1,-1]]


def rawBoardScore(gs):
    rawScore=0
    for r in range(8):
        for c in range(8):
            if gs.board[r][c]!='--':
                rawScore+=pieceScores[gs.board[r][c][1]]
    
    return rawScore


def kingSafetyScore(gs,r,c):
    frndColor=gs.board[r][c][0]
    score=0
    if gs.castleStatus[frndColor+'K']:
        score+=6
    elif not(gs.castlingRights[frndColor+'K']):
        score-=6
    
    kingDirections=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
    checkCount=0.0001
    frndCount=0
    for d in kingDirections:
        x,y=r+d[0],c+d[1]
        if -1<x<8 and -1<y<8:
            if gs.board[x][y][0]==frndColor:
                frndCount+=1
            elif gs.willBeCheck(x,y):
                checkCount+=1

    score-= 2 if frndCount<=1 else 0
    score-= 5 if checkCount>=4 else 0
    
    return score


def mobilityScore(gs,r,c):
    moveCount=0
    piecesProtected=0
    piecesAttacked=0
    frndColor='w' if gs.board[r][c][0]=='w' else 'b'

    if gs.board[r][c][1]=='B' or gs.board[r][c][1]=='Q':

        bishopDirections=[(1,1),(1,-1),(-1,1),(-1,-1)]
        for dir in bishopDirections:
            x,y=r+dir[0],c+dir[1]
            
            while -1<x<8 and -1<y<8:

                if gs.board[x][y]=='--':
                    moveCount+=1

                elif gs.board[x][y][0]==frndColor:
                    piecesProtected+=1
                
                else:
                    piecesAttacked+=1 
                x,y=x+dir[0],y+dir[1]

    
    if gs.board[r][c][1]=='R' or gs.board[r][c][1]=='Q':

        rookDirections=[(1,0),(0,1),(-1,0),(0,-1)]

        for dir in rookDirections:
            x,y=r+dir[0],c+dir[1]

            while -1<x<8 and -1<y<8:

                if gs.board[x][y]=='--':
                    moveCount+=1

                elif gs.board[x][y][0]==frndColor:
                    piecesProtected+=1
                
                else:
                    piecesAttacked+=1 
                x,y=x+dir[0],y+dir[1]

    
    return moveCount*MOBILITYFACTOR/2 + piecesProtected*PROTECTFACTOR + piecesAttacked*ATTACKFACTOR
    

def bestMove(gs):
    global nextMove,moveList,TT,DEPTH,ROOKMOBILITY,MOBILITYFACTOR,PROTECTFACTOR,ATTACKFACTOR,QUEENMOBILITY
    nextMove=None

    # if rawBoardScore(gs)<500 and PROTECTFACTOR==0.8:
    #     PROTECTFACTOR=1.2
    #     ATTACKFACTOR=0.9

    if rawBoardScore(gs)<500 and not(ROOKMOBILITY):
        DEPTH=6
        MOBILITYFACTOR/=2.5
        ROOKMOBILITY=True
        QUEENMOBILITY=True

    elif rawBoardScore(gs)<250 and DEPTH==6:
        MOBILITYFACTOR/=2
        DEPTH=7

    #RecursiveMinMax(gs,DEPTH,validMoves,gs.whiteToMove)
    NegaMaxAlphaBeta(gs,DEPTH,QDEPTH,-CHECKMATE,CHECKMATE, 1 if gs.whiteToMove else -1)

    return nextMove
    

def randomMove(validMoves):
    rand=random.randint(0,len(validMoves)-1)
    return validMoves[rand]

    
def RecursiveMinMax(gs,depth,validMoves,whiteToMove):

    global nextMove
    if depth==0:
        return scoreBoard(gs)
    

    if whiteToMove:
        if depth==DEPTH:
            random.shuffle(validMoves)
        opponentMaxscore=-CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves=gs.getValidMoves()
            score=RecursiveMinMax(gs,depth-1,nextMoves,not(whiteToMove))
            if score>opponentMaxscore:
                opponentMaxscore=score
                if depth==DEPTH:
                    nextMove=move
            gs.undoMove()
        return opponentMaxscore
    

    else:
        if depth==DEPTH:
            random.shuffle(validMoves)
        opponentMinMaxScore=CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves=gs.getValidMoves()
            score=RecursiveMinMax(gs,depth-1,nextMoves,not(whiteToMove))
            if score<opponentMinMaxScore:
                opponentMinMaxScore=score
                if depth==DEPTH:
                    nextMove=move
            gs.undoMove()
        return opponentMinMaxScore



def NegaMaxAlphaBeta(gs,depth,qDepth,alpha,beta,turn): #can add calculate till no captures exist

    global nextMove,TT,moveList

    if depth!=0:

        Z = gs.zobrist

        if Z in TT and TT[Z]["depth"] >= depth:
            return TT[Z]["score"]

    if depth==0:

        if qDepth==0 or not(gs.checks):
            return turn*scoreBoard(gs)
        

    validMoves=gs.getValidMoves()
    random.shuffle(validMoves)

    validMoves.sort(key=lambda m: 0 if m.pieceCaptured != '--' else 1)

    if gs.checkmate:
        return -CHECKMATE+(DEPTH-depth)
    elif gs.draw:
        return DRAW

    maxscore=-CHECKMATE

    for move in validMoves:
        
        if depth==0 and move.pieceCaptured=='--':
            break

        gs.makeMove(move)
        try:
            score=-NegaMaxAlphaBeta(gs, depth-1 if depth!=0 else 0, qDepth-1 if depth==0 else qDepth, -beta,-alpha,-turn)
        finally:
            gs.undoMove()

        if score>maxscore:
            maxscore=score
            if depth==DEPTH:
                nextMove=move
                print(nextMove.getChessNotation(),'|',maxscore)

            alpha=max(alpha,maxscore)
            if alpha>=beta:
                break
    
    if depth!=0:
        TT[Z] = {"score": maxscore, "depth": depth}

    return maxscore


def scoreBoard(gs):

    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE+DEPTH
        else:
            return CHECKMATE-DEPTH
    
    elif gs.draw:
        return DRAW
    
    score=0
    for r in range(8):
        for c in range(8):

            if gs.board[r][c][0]=='w':
                score+=pieceScores[gs.board[r][c][1]]
                if gs.board[r][c][1]=='p':
                    score+=pawnHeatMap[r][c]
                elif gs.board[r][c][1]=='N':
                    score+=knightHeatMap[r][c]
                elif gs.board[r][c][1]=='B':
                    score+=mobilityScore(gs,r,c)
                elif gs.board[r][c][1]=='R' and ROOKMOBILITY:
                    score+=mobilityScore(gs,r,c)
                    if r==1:
                        score+=3
                    if r==0:
                        score+=2
                elif gs.board[r][c][1]=='Q' and QUEENMOBILITY:
                    score+=mobilityScore(gs,r,c)
                elif gs.board[r][c][1]=='K':
                    score+=kingSafetyScore(gs,r,c)
                
                if 3<=r<=4 and 3<=c<=4:
                    score+=CENTERPRESENCE

            elif gs.board[r][c][0]=='b':
                score-=pieceScores[gs.board[r][c][1]]
                if gs.board[r][c][1]=='p':
                    score-=pawnHeatMap[7-r][c]
                elif gs.board[r][c][1]=='N':
                    score-=knightHeatMap[r][c]
                elif gs.board[r][c][1]=='B':
                    score-=mobilityScore(gs,r,c)
                elif gs.board[r][c][1]=='R' and ROOKMOBILITY:
                    score-=mobilityScore(gs,r,c)
                    if r==6:
                        score-=3
                    elif r==7:
                        score-=2
                elif gs.board[r][c][1]=='Q' and QUEENMOBILITY:
                    score-=mobilityScore(gs,r,c)
                elif gs.board[r][c][1]=='K':
                    score-=kingSafetyScore(gs,r,c)

                if 3<=r<=4 and 3<=c<=4:
                    score-=CENTERPRESENCE

    return score