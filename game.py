import random
import datetime

player_data = {}


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



dialogues = {

    "store": {
        "0": {
            "prompt": "Welcome to Monday Madness! What do you want?",
            "options": {
                "1": {"text": "Browse axes", "response": "You check out the axe aisle."},
                "2": {"text": "Ask about discounts", "response": "Everything’s 50% off!"},
                "3": {"text": "Leave", "response": "You leave the store."}
            }
        },
        "1": {
            "prompt": "Two-for-one sword Tuesday! What’s your move?",
            "options": {
                "1": {"text": "Inspect swords", "response": "You admire the blades."},
                "2": {"text": "Ask about durability", "response": "These will last you a lifetime."},
                "3": {"text": "Leave", "response": "You leave the store."}
            }
        },
        "2": {
            "prompt": "Wednesday tools special! Need something sturdy?",
            "options": {
                "1": {"text": "Look at pickaxes", "response": "Solid and sharp."},
                "2": {"text": "Ask about farming gear", "response": "Hoes and seeds are in aisle 2."},
                "3": {"text": "Leave", "response": "You exit quietly."}
            }
        },
       "3": {
            "prompt": "Thirsty Thursday — health potions in stock!",
            "options": {
                "1": {"text": "Buy potion", "response": "You grab a potion."},
                "2": {"text": "Ask about effects", "response": "Restores 20 HP instantly."},
                "3": {"text": "Leave", "response": "You wave goodbye to the shopkeeper."}
            }
        },
        "4": {
            "prompt": "Fierce Friday! You need something deadly?",
            "options": {
                "1": {"text": "Look at spears", "response": "A long, lethal beauty."},
                "2": {"text": "Ask about damage stats", "response": "Pierces armor like butter."},
                "3": {"text": "Leave", "response": "You back out slowly."}
            }
        },
        "5": {
            "prompt": "Stock-up Saturday. Grab what you need.",
            "options": {
                "1": {"text": "Buy essentials", "response": "You grab rations and rope."},
                "2": {"text": "Ask about bundles", "response": "3 items for 2 gold."},
                "3": {"text": "Leave", "response": "You step outside."}
            }
        },
        "6": {
            "prompt": "Silent Sunday. No talking — just shopping.",
            "options": {
                "1": {"text": "Buy shovel", "response": "You quietly buy a shovel."},
                "2": {"text": "Browse silently", "response": "You nod at the vendor in silence."},
                "3": {"text": "Leave", "response": "You exit without a word."}
            }
        }
    },



    "restaurant": {
        "0": {
            "prompt": "Monday stew day! Hungry?",
            "options": {
                "1": {"text": "Eat stew", "response": "You eat the stew. +10 HP."},
                "2": {"text": "Ask what’s in it", "response": "Beef, beans, and mystery."},
                "3": {"text": "Leave", "response": "You back away slowly."}
            }
        },
        "1": {
            "prompt": "Taco Tuesday! You in?",
            "options": {
                "1": {"text": "Munch tacos", "response": "You devour the tacos. +10 HP."},
                "2": {"text": "Ask for hot sauce", "response": "It burns, but you feel alive."},
                "3": {"text": "Leave", "response": "You wave goodbye to the cook."}
            }
        },
        "2": {
            "prompt": "Waffle Wednesday! Syrup or nah?",
            "options": {
                "1": {"text": "Eat waffles", "response": "You munch the waffles. +10 HP."},
                "2": {"text": "Ask about toppings", "response": "We got syrup, berries, and magic."},
                "3": {"text": "Leave", "response": "You leave, still hungry."}
            }
        },
        "3": {
            "prompt": "Thirsty Thursday — drinks on deck.",
            "options": {
                "1": {"text": "Sip juice", "response": "Fresh and fruity. +10 HP."},
                "2": {"text": "Ask for tea", "response": "Herbal, calming, very warm."},
                "3": {"text": "Leave", "response": "You pass on the drinks."}
            }
        },
        "4": {
            "prompt": "Fish Fry Friday! Fried or grilled?",
            "options": {
                "1": {"text": "Eat fried trout", "response": "Crispy, flaky, delicious. +10 HP."},
                "2": {"text": "Ask for grilled", "response": "Outta stock! Fried only."},
                "3": {"text": "Leave", "response": "You slide out the back door."}
            }
        },
        "5": {
            "prompt": "Spaghetti Saturday. You ready for carbs?",
            "options": {
                "1": {"text": "Twirl pasta", "response": "You slurp spaghetti. +10 HP."},
                "2": {"text": "Ask for garlic bread", "response": "One slice coming up."},
                "3": {"text": "Leave", "response": "You tip your hat and walk away."}
            }
        },
        "6": {
            "prompt": "Soup & Silence Sunday. Speak only with slurps.",
            "options": {
                "1": {"text": "Eat soup", "response": "You quietly eat soup. +10 HP."},
                "2": {"text": "Ask for seconds", "response": "Soup is sacred. One bowl only."},
                "3": {"text": "Leave", "response": "You vanish into the quiet fog."}
            }
        }
    }





}

async def handle_command(conn, username, data):
    pdata = player_data[username]

    if pdata.get("dialogue"):
        tree = pdata["dialogue"]
        if data in tree["options"]:
            response = tree["options"][data]["response"]
            await conn.send((response + ""))
            print(f"[{username}] dialogue response: {response}")
            pdata["dialogue"] = None
        else:
            await conn.send("Invalid choice. Choose a number from the list.")
        return

    cmd = data.lower().strip()
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
        x, y = pdata["pos"]
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
        x, y = pdata["pos"]
        day = str(datetime.datetime.now().weekday())
        npc = None

        if y == pdata["house"][1]:
            await conn.send("You're at your house. No one is home.")
            return
        elif x == 10 and y == 20:
            npc = "store"
        elif x == 15 and y == 20:
            npc = "restaurant"

        if npc:
            dialogue = dialogues[npc][day]
            options_text = "".join([f"{k}. {v['text']}" for k, v in dialogue["options"].items()])
            await conn.send(f"NPC: {dialogue['prompt']}{options_text}")
            pdata["dialogue"] = dialogue
        else:
            await conn.send("No one to talk to here.")
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
        if pdata["pos"][0] >=40 and pdata["pos"][0] <=44 and pdata["pos"][1] >= 32 and pdata["pos"][1] <= 35:
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
        if pdata["pos"][0] >=40 and pdata["pos"][0] <=44 and pdata["pos"][1] >= 32 and pdata["pos"][1] <= 35:
            await conn.send("You are in the cave now. A green, rotten goblin attacks!")
            pdata["hp"] = pdata["hp"] - random.randint(1, 5)
            goblin_hp = 10
            await conn.send("Type 'attack' to fight the goblin!")

            pdata["in_combat"] = {
                "enemy": "goblin",
                "enemy_hp": goblin_hp
            }
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
            if abs(pdata["pos"][0] - tdata["pos"][0]) > 5 or abs(pdata["pos"][1] - tdata["pos"][1]) > 5:
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
        elif 30 <= pdata["pos"][0] <= 35 and 35 <= pdata["pos"][1] <= 40:
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
        elif abs(pdata["pos"][0] - player_data[target]["pos"][0]) > 5 or abs(pdata["pos"][1] - player_data[target]["pos"][1]) > 5:
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

    else:
        await conn.send("Unknown command. Type 'help' for options.")
