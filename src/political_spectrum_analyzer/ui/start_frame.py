from __future__ import annotations

from tkinter import messagebox
from tkinter import ttk


class StartFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(
            self,
            text="Political Spectrum Analyzer",
            style="Title.TLabel",
        ).pack(pady=(10, 5))

        ttk.Label(
            self,
            text="Enter the number of people to compare, then fill in their 16 scores.",
            style="Subtitle.TLabel",
            wraplength=700,
            justify="center",
        ).pack(pady=(0, 20))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Number of people:", anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry = ttk.Entry(form, width=10)
        self.entry.grid(row=0, column=1, pady=5, sticky="w")

        ttk.Button(self, text="Start", command=self.on_next).pack(pady=20)
        self.entry.bind("<Return>", lambda e: self.on_next())

    def on_next(self) -> None:
        try:
            n = int(self.entry.get())
            if n <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Please enter a strictly positive integer.")
            return

        self.app.go_to_form(n)