import random
import datetime

player_data = {}

def get_preferred_gender(pdata, time):
    if time == "dialogue_in_restaurant":
        if pdata["preferred_gender"] == "m":
            return "man"
        elif pdata["preferred_gender"] == "f":
            return "lady"
    if time == "dialogue_in_restaurant_2_electric_boogaloo":
        if pdata["preferred_gender"] == "f":
            return "ma'am"
        elif pdata["preferred_gender"] == "m":
            return "sir"

def fmt(text, pdata):
    return text.format(
        pg1=get_preferred_gender(pdata, "dialogue_in_restaurant"),
        pg2=get_preferred_gender(pdata, "dialogue_in_restaurant_2_electric_boogaloo")
    )

def nearby_players(username):
    x, y = player_data[username]["pos"]
    nearby = []
    for other, data in player_data.items():
        if other == username:
            continue
        ox, oy = data["pos"]
        if abs(x - ox) <= 5 and abs(y - oy) <= 5:
            nearby.append(other)
    return nearby


async def send_node(conn, tree_id, node_id, pdata):
    node = DIALOGUE_TREES[tree_id][node_id]
    prompt = fmt(node["prompt"], pdata)
    opts = "\n".join(f"{k}. {fmt(v['text'], pdata)}" for k, v in node["options"].items())
    await conn.send(f"{prompt}\n{opts}\n")

def start_dialogue(pdata, tree_id, node_id="root"):
    pdata["dialogue"] = {"tree": tree_id, "node": node_id}

async def advance_dialogue(conn, pdata, choice):
    dlg = pdata["dialogue"]
    tree = DIALOGUE_TREES[dlg["tree"]]
    node = tree[dlg["node"]]

    if choice not in node["options"]:
        await conn.send("Invalid choice. Pick a number from the list.\n")
        return

    opt = node["options"][choice]

    if evt := opt.get("event"):
        handler = EVENTS.get(evt)
        if handler:
            await handler(conn, pdata)


    if opt.get("end"):
        pdata["dialogue"] = None
        await conn.send("You leave the conversation.\n")
        return

    next_node = opt["next"]
    dlg["node"] = next_node
    await send_node(conn, dlg["tree"], next_node, pdata)




# somewhere global
async def ev_buy_sword(conn, pdata):
    if pdata["gp"] >= .5:
        pdata["inventory"].append("sword")
        await conn.send("You received a sword!\n")
        pdata["gp"] -= .5
    else:
        await conn.send("Unfortunately, you do not have the money for that.")

async def ev_buy_shield(conn, pdata):
    if pdata["gp"] >= .3:
        pdata["inventory"].append("shield")
        await conn.send("You got a shield!!\n")
        pdata["gp"] -= .3
    else:
        await conn.send("Unfortunately, you do not have the money for that.")

async def ev_give_bread(conn, pdata):
    pdata["inventory"].append("bread")
    await conn.send("You take some bread. (+10 hp)\n")

async def ev_give_ale(conn, pdata):
    pdata["inventory"].append("ale")
    await conn.send("You got a cup of ale. (+5 hp)\n")

async def ev_sell_egg(conn, pdata):
    if "golden egg" in pdata["inventory"]:
        pdata["inventory"].remove("golden egg")
        await conn.send('"Looks like a counterfeit there. Have 5 gold coins for your trouble anyways."')
        pdata["gp"] += 5
    else:
        await conn.send('"What golden egg? Are ya a lunatic?!" The shopkeeper punches you in the face. (-5 hp)')
        pdata["hp"] -= 5

async def ev_sell_sword(conn, pdata):
    if "sword" in pdata["inventory"]:
        pdata["inventory"].remove("sword")
        await conn.send('"There\'s your cash. Don\'t spend it all in one place!"')
        pdata["gp"] += .3
    else:
        await conn.send('"What sword? Are ya crazy?!" The shopkeeper socks you in the face. (-7 hp)')
        pdata["hp"] -= 7

