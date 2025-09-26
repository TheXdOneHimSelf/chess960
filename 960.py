import requests
import json

# List of bot usernames
USERNAMES = ["ToromBot", "Endogenetic-Bot", "Exogenetic-Bot","RaspFish", "strain-on-veins", "NNUE_Drift"]

# API endpoint template
API_URL = "https://lichess.org/api/games/user/{}"

# Request parameters
params = {
    "perfType": "chess960",   # Only Chess960 games
    "pgnInJson": "true",      # Easier filtering
    "clocks": "true",         # Include clock times
    "evals": "false",         # Skip evals (smaller file)
}

headers = {"Accept": "application/x-ndjson"}

for USERNAME in USERNAMES:
    print(f"Fetching games for {USERNAME}...")

    # Output PGN files (White and Black)
    OUTPUT_WHITE = f"{USERNAME.lower()}_white_games.pgn"
    OUTPUT_BLACK = f"{USERNAME.lower()}_black_games.pgn"

    response = requests.get(API_URL.format(USERNAME), params=params, headers=headers, stream=True)

    if response.status_code != 200:
        print(f"❌ Failed to fetch games for {USERNAME}: {response.status_code}")
        continue

    with open(OUTPUT_WHITE, "w", encoding="utf-8") as fw, open(OUTPUT_BLACK, "w", encoding="utf-8") as fb:
        for line in response.iter_lines():
            if not line:
                continue
            game_json = json.loads(line.decode("utf-8"))

            # Identify bot color
            bot_as_white = game_json["players"]["white"]["user"]["name"].lower() == USERNAME.lower()
            bot_as_black = game_json["players"]["black"]["user"]["name"].lower() == USERNAME.lower()

            winner = game_json.get("winner", None)
            status = game_json.get("status", "").lower()

            # Conditions for win or draw
            is_win = (winner == "white" and bot_as_white) or (winner == "black" and bot_as_black)
            is_draw = status in ["draw", "stalemate", "timeout", "outoftime", "repetition", "50move", "insufficient"] and not is_win

            if is_win or is_draw:
                if bot_as_white:
                    fw.write(game_json["pgn"] + "\n\n")
                elif bot_as_black:
                    fb.write(game_json["pgn"] + "\n\n")

    print(f"✅ Saved {USERNAME}'s Chess960 White games → {OUTPUT_WHITE}")
    print(f"✅ Saved {USERNAME}'s Chess960 Black games → {OUTPUT_BLACK}")
