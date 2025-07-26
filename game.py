# setup
import random
import datetime
import time
player_data = {}

LOGFILE = "log.txt"

def drunkify(text: str) -> str:
    words = text.split()
    if len(words) < 3:
        return text
    # 50/50: fully reverse or shuffle, just to keep it goofy
    if random.random() < 0.5:
        return " ".join(reversed(words))
    random.shuffle(words)
    return " ".join(words)

async def dsend(conn, pdata, text: str):
    if "drunk" in pdata.get("effects", []):
        text = drunkify(text)
    await conn.send(text)
    #-------------------DELETE OR COMMENT THESE LINES TO DISABLE LOGGING-------------------
    output_print = f'output from {pdata["username"]}: "{text}"'
    print(output_print)
    with open(LOGFILE, "a", encoding="utf-8") as l:
        l.write(output_print + "\n")
    #-------------------DELETE OR COMMENT THESE LINES TO DISABLE LOGGING-------------------
    

def tick_effects(pdata):
    # make sure these exist
    pdata.setdefault("effects", [])
    pdata.setdefault("effect_turn", 0)

    if "drunk" in pdata["effects"]:
        pdata["effect_turn"] += 1
        if pdata["effect_turn"] >= 5:
            pdata["effects"].remove("drunk")
            pdata["effect_turn"] = 0
            return "You feel sober again."
    return None


# nearby
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

# dialogue
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

async def send_node(conn, tree_id, node_id, pdata):
    node = DIALOGUE_TREES[tree_id][node_id]
    prompt = fmt(node["prompt"], pdata)
    opts = "\n".join(f"{k}. {fmt(v['text'], pdata)}" for k, v in node["options"].items())
    await dsend(conn, pdata, f"{prompt}\n{opts}\n")

def start_dialogue(pdata, tree_id, node_id="root"):
    pdata["dialogue"] = {"tree": tree_id, "node": node_id}

async def advance_dialogue(conn, pdata, choice):
    dlg = pdata["dialogue"]
    tree = DIALOGUE_TREES[dlg["tree"]]
    node = tree[dlg["node"]]

    if choice not in node["options"]:
        await dsend(conn, pdata, "Invalid choice. Pick a number from the list.")
        return

    opt = node["options"][choice]

    if evt := opt.get("event"):
        handler = EVENTS.get(evt)
        if handler:
            await handler(conn, pdata)


    if opt.get("end"):
        pdata["dialogue"] = None
        await dsend(conn, pdata, "You leave the conversation.")
        return

    next_node = opt["next"]
    dlg["node"] = next_node
    await send_node(conn, dlg["tree"], next_node, pdata)

#  events
async def ev_buy_sword(conn, pdata):
    if pdata["gp"] >= .5:
        pdata["inventory"].append("sword")
        await dsend(conn, pdata, "You received a sword!")
        pdata["gp"] -= .5
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")

async def ev_buy_shield(conn, pdata):
    if pdata["gp"] >= .3:
        pdata["inventory"].append("shield")
        await dsend(conn, pdata, "You got a shield!")
        pdata["gp"] -= .3
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")

async def ev_buy_toast(conn, pdata):
    if pdata["gp"] >= .1:
        pdata["inventory"].append("toast")
        await dsend(conn, pdata, "You got a toast!")
        pdata["gp"] -= .1
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")

async def ev_buy_ale(conn, pdata):
    if pdata["gp"] >= .05:
        pdata["inventory"].append("ale")
        await dsend(conn, pdata, "You got some ale!")
        pdata["gp"] -= .05
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")

async def ev_sell_egg(conn, pdata):
    if "golden egg" in pdata["inventory"]:
        pdata["inventory"].remove("golden egg")
        await dsend(conn, pdata, '"Looks like a counterfeit there. Have 5 gold coins for your trouble anyways."')
        pdata["gp"] += 5
    else:
        await dsend(conn, pdata, '"What golden egg? Are ya a lunatic?!" The shopkeeper punches you in the face. (-5 hp)')
        pdata["hp"] -= 5

async def ev_sell_sword(conn, pdata):
    if "sword" in pdata["inventory"]:
        pdata["inventory"].remove("sword")
        await dsend(conn, pdata, '"There\'s your cash. Don\'t spend it all in one place!"')
        pdata["gp"] += .3
    else:
        await dsend(conn, pdata, '"What sword? Are ya crazy?!" The shopkeeper socks you in the face. (-7 hp)')
        pdata["hp"] -= 7

async def ev_sell_shield(conn, pdata):
    if "shield" in pdata["inventory"]:
        pdata["inventory"].remove("shield")
        await dsend(conn, pdata, '"Here\'s your money. Spend it all in one place."')
        pdata["gp"] += .2
    else:
        await dsend(conn, pdata, '"What shield? Are ya stupid?!" The shopkeeper roundhouse kicks you in the face. (-15 hp)')
        pdata["hp"] -= 15

async def ev_buy_vodka(conn, pdata):
    if pdata["gp"] >= .1:
        pdata["inventory"].append("vodka")
        await dsend(conn, pdata, "You got a shot of vodka!")
        pdata["gp"] -= .1
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")

