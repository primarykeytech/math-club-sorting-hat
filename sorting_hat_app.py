#!/usr/bin/env python3
"""A small desktop interface for The Hat that Sorts (TM)."""

from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Sequence

from sorting_hat import PROGRAM_NAME, assign_groups, read_students


BACKGROUND = "#f6f0e4"
INK = "#2b1b10"
GOLD = "#c38b22"
RED = "#7e2636"
ASSIGNMENT_DELAY_MS = 650
MAX_RESULT_COLUMNS = 3
DEFAULT_STUDENT_FILE = Path(__file__).with_name("students.txt")


def result_column_count(group_count: int, maximum: int = MAX_RESULT_COLUMNS) -> int:
    """Return a readable number of result columns for the number of groups."""
    if group_count < 1:
        return 0
    return min(group_count, maximum)


class SortingHatApp(tk.Tk):
    """Tkinter application that reveals one sorted student at a time."""

    def __init__(self) -> None:
        super().__init__()
        self.title(PROGRAM_NAME)
        self.configure(background=BACKGROUND)
        self.minsize(720, 580)
        configure_styles(self)
        self.file_path = tk.StringVar(value=str(DEFAULT_STUDENT_FILE))
        self.group_count = tk.IntVar(value=2)
        self._pending_assignments: list[tuple[int, str]] = []
        self._group_lists: list[tk.Listbox] = []
        self._build_entry_screen()

    def _build_entry_screen(self) -> None:
        self._clear_screen()
        frame = ttk.Frame(self, padding=30, style="App.TFrame")
        frame.pack(expand=True, fill="both")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        title = ttk.Label(frame, text=PROGRAM_NAME, style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 4))
        subtitle = ttk.Label(
            frame,
            text="Place each student into their destined group.",
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 22))

        hat = tk.Canvas(frame, width=270, height=260, bg=BACKGROUND, highlightthickness=0)
        hat.grid(row=2, column=0, padx=(0, 25), pady=10, sticky="n")
        self._draw_top_hat(hat)

        controls = ttk.Frame(frame, padding=18, style="Card.TFrame")
        controls.grid(row=2, column=1, sticky="nsew", pady=10)
        ttk.Label(controls, text="Student list", style="Field.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Entry(controls, textvariable=self.file_path, width=30).grid(
            row=1, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Browse…", command=self._choose_file).grid(row=1, column=1)
        ttk.Label(
            controls, text="One student per line", style="Hint.TLabel"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 18))

        ttk.Label(controls, text="Number of groups", style="Field.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Spinbox(controls, from_=1, to=99, textvariable=self.group_count, width=6).grid(
            row=4, column=0, sticky="w"
        )
        ttk.Button(controls, text="Start sorting", style="Start.TButton", command=self._start_sorting).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(28, 0)
        )
        controls.columnconfigure(0, weight=1)

    @staticmethod
    def _draw_top_hat(canvas: tk.Canvas) -> None:
        """Draw a simple top-hat illustration without external image files."""
        canvas.create_oval(53, 190, 220, 232, fill="#171717", outline=INK, width=3)
        canvas.create_rectangle(76, 53, 198, 202, fill="#1b1b1b", outline=INK, width=3)
        canvas.create_oval(76, 38, 198, 77, fill="#333333", outline=INK, width=3)
        canvas.create_rectangle(76, 150, 198, 172, fill=RED, outline=RED)
        canvas.create_line(90, 66, 90, 144, fill="#595959", width=3)
        canvas.create_arc(45, 180, 228, 239, start=190, extent=160, outline=GOLD, width=3)
        canvas.create_text(136, 246, text="Ready to sort!", fill=INK, font=("Georgia", 13, "italic"))

    def _choose_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Choose a student list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if selected:
            self.file_path.set(selected)

    def _start_sorting(self) -> None:
        try:
            path = Path(self.file_path.get().strip())
            if not self.file_path.get().strip():
                raise ValueError("Choose a student list first.")
            groups = assign_groups(read_students(path), self.group_count.get(), random.Random())
        except (ValueError, tk.TclError) as error:
            messagebox.showerror("Unable to sort", str(error), parent=self)
            return

        self._show_results(groups)

    def _show_results(self, groups: Sequence[Sequence[str]]) -> None:
        self._clear_screen()
        frame = ttk.Frame(self, padding=26, style="App.TFrame")
        frame.pack(expand=True, fill="both")
        ttk.Label(frame, text=PROGRAM_NAME, style="Title.TLabel").pack()
        self.status = ttk.Label(frame, text="The hat is considering…", style="Subtitle.TLabel")
        self.status.pack(pady=(3, 22))

        columns = result_column_count(len(groups))
        results = ttk.Frame(frame, style="App.TFrame")
        results.pack(expand=True, fill="both")
        for column in range(columns):
            results.columnconfigure(column, weight=1, uniform="groups")
        self._group_lists = []
        for index, group in enumerate(groups):
            column = index % columns
            row = index // columns
            card = ttk.Frame(results, padding=12, style="Card.TFrame")
            card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
            ttk.Label(card, text=f"Group {index + 1}", style="Group.TLabel").pack(anchor="w")
            student_list = tk.Listbox(
                card, height=max(3, len(group)), bg="#fffdf8", fg=INK, borderwidth=0,
                highlightthickness=0, font=("Segoe UI", 11), activestyle="none",
            )
            student_list.pack(fill="both", expand=True, pady=(8, 0))
            self._group_lists.append(student_list)

        ttk.Button(frame, text="Sort another list", command=self._build_entry_screen).pack(pady=(18, 0))
        self._pending_assignments = [
            (group_index, student)
            for group_index, group in enumerate(groups)
            for student in group
        ]
        self.after(ASSIGNMENT_DELAY_MS, self._reveal_next_assignment)

    def _reveal_next_assignment(self) -> None:
        if not self._pending_assignments:
            self.status.configure(text="The sorting is complete!")
            return
        group_index, student = self._pending_assignments.pop(0)
        self._group_lists[group_index].insert("end", student)
        self.status.configure(text=f"{student} joins Group {group_index + 1}")
        self.after(ASSIGNMENT_DELAY_MS, self._reveal_next_assignment)

    def _clear_screen(self) -> None:
        for child in self.winfo_children():
            child.destroy()


def configure_styles(root: tk.Tk) -> None:
    """Set the visual theme on the application's own Tk window."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("App.TFrame", background=BACKGROUND)
    style.configure("Card.TFrame", background="#fffdf8", relief="solid", borderwidth=1)
    style.configure("Title.TLabel", background=BACKGROUND, foreground=INK, font=("Georgia", 27, "bold"))
    style.configure("Subtitle.TLabel", background=BACKGROUND, foreground="#65594d", font=("Segoe UI", 11))
    style.configure("Field.TLabel", background="#fffdf8", foreground=INK, font=("Segoe UI", 10, "bold"))
    style.configure("Hint.TLabel", background="#fffdf8", foreground="#65594d", font=("Segoe UI", 9))
    style.configure("Group.TLabel", background="#fffdf8", foreground=RED, font=("Georgia", 15, "bold"))
    style.configure("Start.TButton", background=GOLD, foreground="#ffffff", font=("Segoe UI", 11, "bold"), padding=9)
    style.map("Start.TButton", background=[("active", "#a97216")])


def main() -> None:
    app = SortingHatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
