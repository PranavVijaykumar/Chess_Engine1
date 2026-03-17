# ♟️ Chess Engine (Python)

This is a chess engine I built from scratch in Python while exploring
game engines, optimization, and search algorithms. It started as a basic
move generator and gradually evolved into something much more
interesting, especially with experiments around improving move
generation efficiency and AI search depth.

------------------------------------------------------------------------

## What this project does

-   Generates all legal chess moves (including pins and checks)
-   Handles special rules (castling, en passant, promotion)
-   Plays against you using an AI (alpha-beta search)
-   Keeps track of game state efficiently (with undo support)

There's also an ongoing attempt to build a more advanced version that
avoids recomputing all moves after every turn.

------------------------------------------------------------------------

## You can play it right now

You can already play against the engine using the Pygame interface.

``` bash
python ChessMain.py
```

-   You play as White by default\
-   The AI plays the other side\
-   Press `z` to undo moves\
-   Press `r` to reset the game

It's simple, but it works --- and yes, it will try to beat you.

------------------------------------------------------------------------

## How the engine is structured

The engine is built using an object-oriented design to keep the logic
modular and manageable.

### Game State Representation

-   The entire board is stored inside a `GameState` object\
-   It tracks:
    -   Board configuration\
    -   Turn information\
    -   King positions\
    -   Castling rights and en passant\
    -   Move history (for undo functionality)

This makes it easy to simulate moves, backtrack, and explore game trees.

------------------------------------------------------------------------

### Move Abstraction

Moves are represented using a dedicated `Move` object, which stores:

-   Start and end coordinates\
-   Piece moved and piece captured\
-   Special move information (promotion, castling, en passant)

This abstraction simplifies:

-   Move comparison\
-   Logging\
-   Reversing moves

------------------------------------------------------------------------

### Move Generation Logic

Legal move generation is not just "generate everything and filter
later".

Instead, the engine:

-   Detects **pins and checks first**
-   Uses that information to **restrict illegal moves during
    generation**
-   Handles:
    -   Single check (blocking/capturing)
    -   Double check (king-only moves)

This keeps move generation both correct and efficient.

------------------------------------------------------------------------

## Search

-   Negamax with Alpha-Beta pruning\
-   Basic move ordering (captures first)\
-   Quiescence search to avoid unstable positions

The engine also uses:

-   Zobrist hashing\
-   Transposition tables

to avoid recomputing already-seen positions.

------------------------------------------------------------------------

## Evaluation (Heuristics)

The engine evaluates positions using a mix of heuristics rather than
just raw material count.

### Material

Each piece is assigned a base value.

------------------------------------------------------------------------

### Piece Activity (Mobility)

-   Sliding pieces (bishops, rooks, queens) are rewarded for having more
    available moves\
-   Also considers attacking and defending pieces

------------------------------------------------------------------------

### Positional Heuristics (Heatmaps)

-   Pawns and knights use piece-square tables\
-   Encourages central control and better positioning

------------------------------------------------------------------------

### King Safety

-   Penalizes exposed kings\
-   Rewards castling and safer structures\
-   Considers nearby threats and defenders

------------------------------------------------------------------------

## Experimental Feature (Main Focus)

### Incremental Move Generation

Normally, engines do this after every move:\
\> recompute all legal moves from scratch

I'm trying a different approach:\
\> update only the moves that are affected by the last move

This involves maintaining:

-   Move sets for both sides\
-   Pinned pieces\
-   Checks and interactions dynamically

------------------------------------------------------------------------

### Why this is hard (and interesting)

-   Pins and checks are very sensitive to small changes\
-   Sliding pieces create long-range dependencies\
-   Undoing moves correctly becomes tricky\
-   Easy to introduce subtle bugs

------------------------------------------------------------------------

## Results / Observations

Some observations from experimentation:

-   Using a **transposition table (TT)** consistently allowed the engine
    to search about **one extra depth level**, especially when combined
    with dynamic depth adjustments based on the game stage.

-   **Zobrist hashing** significantly improved performance and move
    quality:

    -   The engine avoids recalculating repeated positions\
    -   It started naturally recognizing common structures and playing
        sensible opening moves\
    -   This happened even without any explicit opening database

These optimizations made the engine noticeably stronger without changing
the core evaluation logic.

------------------------------------------------------------------------

## Files

-   `ChessMain.py` → UI (Pygame, play the game here)\
-   `ChessEngine.py` → Standard move generation\
-   `ChessEngineAdvanced.py` → Incremental move updates (work in
    progress)\
-   `ChessAI.py` → Search + evaluation

------------------------------------------------------------------------

## Where this is going

-   Compare incremental vs full recomputation\
-   Improve evaluation function\
-   Try bitboards for performance\
-   Add iterative deepening\
-   Improve quiescence search

------------------------------------------------------------------------

## Why I built this

This started as a learning project, but it turned into something more.

Understanding how to:

-   Efficiently update state\
-   Avoid redundant computation\
-   Structure a non-trivial system

The incremental move generation part is something I'd like to explore
further as a research direction. After that, I'm also interested in
experimenting with reinforcement learning and more logic-based
approaches (like ASP), especially for structured endgame reasoning.

------------------------------------------------------------------------

## Contact

Pranav Vijaykumar\
IIT Kharagpur - Electrical Engineering\
Summer Intern at Google (SDE)\
Interested in AI systems, optimization, and software development\
Email: mindyourviews@gmail.com
