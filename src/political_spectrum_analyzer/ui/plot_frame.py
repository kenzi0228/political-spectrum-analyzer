from __future__ import annotations

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import tkinter as tk

from tkinter import filedialog, messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from political_spectrum_analyzer.plotting.plot_2d import draw_base, draw_people, draw_personalities


class PlotFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Political positioning (2D)", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Economic axis: Left â†” Right | Societal axis: Libertarian â†” Authoritarian",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", pady=(0, 8))

        ttk.Label(ctrl, text="Personality filter:", anchor="w").pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="None")
        categories = sorted({p.display_group for p in self.app.personalities})

        self.filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.filter_var,
            state="readonly",
            width=22,
            values=["None", "All"] + categories,
        )
        self.filter_combo.pack(side="left")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Button(ctrl, text="Apply", command=self.apply_filter).pack(side="left", padx=8)

        graph = ttk.Frame(self)
        graph.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = ttk.Frame(graph)
        toolbar.pack(fill="x")
        NavigationToolbar2Tk(self.canvas, toolbar)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(8, 0))

        ttk.Button(bottom, text="Export chart (PNG)", command=self.save_figure).pack(side="left")

        self._people_data_cache = []

    def create_plot(self, people):
        self._people_data_cache = list(people)
        self._redraw_all()

    def _get_filtered_personalities(self):
        selection = (self.filter_var.get() or "None").strip()

        if selection == "None":
            return []
        if selection == "All":
            return self.app.personalities
        return [p for p in self.app.personalities if p.display_group.lower() == selection.lower()]

    def _redraw_all(self):
        draw_base(self.ax)
        draw_personalities(self.ax, self._get_filtered_personalities())
        draw_people(self.ax, self._people_data_cache)
        self.fig.tight_layout()
        self.canvas.draw()

    def apply_filter(self):
        self._redraw_all()

    def save_figure(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300)
            messagebox.showinfo("Image export", f"Chart saved to: {file_path}")