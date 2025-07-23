import random
import datetime

# Active player data
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


# NPC rotating dialogues by day of week
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

# Handle incoming commands
async def handle_command(conn, username, data):
    pdata = player_data[username]
    if pdata.get("dialogue"):
        tree = pdata["dialogue"]
        if data in tree["options"]:
            response = tree["options"][data]["response"]
            await conn.send((response + "\n"))
            print(f"[{username}] dialogue response: {response}")
            pdata["dialogue"] = None
        else:
            await conn.send("Invalid choice. Choose a number from the list.\n")
        return

    cmd = data.lower().strip()
    if "in_combat" in pdata and pdata["in_combat"]:
        if cmd == "attack":
            damage = random.randint(3, 6)
            pdata["in_combat"]["enemy_hp"] -= damage
            await conn.send(f"You slash the goblin for {damage} damage!")

            if pdata["in_combat"]["enemy_hp"] <= 0:
                await conn.send("You defeated the goblin! +5 XP")
                pdata["in_combat"] = None
                # Give loot or XP here
            else:
                retaliate = random.randint(1, 4)
                pdata["hp"] -= retaliate
                await conn.send(f"The goblin bites back! You lose {retaliate} HP. You have {pdata['hp']} HP left.")

            return  # skip rest of command handling while in combat
        else:
            await conn.send("You're in combat! Type 'attack' to fight!")
            return

    if cmd == "help":
        await conn.send("Available commands:\n")
        await conn.send("  move north/south/east/west - Move around\n")
        await conn.send("  home - Go to your house\n")
        await conn.send("  talk - Talk to nearby NPCs\n")
        await conn.send("  inventory - View items\n")
        await conn.send("  where - Show location\n")
        await conn.send("  who - List players\n")
        await conn.send("  say [msg] - Say something\n")
        await conn.send("  trade [name] - Start trade\n")
        await conn.send("  help - This list\n")
    elif cmd == "home":
        pdata["pos"] = pdata["house"][:]
        await conn.send("You return home.\n")
    elif cmd == "inventory":
        inv = pdata.get("inventory", [])
        if inv:
            await conn.send(f"You have: {', '.join(inv)}\n")
        else:
            await conn.send("Your inventory is empty.\n")
    elif cmd == "where":
        x, y = pdata["pos"]
        await conn.send(f"You are at ({x}, {y})\n")
        if pdata["pos"] == (15, 20):
            await conn.send("You are in the restaurant.\n")
        elif pdata["pos"] == (10, 20):
            await conn.send("You are in the store.\n")
        elif pdata["pos"] == pdata["house"]:
            await conn.send("You are in your home. Cozy!\n")
    elif cmd == "who":
        names = ", ".join(player_data.keys())
        await conn.send(f"Players online: {names}\n")
    elif cmd.startswith("say "):
        msg = data[4:].strip()
        for other, odata in player_data.items():
            if other != username and odata["pos"] == pdata["pos"]:
                odata["conn"].send(f"{username} says: {msg}\n")
        await conn.send("You said it.\n")
    elif cmd == "talk":
        x, y = pdata["pos"]
        day = str(datetime.datetime.now().weekday())
        npc = None

        if y == pdata["house"][1]:
            await conn.send("You're at your house. No one is home.\n")
            return
        elif x == 10 and y == 20:
            npc = "store"
        elif x == 15 and y == 20:
            npc = "restaurant"

        if npc:
            dialogue = dialogues[npc][day]
            options_text = "\n".join([f"{k}. {v['text']}" for k, v in dialogue["options"].items()])
            await conn.send(f"NPC: {dialogue['prompt']}\n{options_text}\n")
            pdata["dialogue"] = dialogue
        else:
            await conn.send("No one to talk to here.\n")
    elif cmd.startswith("move ") and not cmd[-1].isdigit():
        direction = cmd.split(" ")[1]
        dx, dy = 0, 0
        if direction == "north": dy = 1
        elif direction == "south": dy = -1
        elif direction == "east": dx = 1
        elif direction == "west": dx = -1
        pdata["pos"][0] += dx
        pdata["pos"][1] += dy
        await conn.send(f"You move {direction}.\n")
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
        await conn.send(f"You move {direction} {mult} times.\n")
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
            await conn.send(f"{np}\n")
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
            # Check if close enough
            if abs(pdata["pos"][0] - tdata["pos"][0]) > 5 or abs(pdata["pos"][1] - tdata["pos"][1]) > 5:
                await conn.send("They're too far away to hit.")
            else:
                damage = random.randint(5, 15)
                tdata["hp"] -= damage
                await conn.send(f"You attack {target} for {damage} damage!")
                await tdata["conn"].send(f"{username} attacked you for {damage} damage! You have {tdata['hp']} HP left.")
    else:
        await conn.send("Unknown command. Type 'help' for options.\n")