async def ev_buy_martini(conn, pdata):
    if pdata["gp"] >= .15:
        pdata["inventory"].append("martini")
        await dsend(conn, pdata, "You got a martini!")
        pdata["gp"] -= .15
    else:
        await dsend(conn, pdata, "Unfortunately, you do not have the money for that.")



BLACKS = {28, 26, 11, 20, 17, 22, 15, 24, 13, 10, 29, 8, 31, 6, 33, 4, 35, 2}
REDS   = {9, 30, 7, 32, 5, 34, 3, 36, 1, 27, 25, 12, 19, 18, 21, 16, 14}

async def ev_play_roulette(conn, pdata):
    result = random.randint(0, 36)
    color = "green" if result == 0 else ("black" if result in BLACKS else "red")

    # --- get a valid bet ---
    while True:
        await dsend(conn, pdata, f'How much would you like to bet? (You have {pdata["gp"]} gold coins.)')
        try:
            bet = float(await conn.recv())
        except ValueError:
            await dsend(conn, pdata, "Number only, fam.")
            continue

        if 0 < bet <= pdata["gp"]:
            break
        await dsend(conn, pdata, f"Bet must be between 0 and {pdata['gp']}.")

    # --- get bet type ---
    await dsend(conn, pdata, "What would you like to bet on? (number/color)")
    bettype = (await conn.recv()).strip().lower()
    while bettype not in {"number", "num", "color"}:
        await dsend(conn, pdata, "Type 'number' or 'color'.")
        bettype = (await conn.recv()).strip().lower()

    if bettype in {"number", "num"}:
        await dsend(conn, pdata, "What number would you like to bet on? (0-36)")
        try:
            finalbet = int(await conn.recv())
        except ValueError:
            await dsend(conn, pdata, "Not a number. You lose by default.")
            pdata["gp"] -= bet
            return

        if finalbet == result:
            pdata["gp"] += bet * 35  # standard roulette payout
            await dsend(conn, pdata, f"Hit! Ball landed on {result} {color}. You won {bet*35} gold coins!")
        else:
            pdata["gp"] -= bet
            await dsend(conn, pdata, f"Miss. Ball landed on {result} {color}. You lost {bet} gold coins.")
    else:
        await dsend(conn, pdata, "Red or black?")
        chosen = (await conn.recv()).strip().lower()
        if chosen not in {"red", "black"}:
            await dsend(conn, pdata, "Invalid color. You lose by default.")
            pdata["gp"] -= bet
            return

        if chosen == color:
            pdata["gp"] += bet
            await dsend(conn, pdata, f"Nice! It was {color} ({result}). You won {bet} gold coins!")
        else:
            pdata["gp"] -= bet
            await dsend(conn, pdata, f"Nah, it was {color} ({result}). You lost {bet} gold coins.")




SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def _new_deck():
    deck = [(r, s) for s in SUITS for r in RANKS] * 4
    random.shuffle(deck)
    return deck

def _hand_value(hand):
    total = 0
    aces = 0
    for r, _ in hand:
        if r == "A":
            total += 11
            aces += 1
        elif r in ("J", "Q", "K"):
            total += 10
        else:
            total += int(r)
    # soft → hard conversion
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def _is_blackjack(hand):
    return len(hand) == 2 and _hand_value(hand) == 21

def _fmt_hand(hand):
    return " ".join([f"[{r}{s}]" for r, s in hand]) + f"  (={_hand_value(hand)})"

async def ev_play_blackjack(conn, pdata):
    # ------- bet -------
    while True:
        await dsend(conn, pdata, f"How much do you want to bet? (You have {pdata.get('gp', 0):.2f} gp)")
        try:
            bet = float(await conn.recv())
        except ValueError:
            await dsend(conn, pdata, "Numbers only.\n")
            continue
        if 0 < bet <= pdata.get("gp", 0):
            break
        await dsend(conn, pdata, f"Bet must be between 0 and {pdata.get('gp', 0):.2f}.\n")

    deck = _new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    await dsend(conn, pdata, f"Your hand:   {_fmt_hand(player)}\n")
    await dsend(conn, pdata, f"Dealer shows [{dealer[0][0]}{dealer[0][1]}] and a facedown card.\n")

    # Natural blackjacks
    player_bj = _is_blackjack(player)
    dealer_bj = _is_blackjack(dealer)
    if player_bj or dealer_bj:
        await dsend(conn, pdata, f"Dealer hand: {_fmt_hand(dealer)}\n")
        if player_bj and dealer_bj:
            await dsend(conn, pdata, "Push. You get your bet back.\n")
        elif player_bj:
            win = bet * 1.5
            pdata["gp"] += win
            await dsend(conn, pdata, f"Blackjack! You win {win:.2f} gp.\n")
        else:
            pdata["gp"] -= bet
            await dsend(conn, pdata, f"Dealer blackjack. You lose {bet:.2f} gp.\n")
        return

    # ------- player turn -------
    while True:
        if _hand_value(player) > 21:
            await dsend(conn, pdata, f"You bust with {_fmt_hand(player)}. You lose {bet:.2f} gp.\n")
            pdata["gp"] -= bet
            return

        await dsend(conn, pdata, "Hit or stand? (h/s)")
        choice = (await conn.recv()).strip().lower()
        if choice in ("h", "hit"):
            player.append(deck.pop())
            await dsend(conn, pdata, f"Your hand: {_fmt_hand(player)}\n")
            continue
        elif choice in ("s", "stand"):
            break
        else:
            await dsend(conn, pdata, "Type 'h' or 's'.\n")

    # ------- dealer turn -------
    await dsend(conn, pdata, f"Dealer reveals: {_fmt_hand(dealer)}\n")
    while _hand_value(dealer) < 17:
        dealer.append(deck.pop())
        await dsend(conn, pdata, f"Dealer hits: {_fmt_hand(dealer)}\n")

    p_total = _hand_value(player)
    d_total = _hand_value(dealer)

    # ------- resolve -------
    if d_total > 21:
        pdata["gp"] += bet
        await dsend(conn, pdata, f"Dealer busts with {d_total}. You win {bet:.2f} gp!\n")
    elif p_total > d_total:
        pdata["gp"] += bet
        await dsend(conn, pdata, f"You win! {p_total} vs {d_total}. +{bet:.2f} gp.\n")
    elif p_total < d_total:
        pdata["gp"] -= bet
        await dsend(conn, pdata, f"You lose. {p_total} vs {d_total}. -{bet:.2f} gp.\n")
    else:
        await dsend(conn, pdata, "Push. Your bet is returned.\n")

