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
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_leaderboard(scores, file_path="leaderboard.json"):
    with open(file_path, "w") as f:
        json.dump(scores, f, indent=4)

def add_score(name, score, level, duration, file_path="leaderboard.json"):
    scores = load_leaderboard(file_path)
    scores.append({
        "name": name,
        "score": score,
        "level": level,
        "duration": duration  # dalam detik, misalnya
    })
    # Sort descending by score
    scores.sort(key=lambda x: -x["score"])
    scores = scores[:10]  # Keep top 10 scores
    save_leaderboard(scores, file_path)
