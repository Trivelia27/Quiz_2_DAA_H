import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import time
import pygame
import os
from game import MinesweeperGame
from utils import format_time, add_score, load_leaderboard

# ========== THEME COLORS ==========
COLOR_BG = "#1e1e2e"              
COLOR_ACCENT = "#b4befe"          
COLOR_DANGER = "#f38ba8"          
COLOR_PANEL = "#313244"          
COLOR_TEXT = "#cdd6f4"           
COLOR_BTN_BG = "#45475a"         
COLOR_BTN_FG = "#bac2de"          
COLOR_BTN_ACTIVE = "#89b4fa"     
COLOR_FLAG = "#f38ba8"            
COLOR_MINE = "#f38ba8"            
COLOR_CELL_REVEALED = "#313244"   
COLOR_CELL_UNREVEALED = "#1e1e2e" 
COLOR_PROGRESS_BG = "#313244"     
COLOR_PROGRESS_FG = "#89b4fa"     
COLOR_PROGRESS_DANGER = "#f38ba8" 
# ==================================

pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_sound(file_name):
    full_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(full_path):
        return pygame.mixer.Sound(full_path)
    else:
        print(f"[WARNING] Sound file not found: {file_name}")
        return None

click_sound = load_sound("./src/click.wav")
explosion_sound = load_sound("./src/explosion.wav")
win_sound = load_sound("./src/win.wav")

bg_music_path = os.path.join(BASE_DIR, "./src/background.mp3")
if os.path.exists(bg_music_path):
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
else:
    print("[WARNING] Background music not found. Skipping.")

# =================== GUI CLASS ========================

