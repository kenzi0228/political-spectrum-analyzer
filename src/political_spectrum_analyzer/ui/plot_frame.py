from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from political_spectrum_analyzer.plotting.plot_2d import (
    draw_base,
    draw_people,
    draw_personalities,
)
from political_spectrum_analyzer.services.analysis_service import analyze_profile
from political_spectrum_analyzer.services.export_results_service import export_analysis_to_csv
from political_spectrum_analyzer.services.personality_filter_service import (
    ANY_VALUE,
    filter_personalities,
    get_unique_values,
)


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

        ttk.Label(ctrl, text="Group:", anchor="w").pack(side="left", padx=(0, 4))
        self.group_filter_var = tk.StringVar(value=ANY_VALUE)
        self.group_filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.group_filter_var,
            state="readonly",
            width=16,
            values=get_unique_values(self.app.personalities, "display_group"),
        )
        self.group_filter_combo.pack(side="left", padx=(0, 8))
        self.group_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(ctrl, text="Country:", anchor="w").pack(side="left", padx=(0, 4))
        self.country_filter_var = tk.StringVar(value=ANY_VALUE)
        self.country_filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.country_filter_var,
            state="readonly",
            width=18,
            values=get_unique_values(self.app.personalities, "country"),
        )
        self.country_filter_combo.pack(side="left", padx=(0, 8))
        self.country_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(ctrl, text="Period:", anchor="w").pack(side="left", padx=(0, 4))
        self.period_filter_var = tk.StringVar(value=ANY_VALUE)
        self.period_filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.period_filter_var,
            state="readonly",
            width=16,
            values=get_unique_values(self.app.personalities, "period"),
        )
        self.period_filter_combo.pack(side="left", padx=(0, 8))
        self.period_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(ctrl, text="Ideology:", anchor="w").pack(side="left", padx=(0, 4))
        self.ideology_filter_var = tk.StringVar(value=ANY_VALUE)
        self.ideology_filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.ideology_filter_var,
            state="readonly",
            width=20,
            values=get_unique_values(self.app.personalities, "ideology_family"),
        )
        self.ideology_filter_combo.pack(side="left", padx=(0, 8))
        self.ideology_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Button(ctrl, text="Apply", command=self.apply_filter).pack(side="left", padx=(0, 8))

        ttk.Button(
            ctrl,
            text="Clear filters",
            command=self.clear_filters,
        ).pack(side="left", padx=(0, 8))

        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Button(
            ctrl,
            text="Reset graph view",
            command=self.reset_graph_view,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            ctrl,
            text="Export chart (PNG)",
            command=self.save_figure,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            ctrl,
            text="Export results (CSV)",
            command=self.open_csv_export_dialog,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            ctrl,
            text="Back to main menu",
            command=self.back_to_main_menu,
        ).pack(side="left")

        graph = ttk.Frame(self)
        graph.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

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

        self._people_data_cache = []

    def create_plot(self, people):
        self._people_data_cache = list(people)
        self._redraw_all()
        self._update_analysis_panel()

    def _get_filtered_personalities(self):
        return filter_personalities(
            personalities=self.app.personalities,
            display_group=self.group_filter_var.get(),
            country=self.country_filter_var.get(),
            period=self.period_filter_var.get(),
            ideology_family=self.ideology_filter_var.get(),
        )

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

    def clear_filters(self):
        self.group_filter_var.set(ANY_VALUE)
        self.country_filter_var.set(ANY_VALUE)
        self.period_filter_var.set(ANY_VALUE)
        self.ideology_filter_var.set(ANY_VALUE)
        self.apply_filter()

    def reset_graph_view(self):
        self._redraw_all()

    def save_figure(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )

        if file_path:
            self.fig.savefig(file_path, dpi=300)
            messagebox.showinfo("Image export", f"Chart saved to: {file_path}")

    def open_csv_export_dialog(self):
        if not self._people_data_cache:
            messagebox.showwarning("CSV export", "No profile is available to export.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Export results to CSV")
        dialog.geometry("480x280")
        dialog.minsize(440, 260)
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text="Choose what should be included in the CSV export.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", padx=12, pady=(12, 8))

        export_mode_var = tk.StringVar(value="profiles_only")

        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill="x", padx=12, pady=4)

        modes = [
            ("Profiles only", "profiles_only"),
            ("Profiles + closest references", "closest_references"),
            ("Profiles + all references", "all_references"),
            ("Profiles + current filtered references", "filtered_references"),
        ]

        for label, value in modes:
            ttk.Radiobutton(
                options_frame,
                text=label,
                value=value,
                variable=export_mode_var,
            ).pack(anchor="w", pady=2)

        closest_frame = ttk.Frame(dialog)
        closest_frame.pack(fill="x", padx=12, pady=(8, 4))

        ttk.Label(closest_frame, text="Closest references count:").pack(side="left")

        closest_count_var = tk.StringVar(value="3")
        ttk.Spinbox(
            closest_frame,
            from_=1,
            to=20,
            textvariable=closest_count_var,
            width=5,
        ).pack(side="left", padx=8)

        ttk.Label(
            dialog,
            text="Note: current filtered references depend on the selected filters above.",
            wraplength=430,
        ).pack(anchor="w", padx=12, pady=(6, 0))

        button_bar = ttk.Frame(dialog)
        button_bar.pack(fill="x", padx=12, pady=(12, 12))

        def export_csv():
            try:
                closest_count = int(closest_count_var.get())
                if closest_count <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("CSV export", "Closest references count must be a positive integer.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                title="Save analysis export",
            )

            if not file_path:
                return

            mode = export_mode_var.get()
            filtered_personalities = self._get_filtered_personalities()

            if mode == "filtered_references" and not filtered_personalities:
                messagebox.showwarning(
                    "CSV export",
                    "No references match the current filters. "
                    "Adjust filters first or use another export mode.",
                )
                return

            export_analysis_to_csv(
                file_path=file_path,
                people=self._people_data_cache,
                personalities=self.app.personalities,
                mode=mode,
                closest_count=closest_count,
                filtered_personalities=filtered_personalities,
            )

            dialog.destroy()
            messagebox.showinfo("CSV export", f"Results exported to: {file_path}")

        ttk.Button(button_bar, text="Export", command=export_csv).pack(side="left")
        ttk.Button(button_bar, text="Cancel", command=dialog.destroy).pack(side="left", padx=8)

    def back_to_main_menu(self):
        self._people_data_cache = []

        self.app.people_data.clear()
        self.app.current_index = 0
        self.app.num_people = 0

        self.analysis_text.configure(state="normal")
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.configure(state="disabled")

        try:
            self.clear_filters()
        except Exception:
            pass

        try:
            self.app.frame_start.entry.delete(0, "end")
        except Exception:
            pass

        self.app.show_frame(self.app.frame_start)