import pygame as p
import ChessEngine,ChessAI
p.init()

WIDTH=HEIGHT=512
DIMENSION=8
SQ_SIZE=HEIGHT//DIMENSION
MAX_FPS=15
IMAGES={}

def load_images():

    pieces=["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK",]
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("Piece_images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))

def main():

    screen=p.display.set_mode((WIDTH,HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()
    gs=ChessEngine.GameState()

    gameOver=False
    validMoves=gs.getValidMoves()
    moveMade=False
    sqSelected=()
    playerClicks=[]
    running=True
    playerWhite=True
    playerBlack=False

    while running:

        humanMove=(gs.whiteToMove and playerWhite) or (not(gs.whiteToMove) and playerBlack)
        for e in p.event.get():

            if e.type==p.QUIT:
                running=False

            elif e.type==p.MOUSEBUTTONDOWN:   #Mouse clicks

                if not(gameOver) and humanMove:

                    location=p.mouse.get_pos()
                    col=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE

                    if gs.board[row][col][0]==('w' if gs.whiteToMove else 'b'):

                        if (row,col)==sqSelected:
                            sqSelected=()
                            playerClicks=[]
                        else:
                            sqSelected=(row,col)
                            playerClicks=[sqSelected]
                    

                    elif len(playerClicks)==1:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected)


                    if len(playerClicks)==2:
                        moveID=playerClicks[0][0]*1000 + playerClicks[0][1]*100 + playerClicks[1][0]*10 + playerClicks[1][1]
                        for move in validMoves:
                            if moveID==move.getMoveID():
                                gs.makeMove(move)
                                print(move.getChessNotation())
                                moveMade=True
                        sqSelected=()
                        playerClicks=[]

            
            elif e.type==p.KEYDOWN:         #Keyboard clicks

                if e.key==p.K_z:
                    gs.undoMove()
                    validMoves=gs.getValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    if gameOver:
                        gameOver=False
                
                if e.key==p.K_r:
                    gs=ChessEngine.GameState()
                    gameOver=False
                    validMoves=gs.getValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    moveMade=False


        if not(gameOver):

            if not(humanMove):
                move=ChessAI.bestMove(gs)
                if move is None:
                    move=ChessAI.randomMove(validMoves)
                gs.makeMove(move)
                print(move.getChessNotation())
                moveMade=True

            if moveMade:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
                validMoves=gs.getValidMoves()
                moveMade=False

            drawGameState(screen,gs,validMoves,sqSelected)

            if gs.checkmate:
                
                if gs.whiteToMove:
                    drawText(screen,'Black wins by checkmate')
                else:
                    drawText(screen,'White wins by checkmate')
                gameOver=True
            
            if gs.draw:
                
                if gs.stalemate:
                    drawText(screen,'Draw through stalemate')
                elif gs.fiftyMoveCounter==50:
                    drawText(screen,'Draw through 50 Move Rule')
                else:
                    drawText(screen,'Draw through Repetition')
                gameOver=True
            
            clock.tick(MAX_FPS)
            p.display.flip()


def drawGameState(screen,gs,validMoves,sqSelected):

    drawBoard(screen)

    highlight(screen,validMoves,sqSelected)

    drawPieces(screen,gs.board)


def drawBoard(screen):

    global colours
    colours=[p.Color("light gray"),p.Color("dark green")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):            
            colour=colours[(r+c)%2]
            p.draw.rect(screen,colour,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))


def highlight(screen,validMoves,sqSelected):

    if sqSelected:    #To not highlight if nothing is selected
        r,c=sqSelected
        s=p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100) #transparency value
        s.fill(p.Color('blue'))
        screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
        s.fill(p.Color('yellow'))

        for move in validMoves:     #To highlight accessible squares
            if move.startRow==r and move.startCol==c:
                screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))


def drawPieces(screen,board):

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece=board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))


def animateMove(move,screen,board,clock):

    global colours
    dR=move.endRow-move.startRow
    dC=move.endCol-move.startCol
    framesPerSquare=8  #frames to move one square
    frameCount=(abs(dR)+abs(dC))*framesPerSquare

    for frame in range(frameCount+1):

        r,c =  (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)

        colour=colours[(move.endRow+move.endCol)%2]  #erase the piece moved from its ending square
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,colour,endSquare)

        if move.pieceCaptured!='--':  #draw captured piece onto rectangle
            screen.blit(IMAGES[move.pieceCaptured],endSquare)

        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)) #draw moving pieces
        p.display.flip()
        clock.tick(60)


def drawText(screen,text):
    font=p.font.SysFont("Helvetica",32,True,False)
    textObject=font.render(text,0,p.Color('Gray'))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))


if __name__=="__main__":
    main()