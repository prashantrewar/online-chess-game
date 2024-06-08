import json
import socket
from _thread import start_new_thread
from board import Board
from player import Player
import pickle
import time

# Initialize global variables
players = {}

# Load existing ratings from file
def load_ratings():
    global players
    try:
        with open('ratings.json', 'r') as f:
            ratings = json.load(f)
            for name, rating in ratings.items():
                players[name] = Player(name)
                players[name].rating = rating
    except FileNotFoundError:
        pass

load_ratings()

# Functions for handling ratings and performance
def update_ratings(winner, loser):
    K = 32  # K-factor
    expected_win_winner = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))
    expected_win_loser = 1 / (1 + 10 ** ((winner.rating - loser.rating) / 400))
    
    winner.rating += K * (1 - expected_win_winner)
    loser.rating += K * (0 - expected_win_loser)

def log_performance(winner, loser):
    with open('performance.log', 'a') as f:
        f.write(f"{winner.name} won against {loser.name}. New ratings - {winner.name}: {winner.rating}, {loser.name}: {loser.rating}\n")

def save_ratings():
    with open('ratings.json', 'w') as f:
        json.dump({player.name: player.rating for player in players.values()}, f)

# Server setup and main loop
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("[START] Waiting for a connection")

connections = 0
games = {0: Board(8, 8)}
spectartor_ids = []
specs = 0

def read_specs():
    global spectartor_ids
    spectartor_ids = []
    try:
        with open("specs.txt", "r") as f:
            for line in f:
                spectartor_ids.append(line.strip())
    except:
        print("[ERROR] No specs.txt file found, creating one...")
        open("specs.txt", "w")

def threaded_client(conn, game, spec=False):
    global pos, games, currentId, connections, specs, players

    if not spec:
        name = None
        bo = games[game]

        if connections % 2 == 0:
            currentId = "w"
        else:
            currentId = "b"

        bo.start_user = currentId
        data_string = pickle.dumps(bo)

        if currentId == "b":
            bo.ready = True
            bo.startTime = time.time()

        conn.send(data_string)
        connections += 1

        while True:
            if game not in games:
                break

            try:
                d = conn.recv(8192 * 3)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    if data.count("select") > 0:
                        all = data.split(" ")
                        col = int(all[1])
                        row = int(all[2])
                        color = all[3]
                        bo.select(col, row, color)

                    if data == "winner b":
                        bo.winner = "b"
                        winner = players[bo.p2Name]
                        loser = players[bo.p1Name]
                        update_ratings(winner, loser)
                        log_performance(winner, loser)
                        print("[GAME] Player b won in game", game)
                        print(f"[RATING] {bo.p2Name} rating: {winner.rating}")
                        print(f"[RATING] {bo.p1Name} rating: {loser.rating}")
                    if data == "winner w":
                        bo.winner = "w"
                        winner = players[bo.p1Name]
                        loser = players[bo.p2Name]
                        update_ratings(winner, loser)
                        log_performance(winner, loser)
                        print("[GAME] Player w won in game", game)
                        print(f"[RATING] {bo.p1Name} rating: {winner.rating}")
                        print(f"[RATING] {bo.p2Name} rating: {loser.rating}")
                        
                    if data == "update moves":
                        bo.update_moves()

                    if data.count("name") == 1:
                        name = data.split(" ")[1]
                        if currentId == "b":
                            bo.p2Name = name
                        elif currentId == "w":
                            bo.p1Name = name
                        if name not in players:
                            players[name] = Player(name)

                    if bo.ready:
                        if bo.turn == "w":
                            bo.time1 = 900 - (time.time() - bo.startTime) - bo.storedTime1
                        else:
                            bo.time2 = 900 - (time.time() - bo.startTime) - bo.storedTime2

                    sendData = pickle.dumps(bo)
                conn.sendall(sendData)

            except Exception as e:
                print(e)
        
        connections -= 1
        try:
            del games[game]
            print("[GAME] Game", game, "ended")
        except:
            pass
        print("[DISCONNECT] Player", name, "left game", game)
        conn.close()

    else:
        available_games = list(games.keys())
        game_ind = 0
        bo = games[available_games[game_ind]]
        bo.start_user = "s"
        data_string = pickle.dumps(bo)
        conn.send(data_string)

        while True:
            available_games = list(games.keys())
            bo = games[available_games[game_ind]]
            try:
                d = conn.recv(128)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    try:
                        if data == "forward":
                            print("[SPECTATOR] Moved Games forward")
                            game_ind += 1
                            if game_ind >= len(available_games):
                                game_ind = 0
                        elif data == "back":
                            print("[SPECTATOR] Moved Games back")
                            game_ind -= 1
                            if game_ind < 0:
                                game_ind = len(available_games) -1

                        bo = games[available_games[game_ind]]
                    except:
                        print("[ERROR] Invalid Game Recieved from Spectator")

                    sendData = pickle.dumps(bo)
                    conn.sendall(sendData)

            except Exception as e:
                print(e)

        print("[DISCONNECT] Spectator left game", game)
        specs -= 1
        conn.close()

while True:
    read_specs()
    if connections < 6:
        conn, addr = s.accept()
        spec = False
        g = -1
        print("[CONNECT] New connection")

        for game in games.keys():
            if games[game].ready == False:
                g=game

        if g == -1:
            try:
                g = list(games.keys())[-1]+1
                games[g] = Board(8,8)
            except:
                g = 0
                games[g] = Board(8,8)

        print("[DATA] Number of Connections:", connections+1)
        print("[DATA] Number of Games:", len(games))

        start_new_thread(threaded_client, (conn,g,spec))

save_ratings()
