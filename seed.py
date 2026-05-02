"""
Seed script — populates starter moves and tricks.
Safe to re-run: uses INSERT OR IGNORE so nothing gets duplicated.

Called explicitly from server.py on container startup.

Manual usage (with Docker):
    docker compose exec card-tricks python3 seed.py

Manual usage (local):
    source venv/bin/activate
    python3 seed.py
"""
import sqlite3
from database import get_db_path
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
    """Run the starter library seed exactly once per database.

    The seed runs only when ALL of the following are true:
      - settings.initial_seed_done is not '1'
      - the moves table is empty
      - the tricks table is empty

    Once it runs we set settings.initial_seed_done = '1' so subsequent
    container starts never re-add deleted rows. (The moves/tricks tables
    have no UNIQUE name constraint, so INSERT OR IGNORE alone is not safe
    against re-adding things the user has deleted.)
    """
    today = date.today().isoformat()
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    # Has the seed already run on this database?
    flag = c.execute(
        "SELECT value FROM settings WHERE key = 'initial_seed_done'"
    ).fetchone()
    if flag and flag[0] == "1":
        conn.close()
        print("Seed — already run on this database, skipping.")
        return

    # Belt-and-braces: if the user has any data, treat the DB as theirs.
    moves_count  = c.execute("SELECT COUNT(*) FROM moves").fetchone()[0]
    tricks_count = c.execute("SELECT COUNT(*) FROM tricks").fetchone()[0]
    if moves_count or tricks_count:
        c.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('initial_seed_done', '1')"
        )
        conn.commit()
        conn.close()
        print(f"Seed — found existing data ({moves_count} moves, {tricks_count} tricks); marking seed done and skipping.")
        return

    moves_added = 0
    tricks_added = 0

    for name, category, level in MOVES:
        c.execute(
            "INSERT INTO moves (name, category, level, source, notes, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, '', '', 0, ?, ?)",
            (name, category, level, today, today)
        )
        moves_added += 1

    for name, type_, status in TRICKS:
        c.execute(
            "INSERT INTO tricks (name, type, status, moves_used, source, notes, link, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, '', '', '', '', 0, ?, ?)",
            (name, type_, status, today, today)
        )
        tricks_added += 1

    c.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('initial_seed_done', '1')"
    )
    conn.commit()
    conn.close()

    print(f"Seed — {moves_added} moves and {tricks_added} tricks added (first run).")