class StartScreen(tk.Frame):
    def __init__(self, master, start_callback, leaderboard_callback, about_callback):
        super().__init__(master, bg=COLOR_BG)
        self.start_callback = start_callback
        self.leaderboard_callback = leaderboard_callback
        self.about_callback = about_callback
        self.pack(fill="both", expand=True)

        # Logo/emoji
        tk.Label(self, text="💣", font=("Segoe UI Emoji", 48), bg=COLOR_BG, fg=COLOR_ACCENT).pack(pady=(30, 10))

        # Judul
        tk.Label(self, text="Welcome to Minesweeper!", font=("Segoe UI", 22, "bold"),
                 fg=COLOR_ACCENT, bg=COLOR_BG).pack(pady=(0, 10))

        # Deskripsi singkat
        tk.Label(self, text="Find all the mines without triggering any!\nFlag suspected mines and clear the board.",
                 font=("Segoe UI", 12), fg=COLOR_TEXT, bg=COLOR_BG).pack(pady=(0, 20))

        # Input nama
        tk.Label(self, text="Enter your name:", font=("Segoe UI", 14), fg=COLOR_ACCENT, bg=COLOR_BG).pack(pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self, textvariable=self.name_var, font=("Segoe UI", 14), bg=COLOR_PANEL, fg=COLOR_ACCENT,
                                   relief=tk.FLAT, highlightthickness=2, highlightbackground=COLOR_ACCENT, insertbackground=COLOR_ACCENT)
        self.name_entry.pack(pady=(0, 15), ipadx=10, ipady=5)
        self.name_entry.focus_set()

        # Tombol Start
        start_btn = tk.Button(self, text="Start Game", font=("Segoe UI", 14, "bold"),
                              bg=COLOR_ACCENT, fg=COLOR_BG, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE,
                              activeforeground=COLOR_BG, borderwidth=0, command=self.on_start)
        start_btn.pack(pady=5, ipadx=20, ipady=8)
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg=COLOR_BTN_ACTIVE))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=COLOR_ACCENT))

        # Tombol Leaderboard
        leaderboard_btn = tk.Button(self, text="Leaderboard", font=("Segoe UI", 14),
                                    bg=COLOR_BTN_BG, fg=COLOR_ACCENT, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE,
                                    activeforeground=COLOR_BG, borderwidth=0, command=self.leaderboard_callback)
        leaderboard_btn.pack(pady=5, ipadx=20, ipady=8)
        leaderboard_btn.bind("<Enter>", lambda e: leaderboard_btn.config(bg=COLOR_BTN_ACTIVE, fg=COLOR_BG))
        leaderboard_btn.bind("<Leave>", lambda e: leaderboard_btn.config(bg=COLOR_BTN_BG, fg=COLOR_ACCENT))

        # Tombol About
        about_btn = tk.Button(self, text="About", font=("Segoe UI", 14),
                              bg=COLOR_BTN_BG, fg=COLOR_ACCENT, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE,
                              activeforeground=COLOR_BG, borderwidth=0, command=self.about_callback)
        about_btn.pack(pady=5, ipadx=20, ipady=8)
        about_btn.bind("<Enter>", lambda e: about_btn.config(bg=COLOR_BTN_ACTIVE, fg=COLOR_BG))
        about_btn.bind("<Leave>", lambda e: about_btn.config(bg=COLOR_BTN_BG, fg=COLOR_ACCENT))

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
        self.geometry("650x720")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

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
        style.configure("blue.Horizontal.TProgressbar", troughcolor=COLOR_PROGRESS_BG, background=COLOR_PROGRESS_FG)
        style.configure("red.Horizontal.TProgressbar", troughcolor=COLOR_PROGRESS_BG, background=COLOR_PROGRESS_DANGER)

        self.start_screen = StartScreen(self, self.start_game, self.show_leaderboard, self.show_about)

    def show_about(self):
        messagebox.showinfo(
            "About Minesweeper Interactive",
            "Minesweeper Interactive\n\nCreated by Triana, Fela, and Miski. \n\nFind all the mines without triggering any!\nFlag suspected mines and clear the board.\n\nEnjoy the game!"
        )

    def start_game(self, player_name):
        self.player_name = player_name
        self.start_screen.pack_forget()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        # Top Frame with player info and level selector
        frame_top = tk.Frame(self, bg=COLOR_BG)
        frame_top.pack(pady=12, fill="x")

        tk.Label(frame_top, text=f"Player: {self.player_name}", font=("Segoe UI", 12, "italic"),
                 fg=COLOR_ACCENT, bg=COLOR_BG).pack(side=tk.LEFT, padx=15)

        tk.Label(frame_top, text="Select Level:", font=("Segoe UI", 12), fg=COLOR_ACCENT, bg=COLOR_BG).pack(side=tk.LEFT, padx=5)

        self.level_var = tk.StringVar(value=self.current_level)
        level_menu = ttk.Combobox(frame_top, textvariable=self.level_var, values=list(self.levels.keys()),
                                  state="readonly", width=15, font=("Segoe UI", 11))
        level_menu.pack(side=tk.LEFT)
        level_menu.bind("<<ComboboxSelected>>", self.change_level)

        # Timer label
        self.timer_label = tk.Label(self, text="⏰ Time: 00:00", font=("Segoe UI", 18, "bold"),
                                    fg=COLOR_ACCENT, bg=COLOR_BG)
        self.timer_label.pack(pady=5)

        # Progress bar for time limit
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=550,
                                            style="blue.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=5)

        # Score label
        self.score_label = tk.Label(self, text="⭐ Score: 0", font=("Segoe UI", 18, "bold"),
                                    fg=COLOR_ACCENT, bg=COLOR_BG)
        self.score_label.pack(pady=5)

        # Info label (mines left and flags)
        self.info_label = tk.Label(self, text="", font=("Segoe UI", 14), fg=COLOR_TEXT, bg=COLOR_BG)
        self.info_label.pack(pady=5)

        # Board Frame
        self.board_frame = tk.Frame(self, bg=COLOR_PANEL, bd=8, relief=tk.RIDGE, highlightbackground=COLOR_ACCENT, highlightthickness=2)
        self.board_frame.pack(pady=15, padx=15)

        # Bottom buttons frame
        btn_frame = tk.Frame(self, bg=COLOR_BG)
        btn_frame.pack(pady=10)

        self.reset_button = tk.Button(btn_frame, text="Reset Game", font=("Segoe UI", 14),
                                      bg=COLOR_ACCENT, fg=COLOR_BG, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE, activeforeground=COLOR_BG, borderwidth=0, command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.config(bg=COLOR_BTN_ACTIVE))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.config(bg=COLOR_ACCENT))

        self.leaderboard_button = tk.Button(btn_frame, text="Show Leaderboard", font=("Segoe UI", 14),
                                            bg=COLOR_BTN_BG, fg=COLOR_ACCENT, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE, activeforeground=COLOR_BG, borderwidth=0, command=self.show_leaderboard)
        self.leaderboard_button.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        self.leaderboard_button.bind("<Enter>", lambda e: self.leaderboard_button.config(bg=COLOR_BTN_ACTIVE, fg=COLOR_BG))
        self.leaderboard_button.bind("<Leave>", lambda e: self.leaderboard_button.config(bg=COLOR_BTN_BG, fg=COLOR_ACCENT))

        self.quit_button = tk.Button(btn_frame, text="Quit Game", font=("Segoe UI", 14),
                                     bg=COLOR_DANGER, fg=COLOR_BG, relief=tk.FLAT, activebackground=COLOR_BTN_ACTIVE, activeforeground=COLOR_BG, borderwidth=0, command=self.quit_game)
        self.quit_button.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        self.quit_button.bind("<Enter>", lambda e: self.quit_button.config(bg=COLOR_BTN_ACTIVE))
        self.quit_button.bind("<Leave>", lambda e: self.quit_button.config(bg=COLOR_DANGER))

        self.bind('<r>', lambda e: self.reset_game())

    def quit_game(self):
        self.destroy()

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

        cell_font = ("Consolas", 16, "bold")
        cell_width = 3
        cell_height = 1

        for r in range(rows):
            for c in range(cols):
                btn = tk.Button(
                    self.board_frame,
                    font=cell_font,
                    width=cell_width,
                    height=cell_height,
                    bg=COLOR_CELL_UNREVEALED,
                    fg=COLOR_BTN_FG,
                    relief=tk.RAISED,
                    activebackground=COLOR_ACCENT,
                    activeforeground=COLOR_BG,
                    command=lambda x=r, y=c: self.on_left_click(x, y)
                )
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
        if self.score < 0:
            self.score = 0
        self.score_label.config(text=f"⭐ Score: {self.score}")

    def update_info_label(self):
        mines_left = self.game.mines - sum(1 for row in self.game.board for cell in row if cell.flagged)
        self.info_label.config(text=f"Mines: {self.game.mines} | Flags Left: {mines_left}")

    def update_timer(self):
        if not self.timer_running:
            return
        self.elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"⏰ Time: {format_time(self.elapsed_time)}")

        if self.time_limit:
            percent = max(0, 100 - (self.elapsed_time / self.time_limit) * 100)
            self.progress_var.set(percent)
            if percent <= 20:
                self.progress_bar.config(style="red.Horizontal.TProgressbar")
            else:
                self.progress_bar.config(style="blue.Horizontal.TProgressbar")
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
        if click_sound:
            click_sound.play()
        self.game.reveal_cell(x, y)
        # Award points for revealing a safe cell (optional, e.g. +1 for each safe cell revealed)
        if not cell.is_mine and not cell.flagged:
            self.update_score(1)
        self.update_buttons()
        self.update_info_label()
        if self.game.is_game_over:
            if self.game.is_win:
                if win_sound:
                    win_sound.play()
                self.game_over(True)
            else:
                if explosion_sound:
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
        if click_sound:
            click_sound.play()
        # Scoring logic: +5 for correct flag, -2 for incorrect flag, 0 for unflagging
        if cell.flagged:
            if cell.is_mine:
                self.update_score(5)
            else:
                self.update_score(-2)
        else:
            # If unflagging, optionally revert score (optional, here we do nothing)
            pass
        self.update_buttons()
        self.update_info_label()

    def update_buttons(self):
        cell_font = ("Consolas", 16, "bold")
        cell_width = 3
        cell_height = 1
        for (r, c), btn in self.buttons.items():
            cell = self.game.board[r][c]
            btn.config(font=cell_font, width=cell_width, height=cell_height)  # Enforce size/font always
            if cell.revealed:
                btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg=COLOR_CELL_REVEALED, fg=COLOR_ACCENT, borderwidth=1, highlightbackground=COLOR_ACCENT)
                if cell.is_mine:
                    btn.config(text="💣", disabledforeground=COLOR_MINE, bg=COLOR_CELL_REVEALED)
                elif cell.adjacent_mines > 0:
                    btn.config(text=str(cell.adjacent_mines), fg=self.get_color(cell.adjacent_mines), bg=COLOR_CELL_REVEALED)
                else:
                    btn.config(text="", bg=COLOR_CELL_REVEALED)
            else:
                if cell.flagged:
                    btn.config(text="🚩", fg=COLOR_FLAG, bg=COLOR_CELL_UNREVEALED)
                else:
                    btn.config(text="", fg=COLOR_ACCENT, bg=COLOR_CELL_UNREVEALED)
    def get_color(self, number):
        colors = {
            1: "#61afef",  # blue
            2: "#e5c07b",  # yellow
            3: "#e06c75",  # red
            4: "#98c379",  # green
            5: "#c678dd",  # purple
            6: "#56b6c2",  # cyan
            7: "#abb2bf",  # light gray
            8: "#d19a66",  # orange
        }
        return colors.get(number, COLOR_ACCENT)

    def reveal_all(self):
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                self.game.board[r][c].revealed = True
        self.update_buttons()

    def game_over(self, win, timeout=False):
        self.timer_running = False
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)

        if win:
            msg = f"Congratulations {self.player_name}! You Win!\nYour score: {self.score}\nTime: {format_time(self.elapsed_time)}"
        else:
            if timeout:
                msg = f"Time's up!\nYour score: {self.score}"
            else:
                msg = f"You hit a mine! Game Over.\nYour score: {self.score}"

        # Kirim juga level dan durasi ke add_score
        add_score(self.player_name, self.score, self.current_level, self.elapsed_time)

        messagebox.showinfo("Game Over", msg)
        self.show_leaderboard()

    def show_leaderboard(self):
        scores = load_leaderboard()
        text = "Leaderboard (Top 10 Scores):\n\n"
        if not scores:
            text += "No scores yet."
        else:
            for i, entry in enumerate(scores, 1):
                name = entry.get('name', 'Unknown')
                score = entry.get('score', 0)
                level = entry.get('level', 'N/A')
                duration = entry.get('duration', 0)
                formatted_time = format_time(duration)
                text += f"{i}. {name} - {score} points - Level: {level} - Time: {formatted_time}\n"

        messagebox.showinfo("Leaderboard", text)

if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()