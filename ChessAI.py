import random,math,ChessEngine

CENTERPRESENCE=1
CHECKMATE=10000
DRAW=0
DEPTH=5
MOBILITYFACTOR=0.5
ATTACKFACTOR=1
PROTECTFACTOR=0.8
ROOKMOBILITY=False

pieceScores = {'K':0, 'Q':90, 'R':50, 'B':30, 'N':30, 'p':10}

knightHeatMap=[[0, 1, 1, 1, 1, 1, 1, 0],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [0, 1, 1, 1, 1, 1, 1, 0]]

pawnHeatMap=[[-1,-1,-1,-1,-1,-1,-1,-1],
             [8, 9, 9, 9, 9, 9, 9, 8],
             [5, 6, 6, 7, 7, 6, 6, 5],
             [2, 3, 4, 5, 5, 4, 3, 2],
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
            elif gs.willBeCheck(r,c):
                checkCount+=1

    score+= -2 if frndCount<=1 else 0
    score-= math.floor(16*10**(-4/checkCount))
    
    return score


def mobilityScore(gs,r,c):
    moveCount=0
    piecesProtected=0
    piecesAttacked=0
    frndColor='w' if gs.board[r][c]=='w' else 'b'

    if gs.board[r][c][1]=='B':

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

    
    elif gs.board[r][c][1]=='R':

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
    global nextMove,DEPTH,ROOKMOBILITY,MOBILITYFACTOR,PROTECTFACTOR,ATTACKFACTOR
    nextMove=None

    # if len(gs.moveLog) == 6 if gs.whiteToMove else 7:
    #     DEPTH=4

    if rawBoardScore(gs)<500 and PROTECTFACTOR==0.8:
        PROTECTFACTOR=1.2
        ATTACKFACTOR=0.9

    elif 300<rawBoardScore(gs)<420 and not(ROOKMOBILITY):
        DEPTH=5
        MOBILITYFACTOR/=2
        ROOKMOBILITY=True

    elif rawBoardScore(gs)<300 and DEPTH==5:
        DEPTH=6

    #RecursiveMinMax(gs,DEPTH,validMoves,gs.whiteToMove)
    NegaMaxAlphaBeta(gs,DEPTH,-CHECKMATE,CHECKMATE, 1 if gs.whiteToMove else -1)
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



def NegaMaxAlphaBeta(gs,depth,alpha,beta,turn):

    global nextMove
    if depth==0:
        return turn*scoreBoard(gs)

    validMoves=gs.getValidMoves()

    if gs.checkmate:
        return -CHECKMATE+(DEPTH-depth)
    elif gs.draw:
        return DRAW
    
    if depth==DEPTH:
        random.shuffle(validMoves)

    maxscore=-CHECKMATE
    for move in validMoves:

        gs.makeMove(move)
        try:
            score=-NegaMaxAlphaBeta(gs,depth-1,-beta,-alpha,-turn)
        finally:
            gs.undoMove()

        if score>maxscore:
            maxscore=score
            if depth==DEPTH:
                nextMove=move

            alpha=max(alpha,maxscore)
            if alpha>=beta:
                break

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
    if gs.whiteToMove:
        whiteValidMoves=gs.getValidMoves()
        gs.makeMove(ChessEngine.Move((6,7),(6,7),gs.board))
        blackValidMoves=gs.getValidMoves()
    
    else:
        blackValidMoves=gs.getValidMoves()
        gs.makeMove(ChessEngine.Move((1,7),(1,7),gs.board))
        whiteValidMoves=gs.getValidMoves()
    
    gs.undoMove()

    score+= (len(whiteValidMoves)-len(blackValidMoves))*MOBILITYFACTOR/2

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
                elif gs.board[r][c][1]=='Q':
                    pass
                elif gs.board[r][c][1]=='K':
                    score+=kingSafetyScore(gs,r,c)
                
                if 2<=r<=5 and 2<=c<=5:
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
                elif gs.board[r][c][1]=='Q':
                    pass
                elif gs.board[r][c][1]=='K':
                    score-=kingSafetyScore(gs,r,c)

                if 2<=r<=5 and 2<=c<=5:
                    score-=CENTERPRESENCE

    return score