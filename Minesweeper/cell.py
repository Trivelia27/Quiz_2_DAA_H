class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.adjacent_mines = 0
        self.revealed = False
        self.flagged = False

    def reveal(self):
        if not self.flagged:
            self.revealed = True

    def toggle_flag(self):
        if not self.revealed:
            self.flagged = not self.flagged

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, Mine={self.is_mine}, Revealed={self.revealed})"
