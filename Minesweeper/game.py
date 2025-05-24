# game.py

import random
from collections import deque

class Cell:
    def __init__(self):
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.adjacent_mines = 0

    def toggle_flag(self):
        self.flagged = not self.flagged

class MinesweeperGame:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.is_game_over = False
        self.is_win = False
        self._place_mines()
        self._calculate_adjacent_mines()

    def _place_mines(self):
        positions = set()
        while len(positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.board[r][c].is_mine:
                self.board[r][c].is_mine = True
                positions.add((r, c))

    def _calculate_adjacent_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c].is_mine:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.board[nr][nc].is_mine:
                                count += 1
                self.board[r][c].adjacent_mines = count

    def reveal_cell(self, r, c):
        if self.board[r][c].flagged or self.board[r][c].revealed:
            return

        if self.board[r][c].is_mine:
            self.board[r][c].revealed = True
            self.is_game_over = True
            self.is_win = False
            return

        self._dfs_reveal(r, c)
        self._check_win()

    def _dfs_reveal(self, r, c):
        stack = deque()
        stack.append((r, c))

        while stack:
            x, y = stack.pop()
            cell = self.board[x][y]
            if cell.revealed or cell.flagged:
                continue
            cell.revealed = True
            if cell.adjacent_mines == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            neighbor = self.board[nx][ny]
                            if not neighbor.revealed and not neighbor.is_mine:
                                stack.append((nx, ny))

    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                if not cell.is_mine and not cell.revealed:
                    return
        self.is_game_over = True
        self.is_win = True