async def ev_sell_shield(conn, pdata):
    if "shield" in pdata["inventory"]:
        pdata["inventory"].remove("shield")
        await conn.send('"Here\'s your money. Spend it all in one place."')
        pdata["gp"] += .2
    else:
        await conn.send('"What shield? Are ya stupid?!" The shopkeeper roundhouse kicks you in the face. (-15 hp)')
        pdata["hp"] -= 15

EVENTS = {
    "buy_sword": ev_buy_sword,
    "buy_shield": ev_buy_shield,
    "give_bread": ev_give_bread,
    "give_ale": ev_give_ale,
    "sell_golden_egg": ev_sell_egg,
    "sell_sword":      ev_sell_sword,
    "sell_shield":     ev_sell_shield,
}



DIALOGUE_TREES = {
    "shopkeeper": {
        "root": {
            "prompt": '"Hello there! Welcome, how can I help you?"',
            "options": {
                "1": {"text": "Ask about the stock.", "next": "node2"},
                "2": {"text": "Sell something.", "next": "node5"},
                "3": {"text": "Ask about rumours.", "next": "node3"},
                "4": {"text": "Leave.",   "end": True}
            }
        },
        "node2": {
            "prompt": '“The swords will last a life, and take one too. The shields will buy ya some time. Any other stuff is sold to us from our customers!”',
            "options": {
                "1": {"text": 'Buy something.', "next": "node4"},
                "2": {"text": 'Go back', "next": "root"},
                "3": {"text": 'Leave.',   "end": True}
            }
        },
        "node3": {
            "prompt": '"Ahh... Well a little birdy told me that there are some bandits around this part of town.”',
            "options": {
                "1": {"text": 'Go back.', "next": "root"},
                "2": {"text": 'Leave.', "end": True}
            }
        },
        "node4": {
            "prompt": '"What would ya like to buy?”',
            "options": {
                "1": {"text": 'A sword.', "event": "buy_sword", "end": True},
                "2": {"text": 'A shield, please.', "event": "buy_shield", "end": True},
                "3": {"text": "Leave.", "end": True}
            }
        },
        "node5": {
            "prompt": '"What would ya like to sell?"',
            "options": {
                "1": {"text": "A shimmering golden egg. It's made of porcelain!", "event": "sell_golden_egg", "end": True},
                "2": {"text": "A shiny sword. It's pure steel.", "event": "sell_sword", "end": True},
                "3": {"text": "A sturdy wooden shield.", "event": "sell_shield", "end": True},
                "4": {"text": "Go back.", "next": "root"},
                "5": {"text": "Leave.", "end": True},
            }
        },
    },
    "server": {
        "root": {
            "prompt": '"Welcome to the restaurant! Can I get you something to eat, or are you just hanging out?"',
            "options": {
                "1": {"text": 'Could I get some food?', "next": "node2"},
                "2": {"text": 'Just hanging out.', "next": "node3"},
                "3": {"text": 'Leave.', "end": True}
            }
        },
        "node2": {
            "prompt": '"Alright, what would you like?"',
            "options": {
                "1": {"text": "I'll take some bread.", "event": "give_bread" , "end": True},
                "2": {"text": "How about some ale?", "event": "give_ale", "end": True},
                "3": {"text": "Leave.", "end": True}
            }
        },
        "node3": {
            "prompt": 'While sitting down, you come across a young {pg1}.',
            "options": {
                "1": {"text": "Approach the {pg1}", "next": "node4"},
                "2": {"text": "Leave the {pg1} alone.", "next": "node5"},
                "3": {"text": "Leave.", "end": True}
            }
        },
        "node4": {
            "prompt": "The {pg1} says 'Hello! Could I get you something to drink?'",
            "options": {
                "1": {"text": "Sure, {pg2}", "next": "node6"},
                "2": {"text": "No, I'm good. What's your name though?", "next": "node8"},
                "3": {"text": "Leave like the wimp you are.", "end": True}
            }
        },
        "node5": {
            "prompt": "You leave her alone. Now what?",
            "options": {
                "1": {"text": "Go back.", "next": "root"},
                "2": {"text": "Leave.", "end": True}
            }
        },
        "node6": {
            "prompt": "What would you like?",
            "options": {
                "1": {"text": "Just some ale, sweetheart.", "next": "node7"},
                "2": {"text": "Nothing, actually", "next": "node9"},
                "3": {"text": "Leave.", "end": True}
            }
        },
        "node7": {
            "prompt": '"Ew, nevermind!"',
            "options": {
                "1": {"text": "Go back.", "next": "root"},
                "2": {"text": "Leave.", "end": True}
            }
        },
        "node8": {
            "prompt": '"Nevermind..."',
            "options": {
                "1": {"text": "Go back.", "next": "root"},
                "2": {"text": "Leave.", "end": True}
            }
        },
        "node9": {
            "prompt": '"Ok...Nevermind."',
            "options": {
                "1": {"text": "Go back.", "next": "root"},
                "2": {"text": "Leave.", "end": True}
            }
        }
    },
}


