from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.ocr import extract_scores_from_image


class FormFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        header = ttk.Frame(self)
        header.pack(fill="x")

        self.title_label = ttk.Label(header, text="Input form", style="Title.TLabel")
        self.title_label.pack(anchor="w")

        ttk.Label(
            header,
            text="For each person, enter a name and 16 scores between 0 and 100.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        scroll_container = ttk.Frame(self)
        scroll_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(scroll_container, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.inner_window, width=e.width))

        name_block = ttk.Frame(self.inner_frame)
        name_block.pack(fill="x", pady=(0, 10))

        ttk.Label(name_block, text="Name:", width=18).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.name_entry = ttk.Entry(name_block, width=25)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=5)

        self.btn_ocr = ttk.Button(
            name_block,
            text="Import from Politiscales screenshot (OCR)",
            command=self.import_from_screenshot,
        )
        self.btn_ocr.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

        self.entries: dict[str, ttk.Entry] = {}
        fields = ttk.Frame(self.inner_frame)
        fields.pack(fill="x")

        for i, var in enumerate(VARIABLE_NAMES):
            fr = ttk.Frame(fields)
            fr.grid(row=i // 2, column=i % 2, padx=10, pady=6, sticky="w")
            ttk.Label(fr, text=f"{var.replace('_', ' ').capitalize()} (0-100):").pack(anchor="w")
            e = ttk.Entry(fr, width=10)
            e.pack(anchor="w")
            self.entries[var] = e
            e.bind("<Return>", lambda ev: self.validate_form())

        self.btn_validate = ttk.Button(self, text="Validate & next person", command=self.validate_form)
        self.btn_validate.pack(pady=12)

        self.name_entry.bind("<Return>", lambda e: self.validate_form())
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def reset_form(self) -> None:
        idx = self.app.current_index + 1
        total = self.app.num_people
        self.title_label.config(text=f"Input for person {idx}/{total}")

        self.name_entry.delete(0, tk.END)
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        self.canvas.yview_moveto(0)
        self.name_entry.focus_set()

    def import_from_screenshot(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a Politiscales screenshot",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            scores = extract_scores_from_image(path)
        except Exception as exc:
            messagebox.showerror("OCR error", str(exc))
            return

        found = False
        for key, entry in self.entries.items():
            if key in scores:
                entry.delete(0, tk.END)
                entry.insert(0, str(scores[key]))
                if scores[key] != 0:
                    found = True

        if found:
            messagebox.showinfo("OCR", "Scores imported from screenshot. Please review them before validation.")
        else:
            messagebox.showwarning("OCR", "No score was detected automatically.")

    def validate_form(self) -> None:
        name = self.name_entry.get().strip() or f"Person_{self.app.current_index + 1}"

        scores: dict[str, int] = {}
        try:
            for key, entry in self.entries.items():
                value = entry.get().strip() or "0"
                value_int = int(value)
                if not (0 <= value_int <= 100):
                    raise ValueError
                scores[key] = value_int
        except Exception:
            messagebox.showerror("Error", "All scores must be integers between 0 and 100.")
            return

        self.app.save_person_data(name, scores)
        self.app.next_person()