from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from political_spectrum_analyzer.plotting.plot_2d import (
    draw_base,
    draw_people,
    draw_personalities,
)
from political_spectrum_analyzer.services.analysis_service import analyze_profile


class PlotFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Political positioning (2D)", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Economic axis: Left <-> Right | Societal axis: Libertarian <-> Authoritarian",
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

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = ttk.Frame(graph)
        toolbar.pack(fill="x")
        NavigationToolbar2Tk(self.canvas, toolbar)

        analysis_container = ttk.Frame(self)
        analysis_container.pack(fill="both", expand=False, pady=(8, 0))

        ttk.Label(
            analysis_container,
            text="Position analysis",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        self.analysis_text = tk.Text(
            analysis_container,
            height=8,
            wrap="word",
            bg="#ffffff",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
        )
        self.analysis_text.pack(fill="both", expand=True)
        self.analysis_text.configure(state="disabled")

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(8, 0))

        ttk.Button(
            bottom,
            text="Export chart (PNG)",
            command=self.save_figure,
        ).pack(side="left")

        ttk.Button(
            bottom,
            text="Back to main menu",
            command=self.back_to_main_menu,
        ).pack(side="left", padx=8)

        self._people_data_cache = []

    def create_plot(self, people):
        self._people_data_cache = list(people)
        self._redraw_all()
        self._update_analysis_panel()

    def _get_filtered_personalities(self):
        selection = (self.filter_var.get() or "None").strip()

        if selection == "None":
            return []

        if selection == "All":
            return self.app.personalities

        return [
            p
            for p in self.app.personalities
            if p.display_group.lower() == selection.lower()
        ]

    def _redraw_all(self):
        draw_base(self.ax)
        draw_personalities(self.ax, self._get_filtered_personalities())
        draw_people(self.ax, self._people_data_cache)
        self.fig.tight_layout()
        self.canvas.draw()

    def _format_analysis(self) -> str:
        if not self._people_data_cache:
            return "No profile to analyze."

        sections = []

        for person in self._people_data_cache:
            analysis = analyze_profile(
                person=person,
                personalities=self.app.personalities,
                top_n=3,
            )

            closest_lines = []
            for index, match in enumerate(analysis.closest_references, start=1):
                closest_lines.append(
                    f"   {index}. {match.name} ({match.display_group}) - distance: {match.distance}"
                )

            closest_block = "\n".join(closest_lines) if closest_lines else "   No reference available."

            sections.append(
                "\n".join(
                    [
                        f"Profile: {analysis.name}",
                        f"Coordinates: x={analysis.x}, y={analysis.y}",
                        f"Quadrant: {analysis.quadrant}",
                        f"Distance to center: {analysis.distance_to_center}",
                        "Closest references:",
                        closest_block,
                    ]
                )
            )

        return "\n\n" + ("-" * 72 + "\n\n").join(sections)

    def _update_analysis_panel(self):
        analysis = self._format_analysis()

        self.analysis_text.configure(state="normal")
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", analysis.strip())
        self.analysis_text.configure(state="disabled")

    def apply_filter(self):
        self._redraw_all()
        self._update_analysis_panel()

    def save_figure(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )

        if file_path:
            self.fig.savefig(file_path, dpi=300)
            messagebox.showinfo("Image export", f"Chart saved to: {file_path}")

    def back_to_main_menu(self):
        self._people_data_cache = []

        self.app.people_data.clear()
        self.app.current_index = 0
        self.app.num_people = 0

        self.analysis_text.configure(state="normal")
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.configure(state="disabled")

        try:
            self.filter_var.set("None")
        except Exception:
            pass

        try:
            self.app.frame_start.entry.delete(0, "end")
        except Exception:
            pass

        self.app.show_frame(self.app.frame_start)