#!/usr/bin/env python3
"""A small desktop interface for The Hat that Sorts (TM)."""

from __future__ import annotations

import random
import tkinter as tk
from math import ceil
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
BACKGROUND_IMAGE = Path(__file__).with_name("magical_background.png")


def result_column_count(group_count: int, maximum: int = MAX_RESULT_COLUMNS) -> int:
    """Return a readable number of result columns for the number of groups."""
    if group_count < 1:
        return 0
    return min(group_count, maximum)


def cover_subsample_factor(
    image_width: int, image_height: int, target_width: int, target_height: int
) -> int:
    """Return an integer downscale factor that keeps an image large enough to cover a target."""
    if min(image_width, image_height, target_width, target_height) < 1:
        raise ValueError("Image and target dimensions must be positive.")
    return max(1, min(image_width // target_width, image_height // target_height))


def cover_zoom_factor(
    image_width: int, image_height: int, target_width: int, target_height: int
) -> int:
    """Return an integer zoom factor that makes an image cover a target."""
    if min(image_width, image_height, target_width, target_height) < 1:
        raise ValueError("Image and target dimensions must be positive.")
    return max(1, ceil(target_width / image_width), ceil(target_height / image_height))


class SortingHatApp(tk.Tk):
    """Tkinter application that reveals one sorted student at a time."""

    def __init__(self) -> None:
        super().__init__()
        self.title(PROGRAM_NAME)
        self.configure(background=BACKGROUND)
        self.minsize(960, 700)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _event: self.attributes("-fullscreen", False))
        configure_styles(self)
        self._content: ttk.Frame | None = None
        self._content_window: int | None = None
        self._input_widgets: list[tk.Widget] = []
        self._build_background()
        self.file_path = tk.StringVar(value=str(DEFAULT_STUDENT_FILE))
        self.group_count = tk.IntVar(value=2)
        self._pending_assignments: list[tuple[int, str]] = []
        self._group_lists: list[tk.Listbox] = []
        self._group_text_positions: list[tuple[int, int]] = []
        self._revealed_counts: list[int] = []
        self._build_entry_screen()
        self.after(100, self._build_entry_screen)

    def _build_entry_screen(self) -> None:
        self._clear_screen()
        canvas = self._background
        canvas.update_idletasks()
        width = max(900, canvas.winfo_width())
        canvas.create_text(width // 2, 55, text=PROGRAM_NAME, fill="#fff4d6", font=("Georgia", 36, "bold"), tags="content")
        canvas.create_text(width // 2, 98, text="Places each student into their destined group using magic but not at all related to the Harry Potter series.", fill="#f4dca8", font=("Segoe UI", 16), tags="content")
        self._draw_top_hat(canvas, width // 2 - 136, 122, tags="content")

        label_x = width // 2 - 255
        control_y = 400
        canvas.create_text(label_x, control_y, text="Student list", anchor="w", fill="#fff4d6", font=("Segoe UI", 15, "bold"), tags="content")
        file_entry = ttk.Entry(canvas, textvariable=self.file_path, width=38)
        browse_button = ttk.Button(canvas, text="Browse…", command=self._choose_file)
        self._input_widgets.extend([file_entry, browse_button])
        canvas.create_window(width // 2 - 70, control_y + 36, window=file_entry, width=370, tags="content")
        canvas.create_window(width // 2 + 190, control_y + 36, window=browse_button, tags="content")
        canvas.create_text(label_x, control_y + 69, text="One student per line", anchor="w", fill="#f4dca8", font=("Segoe UI", 13), tags="content")
        canvas.create_text(label_x, control_y + 109, text="Number of groups", anchor="w", fill="#fff4d6", font=("Segoe UI", 15, "bold"), tags="content")
        group_spinbox = ttk.Spinbox(canvas, from_=1, to=99, textvariable=self.group_count, width=6)
        start_button = ttk.Button(canvas, text="Start sorting", style="Start.TButton", command=self._start_sorting)
        self._input_widgets.extend([group_spinbox, start_button])
        canvas.create_window(label_x + 55, control_y + 145, window=group_spinbox, tags="content")
        canvas.create_window(width // 2, control_y + 205, window=start_button, width=300, tags="content")

    @staticmethod
    def _draw_top_hat(canvas: tk.Canvas, x_offset: int = 0, y_offset: int = 0, tags: str = "") -> None:
        """Draw a simple top-hat illustration without external image files."""
        canvas.create_oval(53 + x_offset, 190 + y_offset, 220 + x_offset, 232 + y_offset, fill="#171717", outline=INK, width=3, tags=tags)
        canvas.create_rectangle(76 + x_offset, 53 + y_offset, 198 + x_offset, 202 + y_offset, fill="#1b1b1b", outline=INK, width=3, tags=tags)
        canvas.create_oval(76 + x_offset, 38 + y_offset, 198 + x_offset, 77 + y_offset, fill="#333333", outline=INK, width=3, tags=tags)
        canvas.create_rectangle(76 + x_offset, 150 + y_offset, 198 + x_offset, 172 + y_offset, fill=RED, outline=RED, tags=tags)
        canvas.create_line(90 + x_offset, 66 + y_offset, 90 + x_offset, 144 + y_offset, fill="#595959", width=3, tags=tags)
        canvas.create_arc(45 + x_offset, 180 + y_offset, 228 + x_offset, 239 + y_offset, start=190, extent=160, outline=GOLD, width=3, tags=tags)
        canvas.create_text(136 + x_offset, 262 + y_offset, text="Ready to sort!", fill="#fff4d6", font=("Georgia", 16, "italic"), tags=tags)

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
        canvas = self._background
        canvas.update_idletasks()
        width = max(900, canvas.winfo_width())
        columns = result_column_count(len(groups))
        canvas.create_text(
            width // 2, 64, text=PROGRAM_NAME, fill="#fff4d6",
            font=("Georgia", 36, "bold"), tags="content",
        )
        self._status_item = canvas.create_text(
            width // 2, 104, text="The hat is considering…", fill="#f4dca8",
            font=("Segoe UI", 16), tags="content",
        )
        horizontal_padding = 38
        card_gap = 20
        card_width = (width - horizontal_padding * 2 - card_gap * (columns - 1)) // columns
        card_height = max(175, 92 + max(len(group) for group in groups) * 34)
        self._group_text_positions = []
        self._revealed_counts = [0] * len(groups)
        for index, group in enumerate(groups):
            column = index % columns
            row = index // columns
            x1 = horizontal_padding + column * (card_width + card_gap)
            y1 = 138 + row * (card_height + card_gap)
            x2 = x1 + card_width
            y2 = y1 + card_height
            canvas.create_rectangle(
                x1, y1, x2, y2, outline="#e8bd59", width=2, fill="", tags="content"
            )
            canvas.create_text(
                x1 + 18, y1 + 16, text=f"Group {index + 1}", anchor="nw", fill="#ffe9aa",
                font=("Georgia", 21, "bold"), tags="content",
            )
            canvas.create_line(x1 + 18, y1 + 58, x2 - 18, y1 + 58, fill="#c38b22", tags="content")
            self._group_text_positions.append((x1 + 20, y1 + 76))

        button_y = 150 + ((len(groups) - 1) // columns + 1) * (card_height + card_gap)
        button = canvas.create_rectangle(
            width // 2 - 130, button_y, width // 2 + 130, button_y + 52,
            outline="#f2d88c", width=2, fill="", tags=("content", "restart"),
        )
        label = canvas.create_text(
            width // 2, button_y + 26, text="Sort another list", fill="#fff4d6",
            font=("Segoe UI", 15, "bold"), tags=("content", "restart"),
        )
        canvas.tag_bind("restart", "<Button-1>", lambda _event: self._build_entry_screen())
        canvas.tag_bind("restart", "<Enter>", lambda _event: canvas.itemconfigure(button, outline="#ffffff"))
        canvas.tag_bind("restart", "<Leave>", lambda _event: canvas.itemconfigure(button, outline="#f2d88c"))
        self._pending_assignments = [
            (group_index, student)
            for group_index, group in enumerate(groups)
            for student in group
        ]
        self.after(ASSIGNMENT_DELAY_MS, self._reveal_next_assignment)

    def _reveal_next_assignment(self) -> None:
        if not self._pending_assignments:
            self._background.itemconfigure(self._status_item, text="The sorting is complete!")
            return
        group_index, student = self._pending_assignments.pop(0)
        x, y = self._group_text_positions[group_index]
        line_number = self._revealed_counts[group_index]
        self._background.create_text(
            x, y + line_number * 32, text=student, anchor="nw", fill="#fffdf8",
            font=("Segoe UI", 16), tags="content",
        )
        self._revealed_counts[group_index] += 1
        self._background.itemconfigure(self._status_item, text=f"{student} joins Group {group_index + 1}")
        self.after(ASSIGNMENT_DELAY_MS, self._reveal_next_assignment)

    def _clear_screen(self) -> None:
        self._pending_assignments = []
        self._background.delete("content")
        for widget in self._input_widgets:
            widget.destroy()
        self._input_widgets = []
        if self._content is not None:
            self._content.destroy()
            self._content = None
            self._content_window = None

    def _build_background(self) -> None:
        """Show the generated magical artwork behind the light content panel."""
        self._background = tk.Canvas(self, bg="#171127", highlightthickness=0)
        self._background.pack(fill="both", expand=True)
        self._background_source_image = tk.PhotoImage(file=BACKGROUND_IMAGE)
        self._background_zoom: int | None = None
        self._background_image = self._background_source_image
        self._background_id = self._background.create_image(0, 0, anchor="nw", image=self._background_image)
        self._background.bind("<Configure>", self._resize_background)

    def _resize_background(self, event: tk.Event[tk.Misc]) -> None:
        zoom = cover_zoom_factor(
            self._background_source_image.width(), self._background_source_image.height(), event.width, event.height
        )
        if zoom != self._background_zoom:
            self._background_image = self._background_source_image.zoom(zoom, zoom)
            self._background.itemconfigure(self._background_id, image=self._background_image)
            self._background_zoom = zoom
        image_x = (event.width - self._background_image.width()) // 2
        image_y = (event.height - self._background_image.height()) // 2
        self._background.coords(self._background_id, image_x, image_y)
        if self._content_window is not None:
            self._background.coords(self._content_window, event.width // 2, 24)
            self._background.itemconfigure(self._content_window, width=max(720, event.width - 60))

    def _new_content_frame(self, padding: int) -> ttk.Frame:
        self._clear_screen()
        frame = ttk.Frame(self._background, padding=padding, style="App.TFrame")
        self._content = frame
        self._content_window = self._background.create_window(0, 24, anchor="n", window=frame)
        self._background.update_idletasks()
        self._resize_background(
            type("ResizeEvent", (), {"width": self._background.winfo_width(), "height": self._background.winfo_height()})()
        )
        return frame


def configure_styles(root: tk.Tk) -> None:
    """Set the visual theme on the application's own Tk window."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 14))
    style.configure("App.TFrame", background=BACKGROUND)
    style.configure("Card.TFrame", background="#fffdf8", relief="solid", borderwidth=1)
    style.configure("Title.TLabel", background=BACKGROUND, foreground=INK, font=("Georgia", 36, "bold"))
    style.configure("Subtitle.TLabel", background=BACKGROUND, foreground="#65594d", font=("Segoe UI", 16))
    style.configure("Field.TLabel", background="#fffdf8", foreground=INK, font=("Segoe UI", 15, "bold"))
    style.configure("Hint.TLabel", background="#fffdf8", foreground="#65594d", font=("Segoe UI", 13))
    style.configure("Group.TLabel", background="#fffdf8", foreground=RED, font=("Georgia", 21, "bold"))
    style.configure("TButton", font=("Segoe UI", 14), padding=7)
    style.configure("TEntry", font=("Segoe UI", 14), padding=6)
    style.configure("TSpinbox", font=("Segoe UI", 14), padding=6)
    style.configure("Start.TButton", background=GOLD, foreground="#ffffff", font=("Segoe UI", 17, "bold"), padding=12)
    style.map("Start.TButton", background=[("active", "#a97216")])


def main() -> None:
    app = SortingHatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
