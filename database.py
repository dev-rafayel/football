"""
database.py

Handles everything related to saving and loading data with SQLite.
Players and their match stats are stored here, plus the scoring
weights used later for the performance calculations.
"""

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "football.db"


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            match_date TEXT NOT NULL,
            opponent TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE
        )
    """)

    # only one row ever exists in this table, it just stores the current weights
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            goal_weight REAL DEFAULT 3,
            assist_weight REAL DEFAULT 2,
            save_weight REAL DEFAULT 1
        )
    """)
    cur.execute("INSERT OR IGNORE INTO weights (id) VALUES (1)")

    conn.commit()
    conn.close()


# ---- players ----

def add_player(name):
    conn = connect()
    try:
        conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # name already exists
        return False
    finally:
        conn.close()


def list_players():
    conn = connect()
    players = conn.execute("SELECT * FROM players ORDER BY name").fetchall()
    conn.close()
    return players


def delete_player(player_id):
    conn = connect()
    conn.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()


def rename_player(player_id, new_name):
    conn = connect()
    try:
        conn.execute("UPDATE players SET name = ? WHERE player_id = ?", (new_name, player_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # another player already has that name
        return False
    finally:
        conn.close()


# ---- matches ----

def add_match(player_id, match_date, opponent, goals, assists, saves, minutes):
    conn = connect()
    conn.execute("""
        INSERT INTO matches (player_id, match_date, opponent, goals, assists, saves, minutes_played)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (player_id, match_date, opponent, goals, assists, saves, minutes))
    conn.commit()
    conn.close()


def find_match_on_date(player_id, match_date):
    """Used to warn about duplicates before adding a new match."""
    conn = connect()
    match = conn.execute(
        "SELECT * FROM matches WHERE player_id = ? AND match_date = ?",
        (player_id, match_date)
    ).fetchone()
    conn.close()
    return match


def get_match_by_id(match_id):
    conn = connect()
    match = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    conn.close()
    return match


def get_matches_for_player(player_id):
    conn = connect()
    matches = conn.execute(
        "SELECT * FROM matches WHERE player_id = ? ORDER BY match_date",
        (player_id,)
    ).fetchall()
    conn.close()
    return matches


def update_match(match_id, match_date, opponent, goals, assists, saves, minutes):
    conn = connect()
    conn.execute("""
        UPDATE matches
        SET match_date = ?, opponent = ?, goals = ?, assists = ?, saves = ?, minutes_played = ?
        WHERE match_id = ?
    """, (match_date, opponent, goals, assists, saves, minutes, match_id))
    conn.commit()
    conn.close()


def delete_match(match_id):
    conn = connect()
    conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()


# ---- weights ----

def get_weights():
    conn = connect()
    row = conn.execute("SELECT * FROM weights WHERE id = 1").fetchone()
    conn.close()
    return row


def update_weights(goal_weight, assist_weight, save_weight):
    conn = connect()
    conn.execute("""
        UPDATE weights SET goal_weight = ?, assist_weight = ?, save_weight = ?
        WHERE id = 1
    """, (goal_weight, assist_weight, save_weight))
    conn.commit()
    conn.close()
