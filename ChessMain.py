import pygame as p
import ChessEngine
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
    gs=ChessEngine.GameState()
    validMoves=gs.getValidMoves()
    moveMade=False
    load_images()
    sqSelected=()
    playerClicks=[]
    running=True
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos()
                col=location[0]//SQ_SIZE
                row=location[1]//SQ_SIZE
                if sqSelected==(row,col) or (len(playerClicks)==0 and gs.board[row][col]=="--"):
                    sqSelected=()
                    playerClicks=[]
                else:
                    sqSelected=(row,col)
                    playerClicks.append(sqSelected)
                if len(playerClicks)==2:
                    move=ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                    if move.getMoveID() in validMoves:
                        gs.makeMove(move)
                        print(move.getChessNotation())
                        moveMade=True
                    sqSelected=()
                    playerClicks=[]

        if moveMade:
            validMoves=gs.getValidMoves()
            moveMade=False
            
        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()
         
def drawGameState(screen,gs):
    drawBoard(screen)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    colours=[p.Color("light gray"),p.Color("dark green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):            
            colour=colours[(r+c)%2]
            p.draw.rect(screen,colour,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece=board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

if __name__=="__main__":
    main()