def dedupe_seed_duplicates():
    """One-shot cleanup for databases that were affected by the pre-fix seed
    behaviour. Safe to run by hand:

        docker compose exec card-tricks python3 seed.py --dedupe

    For each starter name with multiple rows, keeps the row that looks most
    like the user's (highest practice_count, then longest notes, then
    earliest id) and removes the others. Untouched if no duplicates exist.
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    def _dedupe(table, names):
        removed = 0
        for name in names:
            rows = c.execute(
                f"SELECT id, practice_count, COALESCE(notes,''), updated_at "
                f"FROM {table} WHERE name = ? ORDER BY practice_count DESC, "
                f"length(COALESCE(notes,'')) DESC, id ASC",
                (name,),
            ).fetchall()
            if len(rows) <= 1:
                continue
            keeper_id = rows[0][0]
            duplicate_ids = [r[0] for r in rows[1:]]
            placeholders = ",".join("?" * len(duplicate_ids))
            c.execute(
                f"DELETE FROM {table} WHERE id IN ({placeholders})",
                duplicate_ids,
            )
            removed += len(duplicate_ids)
            print(f"  {table}: kept #{keeper_id} of '{name}', removed {len(duplicate_ids)} duplicate(s)")
        return removed

    moves_removed = _dedupe("moves", [m[0] for m in MOVES])
    tricks_removed = _dedupe("tricks", [t[0] for t in TRICKS])

    # Make sure the seed-done flag is set so future starts never re-seed.
    c.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('initial_seed_done', '1')"
    )

    conn.commit()
    conn.close()
    print(f"Dedupe complete: removed {moves_removed} duplicate move(s) and {tricks_removed} duplicate trick(s).")


def seed_starter_notes():
    """Populate step-by-step notes for the canonical tricks defined in
    seed_notes.STARTER_NOTES.

    Only fills tricks where the notes column is currently empty / NULL —
    NEVER overwrites anything the user has already written. Idempotent.
    """
    from seed_notes import STARTER_NOTES

    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    today = date.today().isoformat()

    filled = 0
    skipped_existing = 0
    skipped_missing = 0

    for name, notes in STARTER_NOTES.items():
        # Match by exact name on active tricks only.
        rows = c.execute(
            "SELECT id, COALESCE(notes,'') AS notes FROM tricks "
            "WHERE name = ? AND deleted_at IS NULL",
            (name,),
        ).fetchall()

        if not rows:
            skipped_missing += 1
            continue

        for tid, existing in rows:
            if existing.strip():
                skipped_existing += 1
                continue
            c.execute(
                "UPDATE tricks SET notes = ?, updated_at = ? WHERE id = ?",
                (notes, today, tid),
            )
            filled += 1

    conn.commit()
    conn.close()
    print(f"Filled notes for {filled} trick(s).")
    if skipped_existing:
        print(f"Skipped {skipped_existing} that already had notes (left untouched).")
    if skipped_missing:
        print(f"Skipped {skipped_missing} starter trick(s) not present in your library.")


def remove_untouched_seeds():
    """Remove any starter-library row the user has never customised.

    A row is considered "untouched" if every field still matches the seed
    defaults exactly: never practiced, no notes/source, default rating, and
    default level/status. Anything the user has touched (rated, added notes,
    bumped status, practised) is preserved.

    Already soft-deleted rows are left alone — they're in Recently Deleted
    and the user can purge them from there if they want.
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    seed_move_names  = [m[0] for m in MOVES]
    seed_trick_names = [t[0] for t in TRICKS]

    move_placeholders  = ",".join("?" * len(seed_move_names))
    trick_placeholders = ",".join("?" * len(seed_trick_names))

    moves_cur = c.execute(
        f"DELETE FROM moves WHERE deleted_at IS NULL "
        f"AND name IN ({move_placeholders}) "
        f"AND COALESCE(practice_count, 0) = 0 "
        f"AND last_practiced IS NULL "
        f"AND COALESCE(notes,  '') = '' "
        f"AND COALESCE(source, '') = '' "
        f"AND COALESCE(rating, 0) = 0 "
        f"AND COALESCE(level, 'beginner') = 'beginner'",
        seed_move_names,
    )
    moves_removed = moves_cur.rowcount

    tricks_cur = c.execute(
        f"DELETE FROM tricks WHERE deleted_at IS NULL "
        f"AND name IN ({trick_placeholders}) "
        f"AND COALESCE(practice_count, 0) = 0 "
        f"AND last_practiced IS NULL "
        f"AND COALESCE(notes,      '') = '' "
        f"AND COALESCE(source,     '') = '' "
        f"AND COALESCE(link,       '') = '' "
        f"AND COALESCE(moves_used, '') = '' "
        f"AND COALESCE(rating, 0) = 0 "
        f"AND COALESCE(status, 'learning') = 'learning'",
        seed_trick_names,
    )
    tricks_removed = tricks_cur.rowcount

    # Make sure auto-seed never resurrects them (belt-and-braces — server.py
    # no longer calls run_seed at all, but if anyone runs `python3 seed.py`
    # by hand, the flag stops it).
    c.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('initial_seed_done', '1')"
    )

    conn.commit()
    conn.close()
    print(f"Removed {moves_removed} untouched starter move(s) and {tricks_removed} untouched starter trick(s).")
    print("Anything you'd practised, rated, or made notes on is untouched.")


if __name__ == "__main__":
    import sys
    from database import init_db
    init_db()
    if "--dedupe" in sys.argv:
        dedupe_seed_duplicates()
    elif "--remove-untouched-seeds" in sys.argv:
        remove_untouched_seeds()
    elif "--seed-notes" in sys.argv:
        seed_starter_notes()
    elif "--seed" in sys.argv:
        run_seed()
    else:
        print("Usage:")
        print("  python3 seed.py --seed                     Add the starter library (only on first run)")
        print("  python3 seed.py --seed-notes               Fill canonical step-by-step notes on tricks with empty notes")
        print("  python3 seed.py --dedupe                   Collapse duplicate seeded rows")
        print("  python3 seed.py --remove-untouched-seeds   Remove starter rows you've never touched")
