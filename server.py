# imports
import asyncio
import websockets
import random
import os
import json
from game import handle_command, player_data
from encrypt_players import load_players_encrypted, save_players_encrypted

# save and load players

# load players (save and load players)
saved_players = load_players_encrypted()

# shop inv

# save players (save and load players)
def save_players():
    #  strip non-serializable stuff like connections BEFORE calling this
    clean = {
        user: {k: v for k, v in pdata.items() if k != "conn"}
        for user, pdata in saved_players.items()
    }
    save_players_encrypted(clean)

# unique house positions along y=25
used_house_positions = set()
def get_unique_house_pos():
    while True:
        pos = (random.randint(0, 49), 25)
        if pos not in used_house_positions:
            used_house_positions.add(pos)
            return list(pos)

# connection handler
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

        await websocket.send("Choose a password:")
        password = await websocket.recv()

        await websocket.send("What is your character's preferred gender in a relationship?(m/f) (trust me, this matters.)")
        preferred_gender = await websocket.recv()
        preferred_gender = preferred_gender.lower().strip()
        if preferred_gender not in ["m", "f"]:
            await websocket.send("Please enter in 'm' or 'f'.")
            preferred_gender = await websocket.recv()
            preferred_gender = preferred_gender.lower().strip()

        pdata = {
            "pos": [random.randint(0, 49), random.randint(0, 49)],
            "house": get_unique_house_pos(),
            "inventory": [],
            "hp": 100,
            "dialogue": None,
            "username": username,
            "password": password,
            "goldeggexist": True,
            "eggpos": [random.randint(29, 34), random.randint(34, 39)],
            "climbcount": 0,
            "trade": None,
            "preferred_gender": preferred_gender,
            "xp": 0,
            "gp": 0,
            "level": 1,
            "last_work_time": 0,
        }
        saved_players[username] = pdata
        save_players()
    elif action == "login":
        if username not in saved_players:
            await websocket.send("No such user.")
            return
        await websocket.send("Enter your password:")
        password = await websocket.recv()
        if password != saved_players[username]["password"]:
            await websocket.send("Password incorrect.")
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

# main (server startup)
async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()  #  run forever

# run main
asyncio.run(main())
