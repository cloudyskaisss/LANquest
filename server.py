import asyncio
import websockets
from game import handle_command, player_data
import random

used_house_positions = set()

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

    player_data[username] = {
        "conn": websocket,
        "pos": [random.randint(0, 49), random.randint(0, 49)],
        "house": get_unique_house_pos(),
        "inventory": [],
        "hp": 100,
        "dialogue": None,
        "username": username,
    }

    await websocket.send(f"Welcome, {username}! Type 'help' for commands.")

    try:
        async for message in websocket:
            await handle_command(websocket, username, message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        del player_data[username]
        print(f"{username} disconnected.")

async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