async def handle_command(conn, username, data):
    pdata = player_data[username]

    x, y = pdata["pos"]



    cmd = data.lower().strip()
    cmd_raw = data.strip()

    if pdata.get("dialogue"):
        if cmd.isdigit():
            await advance_dialogue(conn, pdata, cmd)
        else:
            await conn.send("You're in a convo. Choose a number.\n")
        return
    await conn.send(f">{data.strip()}")
    if "in_combat" in pdata and pdata["in_combat"]:
        if cmd == "attack":
            damage = random.randint(3, 6)
            pdata["in_combat"]["enemy_hp"] -= damage
            await conn.send(f"You slash the goblin for {damage} damage!")

            if pdata["in_combat"]["enemy_hp"] <= 0:
                xp = random.randint(3,7)
                await conn.send("You defeated the goblin! +", xp, " XP")
                pdata["in_combat"] = None
                pdata["xp"] += xp
            else:
                retaliate = random.randint(1, 4)
                pdata["hp"] -= retaliate
                await conn.send(f"The goblin bites back! You lose {retaliate} HP. You have {pdata['hp']} HP left.")

            return
        else:
            await conn.send("You're in combat! Type 'attack' to fight!")
            return

    if cmd == "help":
        await conn.send("Available commands:")
        await conn.send("  move north/south/east/west - Move around")
        await conn.send("  home - Go to your house")
        await conn.send("  talk - Talk to nearby NPCs")
        await conn.send("  inventory - View items")
        await conn.send("  where - Show location")
        await conn.send("  who - List players")
        await conn.send("  say [msg] - Say something")
        await conn.send("  trade [name] - Start trade")
        await conn.send("  attack [name] - Attack a nearby player.")
        await conn.send("  nearby - List nearby players")
        await conn.send("  help - This list")
    elif cmd == "home":
        pdata["pos"] = pdata["house"][:]
        await conn.send("You return home.")
    elif cmd == "inventory":
        inv = pdata.get("inventory", [])
        if inv:
            await conn.send(f"You have: {', '.join(inv)}")
        else:
            await conn.send("Your inventory is empty.")
    elif cmd == "where":
        await conn.send(f"You are at ({x}, {y})")
        if x == 15 and y == 20:
            await conn.send("You are in the restaurant.")
        elif x == 10 and y == 20:
            await conn.send("You are in the store.")
        elif pdata["pos"] == pdata["house"]:
            await conn.send("You are in your home. Cozy!")
        elif x >= 30 and x <=35 and y >= 35 and y <= 40:
            await conn.send("You are in the forest. Perhaps there is some treasure nearby?")
    elif cmd == "who":
        names = ", ".join(player_data.keys())
        await conn.send(f"Players online: {names}")
    elif cmd.startswith("say "):
        msg = data[4:].strip()
        for other, odata in player_data.items():
            if other != username:
                await odata["conn"].send(f"{username} says: {msg}")
        await conn.send("You said it.")
    elif cmd == "talk":
        if [x, y] == [10, 20]:
            start_dialogue(pdata, "shopkeeper")
            await send_node(conn, "shopkeeper", "root", pdata)
        if [x, y] == [15, 20]:
            start_dialogue(pdata, "server")
            await send_node(conn, "server", "root", pdata)
    elif cmd.startswith("move ") and not cmd[-1].isdigit():
        direction = cmd.split(" ")[1]
        dx, dy = 0, 0
        if direction == "north": dy = 1
        elif direction == "south": dy = -1
        elif direction == "east": dx = 1
        elif direction == "west": dx = -1
        pdata["pos"][0] += dx
        pdata["pos"][1] += dy
        await conn.send(f"You move {direction}.")
        if x >=40 and x <=44 and pdata["pos"][1] >= 32 and pdata["pos"][1] <= 35:
            await conn.send("You are in the cave now. A green, rotten goblin attacks!")
            pdata["hp"] = pdata["hp"] - random.randint(1, 5)
            goblin_hp = 10
            await conn.send("Type 'attack' to fight the goblin!")

            pdata["in_combat"] = {
                "enemy": "goblin",
                "enemy_hp": goblin_hp
            }
    elif cmd.startswith("move") and cmd[-1].isdigit():
        direction = cmd.split(" ")[1]
        mult = int(cmd.split(" ")[2])
        dx, dy = 0, 0
        if direction == "north": dy = 1
        elif direction == "south": dy = -1
        elif direction == "east": dx = 1
        elif direction == "west": dx = -1
        pdata["pos"][0] += (dx * mult)
        pdata["pos"][1] += (dy * mult)
        await conn.send(f"You move {direction} {mult} times.")
        if x >=40 and x <=44 and pdata["pos"][1] >= 30 and pdata["pos"][1] <= 34:
            await conn.send("You are in the cave now. A green, rotten goblin attacks!")
            pdata["hp"] = pdata["hp"] - random.randint(1, 5)
            goblin_hp = 10
            await conn.send("Type 'attack' to fight the goblin!")

            pdata["in_combat"] = {
                "enemy": "goblin",
                "enemy_hp": goblin_hp
            }
        if x >= 35 and x <= 40 and pdata["pos"][1] >= 40 and pdata["pos"][1] <= 45:
            await conn.send("You are home.")
    elif cmd == "nearby":
        np = nearby_players(pdata["username"])
        if np:
            await conn.send(f"{np}")
        else:
            await conn.send("There's nobody nearby.")
    elif cmd.startswith("attack "):
        target = cmd.split(" ", 1)[1]
        if target not in player_data:
            await conn.send("No such player.")
        elif target == username:
            await conn.send("You can't attack yourself, weirdo.")
        else:
            tdata = player_data[target]
            if abs(x - tdata["pos"][0]) > 5 or abs(pdata["pos"][1] - tdata["pos"][1]) > 5:
                await conn.send("They're too far away to hit.")
            else:
                damage = random.randint(5, 15)
                tdata["hp"] -= damage
                await conn.send(f"You attack {target} for {damage} damage!")
                await tdata["conn"].send(f"{username} attacked you for {damage} damage! You have {tdata['hp']} HP left.")
    elif cmd.startswith("climb"):
        pdata.setdefault("climbcount", 0)

        # Check for golden egg first
        if pdata["pos"] == pdata["eggpos"] and pdata["goldeggexist"]:
            await conn.send("You climb the tree, and up there lays a golden egg!")
            return  # stop here

        # Forest climb
        elif 30 <= x <= 35 and 35 <= pdata["pos"][1] <= 40:
            pdata["climbcount"] += 1
            if pdata["climbcount"] >= 10:
                await conn.send(f"Maybe you should check {pdata['eggpos']}?")
                pdata["climbcount"] = 0
            else:
                await conn.send("You climb the tree. Not much to see, but you feel special up here.")

        else:
            await conn.send("There's nothing here to climb.")

    elif cmd.startswith("take") or cmd.startswith("grab"):
        if tuple(pdata["pos"]) == tuple(pdata.get("eggpos", ())) and pdata.get("goldeggexist"):
            await conn.send("You take the golden egg! +10 gold.")
            pdata.setdefault("inventory", []).append("golden egg")
            pdata["goldeggexist"] = False
        else:
            await conn.send("There's nothing here to take.")
    elif cmd.startswith("trade "):
        target = cmd.split(" ", 1)[1]
        if target not in player_data:
            await conn.send("No such player.")
        elif target == username:
            await conn.send("You can't trade with yourself.")
        elif abs(x - player_data[target]["pos"][0]) > 5 or abs(pdata["pos"][1] - player_data[target]["pos"][1]) > 5:
            await conn.send("They're too far away to trade.")
        elif player_data[target].get("trade"):
            await conn.send("They're already in a trade!")
        else:
            pdata["trade"] = {"with": target, "stage": "pending"}
            player_data[target]["trade"] = {"with": username, "stage": "incoming"}
            player_data[target]["trade_request"] = username  # 🛠️ Add this line
            await conn.send(f"You offered to trade with {target}.")
            await player_data[target]["conn"].send(f"{username} wants to trade with you. Type 'accept' or 'decline'.")

    elif cmd == "accept":
        if pdata.get("trade") and pdata["trade"]["stage"] == "incoming":
            other = pdata["trade"]["with"]
            if other not in player_data:
                await conn.send("They're gone.")
                pdata["trade"] = None
                return

            pdata["trade"]["stage"] = "offer"
            player_data[other]["trade"]["stage"] = "offer"
            await conn.send(f"You accepted the trade with {other}.")
            await player_data[other]["conn"].send(f"{username} accepted your trade. You can now type 'offer [item]'.")
        else:
            await conn.send("No trade to accept.")

    elif cmd == "decline":
        if pdata.get("trade") and pdata["trade"]["stage"] == "pending":
            other = pdata["trade"]["with"]
            if other in player_data:
                await player_data[other]["conn"].send(f"{username} declined your trade.")
                player_data[other]["trade"] = None
            pdata["trade"] = None
            await conn.send("You declined the trade.")
        else:
            await conn.send("No trade to decline.")
    elif cmd.startswith("offer "):
        if pdata.get("trade") and pdata["trade"]["stage"] == "offer":
            item = cmd.split(" ", 1)[1]
            if item in pdata.get("inventory", []):
                other = pdata["trade"]["with"]

                pdata["trade"]["item"] = item
                pdata["trade"]["confirmed"] = False
                player_data[other]["trade"]["confirmed"] = False  # Reset theirs too

                await player_data[other]["conn"].send(f"{username} offers you a {item}.Type 'offer [item]' to respond.")
                await conn.send(f"You offered a {item}.")
            else:
                await conn.send("You don't have that item.")
        else:
            await conn.send("You're not in a trade.")
    elif cmd == "confirm":
        if pdata.get("trade") and pdata["trade"]["stage"] == "offer" and "item" in pdata["trade"]:
            pdata["trade"]["confirmed"] = True
            other = pdata["trade"]["with"]

            await conn.send("You confirmed your trade offer.")

            if (player_data[other].get("trade") and
                player_data[other]["trade"].get("confirmed")):
                # Swap items
                your_item = pdata["trade"]["item"]
                their_item = player_data[other]["trade"]["item"]

                pdata["inventory"].remove(your_item)
                pdata["inventory"].append(their_item)

                player_data[other]["inventory"].remove(their_item)
                player_data[other]["inventory"].append(your_item)

                await conn.send(f"Trade completed! You got a {their_item}.")
                await player_data[other]["conn"].send(f"Trade completed! You got a {your_item}.")

                pdata["trade"] = None
                player_data[other]["trade"] = None
            else:
                await conn.send("Waiting on the other player to confirm.")
        else:
            await conn.send("No active trade to confirm.")
    elif cmd == "hp" or cmd == "status" or cmd == "health":
        await conn.send(f"Your current health is {pdata["hp"]}")
    else: 
        await conn.send("Unknown command. Type 'help' for options.")
