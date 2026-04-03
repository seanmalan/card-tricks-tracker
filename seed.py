"""
Seed script — populates starter moves and tricks.
Safe to re-run: uses INSERT OR IGNORE so nothing gets duplicated.

Called automatically on container startup via server.py.

Manual usage (with Docker):
    docker compose exec card-tricks python3 seed.py

Manual usage (local):
    source venv/bin/activate
    python3 seed.py
"""
import sqlite3
from database import get_db_path, init_db
from datetime import date


# ---- MOVES & SLEIGHTS ----
# (name, category, level)
MOVES = [
    # Controls
    ("Classic Pass",            "Control",       "beginner"),
    ("Riffle Pass",             "Control",       "beginner"),
    ("Hindu Pass",              "Control",       "beginner"),
    ("Overhand Control",        "Control",       "beginner"),
    ("Hindu Control",           "Control",       "beginner"),
    ("Side Steal",              "Control",       "beginner"),
    ("Card to Top Control",     "Control",       "beginner"),
    ("Injog Control",           "Control",       "beginner"),

    # Double Lifts
    ("Basic Double Lift",       "Other",         "beginner"),
    ("Strike Double Lift",      "Other",         "beginner"),
    ("Push-Off Double Lift",    "Other",         "beginner"),
    ("Snap Double Lift",        "Other",         "beginner"),

    # False Shuffles
    ("Zarrow Shuffle",          "False Shuffle", "beginner"),
    ("Riffle False Shuffle",    "False Shuffle", "beginner"),
    ("Overhand False Shuffle",  "False Shuffle", "beginner"),
    ("Hindu False Shuffle",     "False Shuffle", "beginner"),
    ("Up the Ladder Cut",       "False Shuffle", "beginner"),

    # False Cuts
    ("Triple Cut (false)",      "False Cut",     "beginner"),
    ("Swing Cut",               "False Cut",     "beginner"),
    ("Sybil Cut",               "False Cut",     "beginner"),
    ("Charlier Cut (false)",    "False Cut",     "beginner"),

    # Forces
    ("Classic Force",           "Force",         "beginner"),
    ("Hindu Force",             "Force",         "beginner"),
    ("Riffle Force",            "Force",         "beginner"),
    ("Crisscross Force",        "Force",         "beginner"),
    ("10-20 Force",             "Force",         "beginner"),
    ("Countdown Force",         "Force",         "beginner"),

    # Palms
    ("Classic Palm",            "Palm",          "beginner"),
    ("Finger Palm",             "Palm",          "beginner"),
    ("Top Palm",                "Palm",          "beginner"),
    ("Tenkai Palm",             "Palm",          "beginner"),
    ("Gambler's Cop",           "Palm",          "beginner"),
    ("Back Palm",               "Palm",          "beginner"),

    # Switches & Changes
    ("Top Change",              "Switch",        "beginner"),
    ("Bottom Change",           "Switch",        "beginner"),
    ("Erdnase Color Change",    "Switch",        "beginner"),
    ("Snap Change",             "Switch",        "beginner"),
    ("Turnover Change",         "Switch",        "beginner"),

    # Breaks
    ("Little Finger Break",     "Control",       "beginner"),
    ("Thumb Break",             "Control",       "beginner"),

    # Productions & Vanishes
    ("Glide",                   "Production",    "beginner"),
    ("Ribbon Spread",           "Production",    "beginner"),
    ("Spring",                  "Flourish",      "beginner"),
    ("Pressure Fan",            "Flourish",      "beginner"),
    ("Waterfall",               "Flourish",      "beginner"),
    ("Charlier Cut (one-hand)", "Flourish",      "beginner"),
]

# ---- TRICKS & ROUTINES ----
# (name, type, status)
TRICKS = [
    # Classics
    ("Ambitious Card",                  "Trick",   "learning"),
    ("Triumph",                         "Trick",   "learning"),
    ("Out of This World",               "Trick",   "learning"),
    ("Invisible Deck",                  "Trick",   "learning"),
    ("Card Warp",                       "Trick",   "learning"),
    ("Oil and Water",                   "Trick",   "learning"),
    ("Chicago Opener",                  "Trick",   "learning"),
    ("Do As I Do",                      "Trick",   "learning"),
    ("Think of a Card",                 "Trick",   "learning"),
    ("The Biddle Trick",                "Trick",   "learning"),
    ("Princess Card Trick",             "Trick",   "learning"),
    ("Lie Detector",                    "Trick",   "learning"),
    ("Mental Photography",              "Trick",   "learning"),

    # Ace & Number Tricks
    ("Four Ace Trick",                  "Trick",   "learning"),
    ("Acrobatic Aces",                  "Trick",   "learning"),
    ("Spectator Cuts to the Aces",      "Trick",   "learning"),
    ("Twisted Aces",                    "Trick",   "learning"),
    ("Any Card at Any Number (ACAAN)",  "Trick",   "learning"),
    ("21 Card Trick",                   "Trick",   "learning"),

    # Transpositions & Appearances
    ("Card to Wallet",                  "Trick",   "learning"),
    ("Card to Pocket",                  "Trick",   "learning"),
    ("Card Under Glass",                "Trick",   "learning"),
    ("The Rising Card",                 "Trick",   "learning"),
    ("Three Card Monte",                "Trick",   "learning"),
    ("Sam the Bellhop",                 "Routine", "learning"),

    # Beginner-Friendly
    ("Pick a Card (basic)",             "Trick",   "learning"),
    ("Card Revelation",                 "Trick",   "learning"),
    ("The 10-20 Trick",                 "Trick",   "learning"),
    ("The Self-Working Card Trick",     "Trick",   "learning"),
]


def run_seed():
    init_db()
    today = date.today().isoformat()
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    moves_added = 0
    tricks_added = 0

    for name, category, level in MOVES:
        c.execute(
            "INSERT OR IGNORE INTO moves (name, category, level, source, notes, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, '', '', 0, ?, ?)",
            (name, category, level, today, today)
        )
        moves_added += c.rowcount

    for name, type_, status in TRICKS:
        c.execute(
            "INSERT OR IGNORE INTO tricks (name, type, status, moves_used, source, notes, link, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, '', '', '', '', 0, ?, ?)",
            (name, type_, status, today, today)
        )
        tricks_added += c.rowcount

    conn.commit()
    conn.close()

    if moves_added or tricks_added:
        print(f"Seed — {moves_added} moves and {tricks_added} tricks added.")
    else:
        print("Seed — database already populated, nothing to add.")


run_seed()