import random, itertools

VAL    = {r:i for i,r in enumerate(RANKS, start=2)}  # 2..14

def _fmt(cards):
    return " ".join(f"[{r}{s}]" for r,s in cards)

def _hand_rank5(cards5):
    # returns (category, tiebreakers...)  higher is better
    ranks = sorted([VAL[r] for r,_ in cards5], reverse=True)
    suits = [s for _,s in cards5]
    flush = len(set(suits)) == 1

    # handle straight (incl. wheel A-2-3-4-5)
    def straight_val(vals):
        uniq = sorted(set(vals), reverse=True)
        # wheel
        if set([14, 5, 4, 3, 2]).issubset(set(vals)):
            return 5
        for i in range(len(uniq)-4):
            if uniq[i] - uniq[i+4] == 4:
                return uniq[i]
        return 0
    sv = straight_val(ranks)

    from collections import Counter
    cnt = Counter(ranks).most_common()  # [(rank,count)..] ordered by count desc then rank desc
    cnt.sort(key=lambda x:(x[1], x[0]), reverse=True)
    counts = [c for _,c in cnt]
    ordered = [r for r,_ in cnt for _ in range(_)]

    if sv and flush:  # straight flush
        return (8, sv)
    if counts == [4,1]:
        return (7, cnt[0][0], ordered)
    if counts == [3,2]:
        return (6, cnt[0][0], cnt[1][0], ordered)
    if flush:
        return (5, ordered)
    if sv:
        return (4, sv, ordered)
    if counts == [3,1,1]:
        return (3, cnt[0][0], ordered)
    if counts == [2,2,1]:
        pair_vals = sorted([cnt[0][0], cnt[1][0]], reverse=True)
        return (2, pair_vals, ordered)
    if counts == [2,1,1,1]:
        return (1, cnt[0][0], ordered)
    return (0, ordered)

def _best_rank7(cards7):
    best = None
    for comb in itertools.combinations(cards7, 5):
        r = _hand_rank5(comb)
        if (best is None) or (r > best[0]):
            best = (r, comb)
    return best  # (rank_tuple, best5cards)

async def ev_play_holdem(conn, pdata):
    # --- bet ---
    while True:
        await dsend(conn, pdata, f"Hold'em! Bet amount? (You have {pdata.get('gp',0):.2f} gp)")
        try:
            bet = float(await conn.recv())
        except ValueError:
            await dsend(conn, pdata, "Numbers only.")
            continue
        if 0 < bet <= pdata.get("gp",0):
            break
        await dsend(conn, pdata, f"Bet must be between 0 and {pdata.get('gp',0):.2f}.")

    deck = _new_deck()
    you    = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    board  = []

    await dsend(conn, pdata, f"Your hand: {_fmt(you)}")
    await dsend(conn, pdata, f"Dealer shows [{dealer[0][0]}{dealer[0][1]}] [?]")

    async def ask_continue(stage):
        await dsend(conn, pdata, f"{stage}: check or fold? (c/f)")
        a = (await conn.recv()).strip().lower()
        if a in ("f","fold"):
            pdata["gp"] -= bet
            await dsend(conn, pdata, f"You folded. -{bet:.2f} gp")
            return False
        return True

    # Preflop decision
    if not await ask_continue("Preflop"):
        return

    # Flop
    board += [deck.pop(), deck.pop(), deck.pop()]
    await dsend(conn, pdata, f"Flop: {_fmt(board)}")
    if not await ask_continue("Flop"):
        return

    # Turn
    board += [deck.pop()]
    await dsend(conn, pdata, f"Turn: {_fmt(board)}")
    if not await ask_continue("Turn"):
        return

    # River
    board += [deck.pop()]
    await dsend(conn, pdata, f"River: {_fmt(board)}")

    # Showdown
    await dsend(conn, pdata, f"Dealer hand: {_fmt(dealer)}")

    yrank, ybest = _best_rank7(you + board)
    drank, dbest = _best_rank7(dealer + board)

    if yrank > drank:
        pdata["gp"] += bet
        await dsend(conn, pdata, f"You win! (+{bet:.2f} gp)")
    elif yrank < drank:
        pdata["gp"] -= bet
        await dsend(conn, pdata, f"You lose. (-{bet:.2f} gp)")
    else:
        await dsend(conn, pdata, "Push. Bet returned.")


