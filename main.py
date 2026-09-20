"""
main.py

Entry point. Shows a text menu in the terminal and routes the user's
choice to the right database/calculation/visualization functions.
"""

from datetime import datetime

import database
import calculations
from visualization import plot_player_trend

MENU = """
==== Football Performance Tracker ====
1. Manage players (add / delete)
2. Add match record
3. View / edit / delete matches for a player
4. Show stats for a player
5. Set scoring weights
6. Plot performance trend
7. Exit
"""


def ask_int(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def ask_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number.")


def ask_date(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Please enter a date as YYYY-MM-DD, e.g. 2026-03-14.")


def pick_player():
    players = database.list_players()
    if not players:
        print("No players yet - add one first.")
        return None

    for p in players:
        print(f"  {p['player_id']}. {p['name']}")
    player_id = ask_int("Player ID: ")

    for p in players:
        if p["player_id"] == player_id:
            return p

    print("That ID doesn't match any player.")
    return None


def manage_players_flow():
    players = database.list_players()
    if players:
        print("\nCurrent players:")
        for p in players:
            print(f"  {p['player_id']}. {p['name']}")
    else:
        print("\nNo players yet.")

    action = input("(a)dd, (r)ename, (d)elete, or (b)ack? ").strip().lower()

    if action == "a":
        name = input("Player name: ").strip()
        if not name:
            print("Name can't be empty.")
            return
        if database.add_player(name):
            print(f"Added {name}.")
        else:
            print("A player with that name already exists.")

    elif action == "r":
        if not players:
            print("Nothing to rename.")
            return
        player_id = ask_int("Player ID to rename: ")
        if not any(p["player_id"] == player_id for p in players):
            print("That ID doesn't match any player.")
            return
        new_name = input("New name: ").strip()
        if not new_name:
            print("Name can't be empty.")
            return
        if database.rename_player(player_id, new_name):
            print("Renamed.")
        else:
            print("A player with that name already exists.")

    elif action == "d":
        if not players:
            print("Nothing to delete.")
            return
        player_id = ask_int("Player ID to delete: ")
        if not any(p["player_id"] == player_id for p in players):
            print("That ID doesn't match any player.")
            return
        database.delete_player(player_id)
        print("Deleted. (Their match records were deleted too.)")

    elif action in ("b", ""):
        return

    else:
        print("Unknown option.")


def add_match_flow():
    player = pick_player()
    if not player:
        return

    match_date = ask_date("Match date (YYYY-MM-DD): ")

    existing = database.find_match_on_date(player["player_id"], match_date)
    if existing:
        confirm = input(
            f"{player['name']} already has a match recorded on {match_date} "
            f"(vs {existing['opponent']}). Add another anyway? (y/n): "
        ).strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return

    opponent = input("Opponent: ").strip()
    goals = ask_int("Goals: ")
    assists = ask_int("Assists: ")
    saves = ask_int("Saves: ")
    minutes = ask_int("Minutes played: ")

    database.add_match(player["player_id"], match_date, opponent, goals, assists, saves, minutes)
    print("Match added.")


def manage_matches_flow():
    player = pick_player()
    if not player:
        return

    matches = database.get_matches_for_player(player["player_id"])
    if not matches:
        print("No matches recorded for this player yet.")
        return

    print(f"\nMatches for {player['name']}:")
    for m in matches:
        print(f"  {m['match_id']}. {m['match_date']} vs {m['opponent']} - "
              f"G:{m['goals']} A:{m['assists']} S:{m['saves']} Min:{m['minutes_played']}")

    action = input("\n(e)dit, (d)elete, or (b)ack? ").strip().lower()
    if action == "b" or action == "":
        return

    match_id = ask_int("Match ID: ")
    if not any(m["match_id"] == match_id for m in matches):
        print("That match ID isn't in this player's records.")
        return

    if action == "d":
        database.delete_match(match_id)
        print("Deleted.")
    elif action == "e":
        match_date = ask_date("New date (YYYY-MM-DD): ")
        opponent = input("New opponent: ").strip()
        goals = ask_int("New goals: ")
        assists = ask_int("New assists: ")
        saves = ask_int("New saves: ")
        minutes = ask_int("New minutes played: ")
        database.update_match(match_id, match_date, opponent, goals, assists, saves, minutes)
        print("Updated.")
    else:
        print("Unknown option.")


def show_stats_flow():
    player = pick_player()
    if not player:
        return

    matches = database.get_matches_for_player(player["player_id"])
    if not matches:
        print("No matches recorded yet.")
        return

    totals = calculations.total_stats(matches)
    averages = calculations.average_stats(matches)
    weights = database.get_weights()

    print(f"\n-- Stats for {player['name']} ({len(matches)} matches) --")
    print(f"Total goals: {totals['goals']}, assists: {totals['assists']}, saves: {totals['saves']}")
    print(f"Average per match: {averages['goals']:.2f}G  {averages['assists']:.2f}A  {averages['saves']:.2f}S")

    total_score = sum(calculations.performance_score(m, weights) for m in matches)
    print(f"Total performance score: {total_score:.1f}")
    print(f"Average performance score: {total_score / len(matches):.1f}")


def set_weights_flow():
    current = database.get_weights()
    print(f"Current weights - goal: {current['goal_weight']}, "
          f"assist: {current['assist_weight']}, save: {current['save_weight']}")

    goal_w = ask_float("New goal weight: ")
    assist_w = ask_float("New assist weight: ")
    save_w = ask_float("New save weight: ")

    database.update_weights(goal_w, assist_w, save_w)
    print("Weights updated.")


def plot_trend_flow():
    player = pick_player()
    if not player:
        return

    matches = database.get_matches_for_player(player["player_id"])
    weights = database.get_weights()
    plot_player_trend(player["name"], matches, weights)


def main():
    database.setup_database()

    actions = {
        "1": manage_players_flow,
        "2": add_match_flow,
        "3": manage_matches_flow,
        "4": show_stats_flow,
        "5": set_weights_flow,
        "6": plot_trend_flow,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "7":
            print("Bye.")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Not a valid option, try again.")


if __name__ == "__main__":
    main()
