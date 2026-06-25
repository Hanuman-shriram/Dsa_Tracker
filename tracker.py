import sqlite3
import csv
import os
from datetime import datetime

DB_FILE = "dsa_tracker.db"

COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}

def c(color, text):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

# ── Database Setup ────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            topic TEXT NOT NULL,
            platform TEXT DEFAULT 'LeetCode',
            notes TEXT DEFAULT '',
            date_solved TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_FILE)

# ── Add Problem ───────────────────────────────────────────
def add_problem():
    print(c("cyan", "\n━━━ Add Problem ━━━"))
    name = input("Problem name: ").strip()
    if not name:
        print(c("red", "Name cannot be empty."))
        return

    print("Difficulty: 1) Easy  2) Medium  3) Hard")
    diff_map = {"1": "Easy", "2": "Medium", "3": "Hard"}
    diff_choice = input("Choose (1/2/3): ").strip()
    difficulty = diff_map.get(diff_choice, "Medium")

    print("Topic: 1) Array  2) String  3) LinkedList  4) Tree  5) DP  6) Graph  7) BinarySearch  8) Stack/Queue  9) Hashing  10) Other")
    topic_map = {
        "1": "Array", "2": "String", "3": "LinkedList", "4": "Tree",
        "5": "DP", "6": "Graph", "7": "BinarySearch", "8": "Stack/Queue",
        "9": "Hashing", "10": "Other"
    }
    topic_choice = input("Choose (1-10): ").strip()
    topic = topic_map.get(topic_choice, "Other")

    print("Platform: 1) LeetCode  2) Codeforces  3) GeeksForGeeks  4) Other")
    platform_map = {"1": "LeetCode", "2": "Codeforces", "3": "GeeksForGeeks", "4": "Other"}
    platform_choice = input("Choose (1-4) [default=LeetCode]: ").strip()
    platform = platform_map.get(platform_choice, "LeetCode")

    notes = input("Notes (optional, press Enter to skip): ").strip()
    date = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    conn.execute(
        "INSERT INTO problems (name, difficulty, topic, platform, notes, date_solved) VALUES (?,?,?,?,?,?)",
        (name, difficulty, topic, platform, notes, date)
    )
    conn.commit()
    conn.close()

    diff_color = {"Easy": "green", "Medium": "yellow", "Hard": "red"}[difficulty]
    print(c("green", f"\n✅ Added: ") + c("bold", name) + f" [{c(diff_color, difficulty)}] [{topic}]")

# ── View Stats ────────────────────────────────────────────
def view_stats():
    conn = get_conn()
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    easy  = cur.execute("SELECT COUNT(*) FROM problems WHERE difficulty='Easy'").fetchone()[0]
    med   = cur.execute("SELECT COUNT(*) FROM problems WHERE difficulty='Medium'").fetchone()[0]
    hard  = cur.execute("SELECT COUNT(*) FROM problems WHERE difficulty='Hard'").fetchone()[0]

    print(c("cyan", "\n━━━ Your DSA Stats ━━━"))
    print(f"  Total Solved : {c('bold', str(total))}")
    print(f"  {c('green','Easy')}          : {easy}")
    print(f"  {c('yellow','Medium')}        : {med}")
    print(f"  {c('red','Hard')}          : {hard}")

    print(c("cyan", "\n━━━ Topic Breakdown ━━━"))
    topics = cur.execute(
        "SELECT topic, COUNT(*) as cnt FROM problems GROUP BY topic ORDER BY cnt DESC"
    ).fetchall()
    for topic, count in topics:
        bar = "█" * count
        print(f"  {topic:<15} {c('blue', bar)} {count}")

    print(c("cyan", "\n━━━ Recent 5 Problems ━━━"))
    recent = cur.execute(
        "SELECT name, difficulty, topic, date_solved FROM problems ORDER BY id DESC LIMIT 5"
    ).fetchall()
    for row in recent:
        name, diff, topic, date = row
        diff_color = {"Easy": "green", "Medium": "yellow", "Hard": "red"}.get(diff, "reset")
        print(f"  {c(diff_color, f'[{diff}]'):<20} {name:<35} {topic:<15} {date}")

    conn.close()

