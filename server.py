import asyncio
import websockets
import random
import os
import json
from game import handle_command, player_data

used_house_positions = set()
PLAYER_FILE = "players.json"

# Load saved players
if os.path.exists(PLAYER_FILE):
    with open(PLAYER_FILE, "r") as f:
        saved_players = json.load(f)
else:
    saved_players = {}

def save_players():
    clean = {}
    for user, pdata in saved_players.items():
        clean[user] = {
            key: val for key, val in pdata.items()
            if key != "conn"
        }
    with open(PLAYER_FILE, "w") as f:
        json.dump(clean, f, indent=2)

def get_unique_house_pos():
    while True:
        pos = (random.randint(0, 49), 25)
        if pos not in used_house_positions:
            used_house_positions.add(pos)
            return list(pos)

async def handle_connection(websocket):
    await websocket.send("Welcome to LANQuest! Enter your username:")
    username = await websocket.recv()

    while not username or username in player_data:
        await websocket.send("Username taken or invalid. Try another:")
        username = await websocket.recv()

    await websocket.send("Do you want to login or register? (login/register):")
    action = await websocket.recv()
    action = action.lower().strip()

    while action not in ("login", "register"):
        await websocket.send("Invalid option. Type 'login' or 'register':")
        action = await websocket.recv()
        action = action.lower().strip()

    if action == "register":
        if username in saved_players:
            await websocket.send("Username already exists.")
            return
        pdata = {
            "pos": [random.randint(0, 49), random.randint(0, 49)],
            "house": get_unique_house_pos(),
            "inventory": [],
            "hp": 100,
            "dialogue": None,
            "username": username,
            "goldeggexist": True,
            "eggpos": [random.randint(29, 34), random.randint(34, 39)],
            "climbcount": 0,
            "trade": None,
        }
        saved_players[username] = pdata
        save_players()
    elif action == "login":
        if username not in saved_players:
            await websocket.send("No such user.")
            return
        pdata = saved_players[username]

    pdata["conn"] = websocket
    player_data[username] = pdata

    await websocket.send(f"Welcome, {username}! Type 'help' for commands.")

    try:
        async for message in websocket:
            await handle_command(websocket, username, message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        saved_players[username] = player_data[username]
        del player_data[username]
        save_players()
        print(f"{username} disconnected.")

async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
