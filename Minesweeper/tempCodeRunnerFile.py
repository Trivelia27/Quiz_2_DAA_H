import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import time
import pygame
from game import MinesweeperGame
from utils import format_time, add_score, load_leaderboard

pygame.mixer.init()
click_sound = pygame.mixer.Sound("click.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
win_sound = pygame.mixer.Sound("win.wav")
gameover_sound = pygame.mixer.Sound("gameover.wav")
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

class StartScreen(tk.Frame):
    def __init__(self, master, start_callback):
        super().__init__(master)
        self.start_callback = start_callback
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Welcome to Minesweeper Interactive!", font=("Helvetica", 18, "bold")).pack(pady=20)
        tk.Label(self, text="Enter your name:", font=("Helvetica", 14)).pack(pady=5)

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self, textvariable=self.name_var, font=("Helvetica", 14))
        self.name_entry.pack(pady=5)
        self.name_entry.focus_set()

        tk.Button(self, text="Start Game", font=("Helvetica", 14), command=self.on_start).pack(pady=20)

    def on_start(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Invalid Name", "Please enter your name to start the game.")
            return
        self.start_callback(name)
        self.destroy()

class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper Interactive")
        self.geometry("600x700")
        self.resizable(False, False)

        self.player_name = None

        self.levels = {
            "Easy": (9, 9, 10, None),
            "Medium": (16, 16, 40, None),
            "Hard": (24, 24, 99, None),
            "Time Challenge": (16, 16, 40, 120),
            "Expert": (24, 24, 99, 60)
        }
        self.current_level = "Easy"
        self.game = None
        self.buttons = {}
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.score = 0

        style = ttk.Style()
        style.theme_use('default')
        style.configure("green.Horizontal.TProgressbar", troughcolor='white', background='green')
        style.configure("red.Horizontal.TProgressbar", troughcolor='white', background='red')

        self.start_screen = StartScreen(self, self.start_game)

    def start_game(self, player_name):
        self.player_name = player_name
        self.start_screen.pack_forget()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        frame_top = tk.Frame(self)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text=f"Player: {self.player_name}", font=("Helvetica", 12, "italic")).pack(side=tk.LEFT, padx=10)
        tk.Label(frame_top, text="Select Level:").pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value=self.current_level)
        level_menu = ttk.Combobox(frame_top, textvariable=self.level_var, values=list(self.levels.keys()), state="readonly")
        level_menu.pack(side=tk.LEFT)
        level_menu.bind("<<ComboboxSelected>>", self.change_level)

        self.timer_label = tk.Label(self, text="Time: 00:00", font=("Helvetica", 14))
        self.timer_label.pack()
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=500)
        self.progress_bar.pack(pady=5)

        self.score_label = tk.Label(self, text="Score: 0", font=("Helvetica", 14))
        self.score_label.pack()

        self.info_label = tk.Label(self, text="", font=("Helvetica", 12))
        self.info_label.pack(pady=5)

        self.board_frame = tk.Frame(self)
        self.board_frame.pack(pady=10, fill="both", expand=True)

        self.reset_button = tk.Button(self, text="Reset Game", command=self.reset_game)
        self.reset_button.pack(pady=5)

        self.leaderboard_button = tk.Button(self, text="Show Leaderboard", command=self.show_leaderboard)
        self.leaderboard_button.pack(pady=5)

        self.bind('<r>', lambda e: self.reset_game())

    def change_level(self, event):
        self.current_level = self.level_var.get()
        self.reset_game()

    def reset_game(self):
        if self.timer_running:
            self.timer_running = False
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        rows, cols, mines, self.time_limit = self.levels[self.current_level]
        self.game = MinesweeperGame(rows, cols, mines)
        self.buttons = {}

        for r in range(rows):
            self.board_frame.grid_rowconfigure(r, weight=1)
            for c in range(cols):
                self.board_frame.grid_columnconfigure(c, weight=1)
                btn = tk.Button(self.board_frame, font=("Consolas", 12, "bold"),
                                command=lambda x=r, y=c: self.on_left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.on_right_click(x, y))
                btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                self.buttons[(r, c)] = btn

        self.start_time = time.time()
        self.elapsed_time = 0
        self.score = 0
        self.update_score(0)
        self.update_info_label()
        self.timer_running = True
        self.update_timer()
        self.reset_button.focus_set()

    def update_score(self, add_points):
        self.score += add_points
        self.score_label.config(text=f"Score: {self.score}")

    def update_info_label(self):
        mines_left = self.game.mines - sum(1 for row in self.game.board for cell in row if cell.flagged)
        self.info_label.config(text=f"Mines: {self.game.mines} | Flags Left: {mines_left}")

    def update_timer(self):
        if not self.timer_running:
            return
        self.elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {format_time(self.elapsed_time)}")

        if self.time_limit:
            percent = max(0, 100 - (self.elapsed_time / self.time_limit) * 100)
            self.progress_var.set(percent)
            if percent <= 20:
                self.progress_bar.config(style="red.Horizontal.TProgressbar")
            else:
                self.progress_bar.config(style="green.Horizontal.TProgressbar")
            if self.elapsed_time >= self.time_limit:
                self.timer_running = False
                self.game.is_game_over = True
                self.game.is_win = False
                self.reveal_all()
                self.game_over(False, timeout=True)
                return
        else:
            self.progress_var.set(0)

        self.after(1000, self.update_timer)

    def on_left_click(self, x, y):
        if self.game.is_game_over:
            return
        cell = self.game.board[x][y]
        if cell.flagged or cell.revealed:
            return
        click_sound.play()
        self.game.reveal_cell(x, y)
        self.update_buttons()
        self.update_info_label()
        if self.game.is_game_over:
            if self.game.is_win:
                win_sound.play()
                self.game_over(True)
            else:
                explosion_sound.play()
                self.reveal_all()
                self.game_over(False)

    def on_right_click(self, x, y):
        if self.game.is_game_over:
            return
        cell = self.game.board[x][y]
        if cell.revealed:
            return
        cell.toggle_flag()
        click_sound.play()
        self.update_buttons()
        self.update_info_label()

    def update_buttons(self):
        for (r, c), btn in self.buttons.items():
            cell = self.game.board[r][c]
            if cell.revealed:
                btn.config(relief=tk.SUNKEN, state=tk.DISABLED)
                if cell.is_mine:
                    btn.config(text="💣", disabledforeground="red", bg="pink")
                elif cell.adjacent_mines > 0:
                    btn.config(text=str(cell.adjacent_mines), fg=self.get_color(cell.adjacent_mines), bg="lightgrey")
                else:
                    btn.config(text="", bg="lightgrey")
            else:
                if cell.flagged:
                    btn.config(text="🚩", fg="red", bg="SystemButtonFace")
                else:
                    btn.config(text="", fg="black", bg="SystemButtonFace")

    def get_color(self, number):
        colors = {
            1: "blue",
            2: "green",
            3: "red",
            4: "darkblue",
            5: "brown",
            6: "cyan",
            7: "black",
            8: "grey",
        }
        return colors.get(number, "black")

    def reveal_all(self):
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                self.game.board[r][c].revealed = True
        self.update_buttons()

    def game_over(self, win, timeout=False):
        self.timer_running = False
        if win:
            msg = f"Congratulations {self.player_name}! You Win!\nYour score: {self.score}\nTime: {format_time(self.elapsed_time)}"
            name = self.player_name
            add_score(name, self.score)
        else:
            if timeout:
                msg = "Time's up! You lost."
            else:
                msg = "You hit a mine! Game Over."
            gameover_sound.play()
            self.flash_game_over()
        messagebox.showinfo("Game Over", msg)

    def flash_game_over(self):
        def flash(count):
            if count == 0:
                self.update_buttons()
                return
            for (r, c), btn in self.buttons.items():
                if count % 2 == 0:
                    btn.config(bg="red")
                else:
                    self.update_buttons()
            self.after(300, lambda: flash(count - 1))
        flash(6)

    def show_leaderboard(self):
        scores = load_leaderboard()
        text = "Leaderboard (Top 10 Scores):\n\n"
        for i, entry in enumerate(scores, 1):
            text += f"{i}. {entry['name']} - {entry['score']}\n"
        if not scores:
            text += "No scores yet."
        messagebox.showinfo("Leaderboard", text)

if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()