# events
EVENTS = {
    "buy_sword": ev_buy_sword,
    "buy_shield": ev_buy_shield,
    "buy_ale": ev_buy_ale,
    "buy_ale": ev_buy_ale,
    "sell_golden_egg": ev_sell_egg,
    "sell_sword": ev_sell_sword,
    "sell_shield": ev_sell_shield,
    "buy_vodka": ev_buy_vodka,
    "buy_martini": ev_buy_martini,
    "play_roulette": ev_play_roulette,
    "play_blackjack": ev_play_blackjack,
    "play_holdem": ev_play_holdem,
}


# main dialogue trees
DIALOGUE_TREES = {
    # shopkeeper
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

    # server
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
                "1": {"text": "I'll take some toast.", "event": "buy_ale" , "end": True},
                "2": {"text": "How about some ale?", "event": "buy_ale", "end": True},
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
        },
    },
    
    #dealer
    "dealer": {
        "root": {
            "prompt": '"Welcome to Shelly\'s casino! What would you like to do?"',
            "options": {
                "1": {"text": "What kind of game's do you guys have?", "next": "node2"},
                "2": {"text": "Could I get something at the bar?", "next": "node3"},
                "3": {"text": "Leave.", "end": True}
            }
        },
        "node2": {
            "prompt": '"We\'ve got roulette, blackjack, and texas hold\'em. How\'s about it?"',
            "options": {
                "1": {"text": "Roulette, please.", "next": "node5"},
                "2": {"text": "Blackjack, thank you.", "next": "node6"},
                "3": {"text": "Hold'em.", "next": "node7"},
                "4": {"text": "Leave.", "end": True}
            }
        },
        "node3": {
            "prompt": '"Sure! Go and talk to the bartender about that."',
            "options": {
                "1": {"text": "Just a shot of vodka. (-0.1 gold coins)", "event": "buy_vodka", "next": "node4"},
                "2": {"text": "I'll take a martini. (-0.15 gold coins)", "event": "buy_martini", "next": "node4"},
                "3": {"text": "I'll have a pint of ale, please. (-0.05 gold coins)", "event": "buy_ale", "next": "node4"},
                "4": {"text": "Leave.", "end": True}
            }
        },
        "node4": {
            "prompt": '"Thank you. Is that all, or would you like to play a game?"',
            "options": {
                "1": {"text": "I think that's all. (Leave)", "end": True},
                "2": {"text": "You know what? I'll play a game.", "next": "node2"},
                "3": {"text": "Leave without saying a word.", "end": True}
            }
        },
        "node5": {
            "prompt": '"Amazing! Let\'s spin the wheel!."',
            "options": {
                "1": {"text": "Sound's good!", "event": "play_roulette", "next": "node8"},
                "2": {"text": "On second thought, I'm going to leave. (Leave)", "end": True}
            }
        },
        "node6": {
            "prompt": '"Wonderful! Let\'s deal the cards for blackjack!."',
            "options": {
                "1": {"text": "Sound's good!", "event": "play_blackjack", "next": "node8"},
                "2": {"text": "On second thought, I'm going to leave. (Leave)", "end": True}
            }
        },
        "node7": {
            "prompt": '"Great! Let\'s deal the cards for Hold\'em."',
            "options": {
                "1": {"text": "Sound's good!", "event": "play_holdem", "next": "node8"},
                "2": {"text": "On second thought, I'm going to leave. (Leave)", "end": True}
            }
        },
        "node8": {
            "prompt": '"Done with the games, or would you like to play something else?"',
            "options": {
                "1": {"text": "I think I'm done for now. (Leave)", "end": True},
                "2": {"text": "Actually, can I get a drink now?", "next": "node3"},
                "3": {"text": "No, let's keep playing! What games again?", "next": "node2"}
            }
        }
    }
}

