import json
import os

def dfs_reveal(board, x, y, rows, cols):
    stack = [(x, y)]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))

        cell = board[cx][cy]
        if cell.flagged or cell.revealed:
            continue

        cell.reveal()

        if cell.adjacent_mines == 0 and not cell.is_mine:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                        stack.append((nx, ny))

def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def load_leaderboard(file_path="leaderboard.json"):
    if not os.path.exists(file_path):
        # Jika file tidak ada, buat file kosong
        with open(file_path, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Validasi: pastikan data list of dict
            if isinstance(data, list):
                return data
            else:
                return []
    except Exception as e:
        print(f"[ERROR] Failed to load leaderboard: {e}")
        # Jika file corrupt, reset leaderboard
        with open(file_path, "w") as f:
            json.dump([], f)
        return []

def save_leaderboard(scores, file_path="leaderboard.json"):
    try:
        with open(file_path, "w") as f:
            json.dump(scores, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Failed to save leaderboard: {e}")

def add_score(name, score, level, duration, file_path="leaderboard.json"):
    scores = load_leaderboard(file_path)
    scores.append({
        "name": name,
        "score": score,
        "level": level,
        "duration": duration  # dalam detik
    })
    # Sort descending by score, jika sama urutkan berdasarkan waktu tercepat
    scores.sort(key=lambda x: (-x["score"], x["duration"]))
    scores = scores[:10]  # Keep top 10 scores
    save_leaderboard(scores, file_path)