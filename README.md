# Online Multiplayer Chess
Description: An online multiplayer chess game. Supports infinite players playing against random opponents on different machines on different networks. This project was created using python 3.7, pygame and the sockets module from python3. It runs on a basic client server system where a server script handles all incoming connections and game management. The clients simply hanlde the UI and game play.


# Required:
- Python 3.x
- pygame


# TO MAKE THIS CODE WORK...
You will need to change the server address from within the following two files:
- client.py
- server.py

You will also need to run server.py on some kind of server. After that you can launch two instances of game from anywhere to play online chess.

## Step 1: To start the server

```bash
{ pip3 install -r requirements.txt; } && { python3 server.py; }
```

## Step 2: Make a new connection for layer

```bash
python3 game.py
```

Run this command in the new terminal for each player.


# List of the APIs available

## Server APIs:

'threaded_client(conn, game, spec=False)': Handles client connections and game state updates.

update_ratings(winner_color, loser_color): Updates player ratings after a game ends.

save_ratings(): Saves player ratings to a file.

load_ratings(): Loads player ratings from a file.

## Client APIs:

connect(): Connects the client to the server.

send(data): Sends data to the server.

receive(): Receives data from the server.


## Game Object APIs:

Board.update_moves(): Updates the valid moves for all pieces on the board.

Board.draw(win, color): Draws the board and pieces on the screen.

Board.select(col, row, color): Handles piece selection and movement.

Board.is_checked(color): Checks if the king of the given color is in check.

Board.check_mate(color): Checks if the given color is in checkmate.

Board.move(start, end, color): Moves a piece on the board and handles captures.

## Piece APIs:

Piece.update_valid_moves(board): Updates the valid moves for the piece.

Piece.draw(win, color): Draws the piece on the screen.

Piece.change_pos(new_pos): Changes the position of the piece.


# List the various game objects involved

## Board:

Manages the chessboard grid and the positioning of pieces.
Methods for updating moves, drawing the board, selecting pieces, checking for check/checkmate, and moving pieces.

## Piece:

Base class for all chess pieces, managing common attributes and methods.
Subclasses: Bishop, King, Knight, Pawn, Queen, Rook.
Methods for updating valid moves, drawing pieces, and changing positions.

## Player:

Manages player information such as name, color, and rating.

## Server:

Manages client connections, game states, and communication between clients.
Methods for handling client threads, updating ratings, and saving/loading ratings.

## Client:

Manages connection to the server and communication with it.


# Known Bugs:
- Checkmate does not work, if you loose or win you will need to end the game by hitting "q"
- Very rare bug where a certain move will crash the game
- No Enpesant Pawn Rule