# command handling
async def handle_command(conn, username, data):




    pdata = player_data[username]

    msg = tick_effects(pdata)   # <-- no await, and WITH parentheses
    if msg:
        await conn.send(msg)

    x, y = pdata["pos"]

    #hp and levels

    if pdata["hp"] > 100:
        pdata["hp"] = 100
    
    if pdata["xp"] >= 10 and pdata["xp"] < 30:
        if pdata["level"] == 1:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1
    elif pdata["xp"] >= 30 and pdata["xp"] < 100:
        if pdata["level"] == 2:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1
    elif pdata["xp"] >= 100 and pdata["xp"] < 500:
        if pdata["level"] == 3:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1
    elif pdata["xp"] >= 500 and pdata["xp"] < 2000:
        if pdata["level"] == 4:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1
    elif pdata["xp"] >= 2000 and pdata["xp"] < 10000:
        if pdata["level"] == 5:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1
    elif pdata["xp"] >= 10000 and pdata["xp"] < 50000:
        if pdata["level"] == 6:
            await dsend(conn, pdata, f"Level up! You are now level {pdata[level]}.")
            pdata["level"] += 1


    cmd = data.lower().strip()
    cmd_raw = data.strip()

    # dialogue check (make sure player isn't in dialogue)(KEEP HERE)
    if pdata.get("dialogue"):
        if cmd.isdigit():
            await advance_dialogue(conn, pdata, cmd)
        else:
            await dsend(conn, pdata, "You're in a convo. Choose a number.")
        return
    await dsend(conn, pdata, f">{data.strip()}")

    # combat check (carry out combat)(KEEP HERE)
    if "in_combat" in pdata and pdata["in_combat"]:
        if cmd == "attack":
            damage = random.randint(3, 6)
            pdata["in_combat"]["enemy_hp"] -= damage
            await dsend(conn, pdata, f"You slash the goblin for {damage} damage!")

            if pdata["in_combat"]["enemy_hp"] <= 0:
                xp = random.randint(3,7)
                await dsend(conn, pdata, "You defeated the goblin! +", xp, " XP")
                pdata["in_combat"] = None
                pdata["xp"] += xp
            else:
                retaliate = random.randint(1, 4)
                pdata["hp"] -= retaliate
                await dsend(conn, pdata, f"The goblin bites back! You lose {retaliate} HP. You have {pdata['hp']} HP left.")

            return
        else:
            await dsend(conn, pdata, "You're in combat! Type 'attack' to fight!")
            return

    # help (display help message)
    if cmd == "help":
        await dsend(conn, pdata, "Available commands:")
        await dsend(conn, pdata, "  move/go north/south/east/west - Move around.")
        await dsend(conn, pdata, "  home - Go to your house.")
        await dsend(conn, pdata, "  talk - Talk to nearby NPCs.")
        await dsend(conn, pdata, "  say [msg] - Say something to other players.")
        await dsend(conn, pdata, "  inventory - View items.")
        await dsend(conn, pdata, "  xp - Display your experience points.")
        await dsend(conn, pdata, "  hp - Display health.")
        await dsend(conn, pdata, "  where - Show location.")
        await dsend(conn, pdata, "  who - List players.")
        await dsend(conn, pdata, "  trade [name] - Start trade with a nearby player.")
        await dsend(conn, pdata, "  attack [name] - Attack a nearby player.")
        await dsend(conn, pdata, "  attack - Attack a nearby mob, if available.")
        await dsend(conn, pdata, "  nearby - List nearby players.")
        await dsend(conn, pdata, "  map - display a map of the land!")
        await dsend(conn, pdata, "  help - This list.")

    # home (teleport home)
    elif cmd == "home":
        pdata["pos"] = pdata["house"][:]
        await dsend(conn, pdata, "You return home.")
    
    # inv (see your inventory)
    elif cmd == "inventory" or cmd == "inv":
        if pdata["inventory"]:
            await dsend(conn, pdata, "You have:")
            for item in pdata["inventory"]:
                await dsend(conn, pdata, f"  {item}")
        else:
            await dsend(conn, pdata, "Your inventory is empty.")

    # where (see where you are)
    elif cmd == "where":
        await dsend(conn, pdata, f"You are at ({x}, {y})")
        if x == 15 and y == 20:
            await dsend(conn, pdata, "You are in the restaurant.")
        elif x == 10 and y == 20:
            await dsend(conn, pdata, "You are in the store.")
        elif x == 20 and y == 20:
            await dsend(conn, pdata, "You are in the casino.")
        elif pdata["pos"] == pdata["house"]:
            await dsend(conn, pdata, "You are in your home. Cozy!")
        elif x >= 30 and x <=35 and y >= 35 and y <= 40:
            await dsend(conn, pdata, "You are in the forest. Perhaps there is some treasure nearby?")

    # who (see who's online)
    elif cmd == "who":
        names = ", ".join(player_data.keys())
        await dsend(conn, pdata, f"Players online: {names}")

    # say (talk to players)
    elif cmd.startswith("say "):
        msg = data[4:].strip()
        for other, odata in player_data.items():
            if other != username:
                await odata["conn"].send(f"{username} says: {msg}")
        await dsend(conn, pdata, "You said it.")

    # talk (talk to npc)
    elif cmd == "talk":
        if [x, y] == [10, 20]:
            start_dialogue(pdata, "shopkeeper")
            await send_node(conn, "shopkeeper", "root", pdata)
        if [x, y] == [15, 20]:
            start_dialogue(pdata, "server")
            await send_node(conn, "server", "root", pdata)
        if [x, y] == [20, 20]:
            start_dialogue(pdata, "dealer")
            await send_node(conn, "dealer", "root", pdata)

    # move (move 1 unit in the given direction)
    elif cmd.startswith("move ") and not cmd[-1].isdigit():
        direction = cmd.split(" ")[1]
        dx, dy = 0, 0
        if direction == "north": dy = 1
        elif direction == "south": dy = -1
        elif direction == "east": dx = 1
        elif direction == "west": dx = -1
        pdata["pos"][0] += dx
        pdata["pos"][1] += dy
        await dsend(conn, pdata, f"You move {direction}.")
        if x >=40 and x <=44 and pdata["pos"][1] >= 32 and pdata["pos"][1] <= 35:
            await dsend(conn, pdata, "You are in the cave now. A green, rotten goblin attacks!")
            pdata["hp"] = pdata["hp"] - random.randint(1, 5)
            goblin_hp = 10
            await dsend(conn, pdata, "Type 'attack' to fight the goblin!")

            pdata["in_combat"] = {
                "enemy": "goblin",
                "enemy_hp": goblin_hp
            }

    # move (move given number of units in given direction)
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
        await dsend(conn, pdata, f"You move {direction} {mult} times.")
        if x >=40 and x <=44 and pdata["pos"][1] >= 30 and pdata["pos"][1] <= 34:
            await dsend(conn, pdata, "You are in the cave now. A green, rotten goblin attacks!")
            pdata["hp"] = pdata["hp"] - random.randint(1, 5)
            goblin_hp = 10
            await dsend(conn, pdata, "Type 'attack' to fight the goblin!")

            pdata["in_combat"] = {
                "enemy": "goblin",
                "enemy_hp": goblin_hp
            }
        if x >= 35 and x <= 40 and y >= 40 and y <= 45:
            await dsend(conn, pdata, "You are home.")

    # nearby (display nearby players)
    elif cmd == "nearby":
        np = nearby_players(pdata["username"])
        if np:
            await dsend(conn, pdata, f"{np}")
        else:
            await dsend(conn, pdata, "There's nobody nearby.")

    # attack (attack given player)
    elif cmd.startswith("attack "):
        target = cmd.split(" ", 1)[1]
        if target not in player_data:
            await dsend(conn, pdata, "No such player.")
        elif target == username:
            await dsend(conn, pdata, "You can't attack yourself, weirdo.")
        else:
            tdata = player_data[target]
            if abs(x - tdata["pos"][0]) > 5 or abs(pdata["pos"][1] - tdata["pos"][1]) > 5:
                await dsend(conn, pdata, "They're too far away to hit.")
            else:
                damage = random.randint(5, 15)
                tdata["hp"] -= damage
                await dsend(conn, pdata, f"You attack {target} for {damage} damage!")
                await tdata["conn"].send(f"{username} attacked you for {damage} damage! You have {tdata['hp']} HP left.")
    elif cmd.startswith("climb"):
        pdata.setdefault("climbcount", 0)

        #  check for golden egg first
        if pdata["pos"] == pdata["eggpos"] and pdata["goldeggexist"]:
            await dsend(conn, pdata, "You climb the tree, and up there lays a golden egg!")
            return  #  stop here

        #  forest climb
        elif 30 <= x <= 35 and 35 <= pdata["pos"][1] <= 40:
            pdata["climbcount"] += 1
            if pdata["climbcount"] >= 10:
                await dsend(conn, pdata, f"Maybe you should check {pdata['eggpos']}?")
                pdata["climbcount"] = 0
            else:
                await dsend(conn, pdata, "You climb the tree. Not much to see, but you feel special up here.")

        else:
            await dsend(conn, pdata, "There's nothing here to climb.")

    # take (take something nearby)
    elif cmd.startswith("take") or cmd.startswith("grab"):
        if tuple(pdata["pos"]) == tuple(pdata.get("eggpos", ())) and pdata.get("goldeggexist"):
            await dsend(conn, pdata, "You take the golden egg! +10 gold.")
            pdata.setdefault("inventory", []).append("golden egg")
            pdata["goldeggexist"] = False
        else:
            await dsend(conn, pdata, "There's nothing here to take.")

    # trade (trade something with a given player)
    elif cmd.startswith("trade "):
        target = cmd.split(" ", 1)[1]
        if target not in player_data:
            await dsend(conn, pdata, "No such player.")
        elif target == username:
            await dsend(conn, pdata, "You can't trade with yourself.")
        elif abs(x - player_data[target]["pos"][0]) > 5 or abs(pdata["pos"][1] - player_data[target]["pos"][1]) > 5:
            await dsend(conn, pdata, "They're too far away to trade.")
        elif player_data[target].get("trade"):
            await dsend(conn, pdata, "They're already in a trade!")
        else:
            pdata["trade"] = {"with": target, "stage": "pending"}
            player_data[target]["trade"] = {"with": username, "stage": "incoming"}
            player_data[target]["trade_request"] = username  #  🛠️ Add this line
            await dsend(conn, pdata, f"You offered to trade with {target}.")
            await player_data[target]["conn"].send(f"{username} wants to trade with you. Type 'accept' or 'decline'.")

    # accept (trade)
    elif cmd == "accept":
        if pdata.get("trade") and pdata["trade"]["stage"] == "incoming":
            other = pdata["trade"]["with"]
            if other not in player_data:
                await dsend(conn, pdata, "They're gone.")
                pdata["trade"] = None
                return

            pdata["trade"]["stage"] = "offer"
            player_data[other]["trade"]["stage"] = "offer"
            await dsend(conn, pdata, f"You accepted the trade with {other}.")
            await player_data[other]["conn"].send(f"{username} accepted your trade. You can now type 'offer [item]'.")
        else:
            await dsend(conn, pdata, "No trade to accept.")
    
    # decline (trade)
    elif cmd == "decline":
        if pdata.get("trade") and pdata["trade"]["stage"] == "pending":
            other = pdata["trade"]["with"]
            if other in player_data:
                await player_data[other]["conn"].send(f"{username} declined your trade.")
                player_data[other]["trade"] = None
            pdata["trade"] = None
            await dsend(conn, pdata, "You declined the trade.")
        else:
            await dsend(conn, pdata, "No trade to decline.")

    # offer (trade)
    elif cmd.startswith("offer "):
        if pdata.get("trade") and pdata["trade"]["stage"] == "offer":
            item = cmd.split(" ", 1)[1]
            if item in pdata.get("inventory", []):
                other = pdata["trade"]["with"]

                pdata["trade"]["item"] = item
                pdata["trade"]["confirmed"] = False
                player_data[other]["trade"]["confirmed"] = False  #  Reset theirs too

                await player_data[other]["conn"].send(f"{username} offers you a {item}.Type 'offer [item]' to respond.")
                await dsend(conn, pdata, f"You offered a {item}.")
            else:
                await dsend(conn, pdata, "You don't have that item.")
        else:
            await dsend(conn, pdata, "You're not in a trade.")

    # confirm (trade)
    elif cmd == "confirm":
        if pdata.get("trade") and pdata["trade"]["stage"] == "offer" and "item" in pdata["trade"]:
            pdata["trade"]["confirmed"] = True
            other = pdata["trade"]["with"]

            await dsend(conn, pdata, "You confirmed your trade offer.")

            if (player_data[other].get("trade") and
                player_data[other]["trade"].get("confirmed")):
                #  Swap items
                your_item = pdata["trade"]["item"]
                their_item = player_data[other]["trade"]["item"]

                pdata["inventory"].remove(your_item)
                pdata["inventory"].append(their_item)

                player_data[other]["inventory"].remove(their_item)
                player_data[other]["inventory"].append(your_item)

                await dsend(conn, pdata, f"Trade completed! You got a {their_item}.")
                await player_data[other]["conn"].send(f"Trade completed! You got a {your_item}.")

                pdata["trade"] = None
                player_data[other]["trade"] = None
            else:
                await dsend(conn, pdata, "Waiting on the other player to confirm.")
        else:
            await dsend(conn, pdata, "No active trade to confirm.")
    
    # hp (display hp)
    elif cmd == "hp" or cmd == "health":
        hp = pdata["hp"]
        await dsend(conn, pdata, f"Your current health is {hp}")
        if hp >= 85:
            await dsend(conn, pdata, "You are healthy.")
        elif hp >= 60 and hp < 85:
            await dsend(conn, pdata, "You're doing alright. Maybe eat some toast.")
        elif hp >= 30 and hp < 60:
            await dsend(conn, pdata, "You might want to get to the hospital.")
        elif hp < 30:
            await dsend(conn, pdata, "You definitely need some help.")
        else:
            print(f"{username} has a messed up hp! Their hp is {hp}")
            await dsend(conn, pdata, "You're health is...weird...")

    # xp (display xp)
    elif cmd == "xp" or cmd == "exp" or cmd == "level":
        await dsend(conn, pdata, f"Your current XP is {pdata["xp"]}")
        await dsend(conn, pdata, f"Your level is {pdata["level"]}")

    # gp (display gp)
    elif cmd == "gp" or cmd == "gold" or cmd == "money":
        gp = pdata["gp"]
        await dsend(conn, pdata, f"You currently have {gp} gold points.")
        if gp < 5:
            await dsend(conn, pdata, "You're kind of broke.")
        elif gp >= 5:
            await dsend(conn, pdata, "You've got some money.")
        elif gp >= 20:
            await dsend(conn, pdata, "You're getting up there.")
        elif gp >= 100:
            await dsend(conn, pdata, "You're rich!")
        elif gp >= 1000:
            await dsend(conn, pdata, "Holy sh.. You're the richest person I've met.")
        else:
            await dsend(conn, pdata, "You're gold is...weird...")

    # status (display hp, xp, and gp)
    elif cmd == "status":
        # hp
        hp = pdata["hp"]
        await dsend(conn, pdata, f"Your current health is {hp}")
        if hp >= 85:
            await dsend(conn, pdata, "You are healthy.")
        elif hp >= 60 and hp < 85:
            await dsend(conn, pdata, "You're doing alright. Maybe eat some toast.")
        elif hp >= 30 and hp < 60:
            await dsend(conn, pdata, "You might want to get to the hospital.")
        elif hp < 30:
            await dsend(conn, pdata, "You definitely need some help.")
        else:
            print(f"{username} has a messed up hp! Their hp is {hp}")
            await dsend(conn, pdata, "You're health is...weird...")

        # xp
        await dsend(conn, pdata, f"Your current XP is {pdata["xp"]}")
        await dsend(conn, pdata, f"Your level is {pdata["level"]}")

        # gp
        gp = pdata["gp"]
        await dsend(conn, pdata, f"You currently have {gp} gold points.")
        if gp < 5:
            await dsend(conn, pdata, "You're kind of broke.")
        elif gp >= 5:
            await dsend(conn, pdata, "You've got some money.")
        elif gp >= 20:
            await dsend(conn, pdata, "You're getting up there.")
        elif gp >= 100:
            await dsend(conn, pdata, "You're rich!")
        elif gp >= 1000:
            await dsend(conn, pdata, "Holy sh.. You're the richest person I've met.")
        else:
            await dsend(conn, pdata, "You're gold is...weird...")
    
    #work (work at your job)
    elif cmd == "work":
        if pdata["level"] < 2:
            await dsend(conn, pdata, "You must be at least level 2 to work.")
            return
        else:
            now = time.time()
            addxp = random.randint(5, 10)
            addgp= random.randint(3, 7) / 100

            last_work = pdata["last_work_time"]
            if now - last_work < 15:  # 1 minute cooldown
                await dsend(conn, pdata, "You need to rest before working again.")
                return

            if pdata["pos"] == [10, 20]:  # Shop location
                pdata["gp"] += addgp
                pdata["xp"] += addxp
                pdata["last_work_time"] = now
                await dsend(conn, pdata, f"You worked at the shop! +{addxp} XP, +{addgp} gold.")
            elif pdata["pos"] == [15, 20]:  # Restaurant location
                pdata["gp"] += addgp
                pdata["xp"] += addxp
                pdata["last_work_time"] = now
                await dsend(conn, pdata, f"You worked at the restaurant! +{addxp} XP, +{addgp} gold.")
            else:
                await dsend(conn, pdata, "You need to be at the shop or restaurant to work.")
            return

    #sleep
    elif cmd == "sleep":
        if [x, y] == pdata["house"]:
            await dsend(conn, pdata, "You take a good nap. (HP regenerated)")
            pdata["hp"] = 100
    
    #map
    elif cmd == "map":
        await dsend(conn, pdata, "  |-  -  -  -  -  -  -  -  -  -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -  |")
        await dsend(conn, pdata, "50|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "49|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "48|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "47|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "46|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "45|                                                                                                                               |-------------------|                                          |")
        await dsend(conn, pdata, "  |                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "44|                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "  |                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "43|                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "  |                                                                                                                               |       forest      |                                          |")
        await dsend(conn, pdata, "42|                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "  |                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "41|                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "  |                                                                                                                               |                   |                                          |")
        await dsend(conn, pdata, "40|                                                                                                                               |-------------------|                                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "39|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "38|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "37|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "36|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "35|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "34|-                                                                                                                                                  |---------------|                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "33|                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "32|                                                                                                                                                   |     cave      |                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "31|                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                   |               |                          |")
        await dsend(conn, pdata, "30|-                                                                                                                                                  |---------------|                          |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "29|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "28|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "27|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "26|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "25|-------------------------------------------------------------------------------H----O----U----S----E----S-------------------------------------------------------------------------------------|")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "24|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "23|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "22|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "21|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                            |                  |                   |                                                                                                                          |")
        await dsend(conn, pdata, "20|                          store           restaurant            casino                                                                                                                        |")
        await dsend(conn, pdata, "  |                            |                  |                   |                                                                                                                          |")
        await dsend(conn, pdata, "19|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "18|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "17|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "16|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "15|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "14|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "13|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "12|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "11|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "10|                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "9 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "8 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "7 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "6 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "5 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "4 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "3 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "2 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "1 |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "  |                                                                                                                                                                                              |")
        await dsend(conn, pdata, "0 |-  -  -  -  -  -  -  -  -  -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -  |")
        await dsend(conn, pdata, "   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  50  ")
    
    #drink
    elif cmd.startswith("drink"):
        if cmd.startswith("drink ") and cmd[-1] != " " and len(cmd.split(" ")) == 2:
            drink = cmd.split(" ")[1]
            if drink in pdata["inventory"]:
                if drink == "ale":
                    await dsend(conn, pdata, "You chug down the ale in one gulp. You are now drunk.")
                    if "drunk" not in pdata["effects"]:
                        pdata["effects"].append("drunk")
                    pdata["effect_turn"] = 0
                elif drink == "water":
                    await dsend(conn, pdata, "You sip the water until it's finished.")
                    pdata["hp"] += 10
                elif drink == "vodka":
                    await dsend(conn, pdata, "You take a shot of vodka. You are now drunk.")
                    if "drunk" not in pdata["effects"]:
                        pdata["effects"].append("drunk")
                    pdata["effect_turn"] = 0
                elif drink == "martini":
                    await dsend(conn, pdata, "You sip the martini until you're done. You are now drunk.")
                    if "drunk" not in pdata["effects"]:
                        pdata["effects"].append("drunk")
                    pdata["effect_turn"] = 0
            else:
                await dsend(conn, pdata, "You need to have something, in order to drink it.")
        else:
            await dsend(conn, pdata, "Please type 'drink [item]' in order to drink something.")
    
    #eat
    elif cmd.startswith("eat"):
        if cmd.startswith("eat ") and cmd[-1] != " " and len(cmd.split(" ")) == 2:
            drink = cmd.split(" ")[1]
            if drink in pdata["inventory"]:
                if drink == "toast":
                    await dsend(conn, pdata, "You chug down the ale in one gulp.")
                    pdata["hp"] += 20
            else:
                await dsend(conn, pdata, "You need to have something, in order to eat it.")
        else:
            await dsend(conn, pdata, "Please type 'eat [item]' in order to drink something.")
    
    #everything else!
    else: 
        await dsend(conn, pdata, "Unknown command. Type 'help' for options.")