# ── List All Problems ─────────────────────────────────────
def list_problems():
    print(c("cyan", "\n━━━ Filter By ━━━"))
    print("1) All  2) Easy  3) Medium  4) Hard  5) By Topic")
    choice = input("Choose: ").strip()

    conn = get_conn()
    cur = conn.cursor()

    if choice == "2":
        rows = cur.execute("SELECT id, name, difficulty, topic, platform, date_solved FROM problems WHERE difficulty='Easy' ORDER BY id DESC").fetchall()
    elif choice == "3":
        rows = cur.execute("SELECT id, name, difficulty, topic, platform, date_solved FROM problems WHERE difficulty='Medium' ORDER BY id DESC").fetchall()
    elif choice == "4":
        rows = cur.execute("SELECT id, name, difficulty, topic, platform, date_solved FROM problems WHERE difficulty='Hard' ORDER BY id DESC").fetchall()
    elif choice == "5":
        topic = input("Enter topic name: ").strip()
        rows = cur.execute("SELECT id, name, difficulty, topic, platform, date_solved FROM problems WHERE topic LIKE ? ORDER BY id DESC", (f"%{topic}%",)).fetchall()
    else:
        rows = cur.execute("SELECT id, name, difficulty, topic, platform, date_solved FROM problems ORDER BY id DESC").fetchall()

    conn.close()

    if not rows:
        print(c("yellow", "No problems found."))
        return

    print(c("cyan", f"\n{'ID':<5} {'Name':<35} {'Diff':<10} {'Topic':<15} {'Platform':<15} {'Date'}"))
    print("─" * 95)
    for row in rows:
        id_, name, diff, topic, platform, date = row
        diff_color = {"Easy": "green", "Medium": "yellow", "Hard": "red"}.get(diff, "reset")
        print(f"  {id_:<4} {name:<35} {c(diff_color, diff):<10} {topic:<15} {platform:<15} {date}")

# ── Delete Problem ────────────────────────────────────────
def delete_problem():
    list_problems()
    try:
        pid = int(input("\nEnter ID to delete: ").strip())
        conn = get_conn()
        conn.execute("DELETE FROM problems WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        print(c("green", f"✅ Problem #{pid} deleted."))
    except:
        print(c("red", "Invalid ID."))

# ── Export CSV ────────────────────────────────────────────
def export_csv():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM problems ORDER BY id DESC").fetchall()
    conn.close()

    filename = f"dsa_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Difficulty", "Topic", "Platform", "Notes", "Date Solved"])
        writer.writerows(rows)

    print(c("green", f"✅ Exported {len(rows)} problems to {c('bold', filename)}"))

# ── Main Menu ─────────────────────────────────────────────
def main():
    init_db()
    print(c("bold", c("blue", """
╔═══════════════════════════════════╗
║    DSA Progress Tracker v1.0      ║
║    by Dev | IIT Patna             ║
╚═══════════════════════════════════╝""")))

    while True:
        print(c("cyan", "\n━━━ Main Menu ━━━"))
        print("  1) Add Problem")
        print("  2) View Stats")
        print("  3) List Problems")
        print("  4) Delete Problem")
        print("  5) Export to CSV")
        print("  6) Exit")

        choice = input(c("bold", "\nChoose: ")).strip()

        if choice == "1":
            add_problem()
        elif choice == "2":
            view_stats()
        elif choice == "3":
            list_problems()
        elif choice == "4":
            delete_problem()
        elif choice == "5":
            export_csv()
        elif choice == "6":
            print(c("green", "\nKeep grinding! 💪\n"))
            break
        else:
            print(c("red", "Invalid choice."))

if __name__ == "__main__":
    main()
