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
    NONE_VALUE,
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

        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(0, 8))

        # ------------------------------------------------------------
        # Filters row
        # ------------------------------------------------------------
        filters_row = ttk.LabelFrame(controls, text="Reference filters")
        filters_row.pack(fill="x", padx=0, pady=(0, 6))

        self.group_filter_var = tk.StringVar(value=NONE_VALUE)
        self.country_filter_var = tk.StringVar(value=NONE_VALUE)
        self.period_filter_var = tk.StringVar(value=NONE_VALUE)
        self.ideology_filter_var = tk.StringVar(value=NONE_VALUE)

        self._add_filter_control(
            parent=filters_row,
            label="Group",
            variable=self.group_filter_var,
            values=get_unique_values(self.app.personalities, "display_group"),
            column=0,
            width=18,
        )

        self._add_filter_control(
            parent=filters_row,
            label="Country",
            variable=self.country_filter_var,
            values=get_unique_values(self.app.personalities, "country"),
            column=1,
            width=20,
        )

        self._add_filter_control(
            parent=filters_row,
            label="Period",
            variable=self.period_filter_var,
            values=get_unique_values(self.app.personalities, "period"),
            column=2,
            width=18,
        )

        self._add_filter_control(
            parent=filters_row,
            label="Ideology",
            variable=self.ideology_filter_var,
            values=get_unique_values(self.app.personalities, "ideology_family"),
            column=3,
            width=24,
        )

        ttk.Button(
            filters_row,
            text="Apply filters",
            command=self.apply_filter,
        ).grid(row=0, column=8, padx=(12, 4), pady=6, sticky="w")

        ttk.Button(
            filters_row,
            text="Clear filters",
            command=self.clear_filters,
        ).grid(row=0, column=9, padx=4, pady=6, sticky="w")

        self.reference_count_var = tk.StringVar(value="Displayed references: 0")
        ttk.Label(
            filters_row,
            textvariable=self.reference_count_var,
            anchor="w",
        ).grid(row=0, column=10, padx=(12, 4), pady=6, sticky="w")

        for column in range(11):
            filters_row.columnconfigure(column, weight=0)

        filters_row.columnconfigure(10, weight=1)

        # ------------------------------------------------------------
        # Actions row
        # ------------------------------------------------------------
        actions_row = ttk.LabelFrame(controls, text="Actions")
        actions_row.pack(fill="x", padx=0, pady=(0, 0))

        ttk.Button(
            actions_row,
            text="Reset graph view",
            command=self.reset_graph_view,
        ).pack(side="left", padx=(8, 6), pady=6)

        ttk.Button(
            actions_row,
            text="Export chart (PNG)",
            command=self.save_figure,
        ).pack(side="left", padx=6, pady=6)

        ttk.Button(
            actions_row,
            text="Export results (CSV)",
            command=self.open_csv_export_dialog,
        ).pack(side="left", padx=6, pady=6)

        ttk.Button(
            actions_row,
            text="Back to main menu",
            command=self.back_to_main_menu,
        ).pack(side="left", padx=6, pady=6)

        ttk.Label(
            actions_row,
            text="Tip: keep filters on None to hide references, use Any to display all values.",
            anchor="w",
        ).pack(side="left", padx=(16, 6), pady=6)

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
        self._update_reference_count()

    def _add_filter_control(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        values: list[str],
        column: int,
        width: int,
    ) -> None:
        container = ttk.Frame(parent)
        container.grid(row=0, column=column, padx=(8, 6), pady=6, sticky="w")

        ttk.Label(container, text=f"{label}:").pack(side="left", padx=(0, 4))

        combo = ttk.Combobox(
            container,
            textvariable=variable,
            state="readonly",
            width=width,
            values=values,
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda event: self.apply_filter())

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
        filtered_personalities = self._get_filtered_personalities()

        draw_base(self.ax)
        draw_personalities(self.ax, filtered_personalities)
        draw_people(self.ax, self._people_data_cache)
        self.fig.tight_layout()
        self.canvas.draw()

        self._update_reference_count(filtered_personalities)

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

    def _update_reference_count(self, filtered_personalities=None):
        if filtered_personalities is None:
            filtered_personalities = self._get_filtered_personalities()

        total_references = len(self.app.personalities)
        displayed_references = len(list(filtered_personalities))

        self.reference_count_var.set(
            f"Displayed references: {displayed_references} / {total_references}"
        )

    def apply_filter(self):
        self._redraw_all()
        self._update_analysis_panel()

    def clear_filters(self):
        self.group_filter_var.set(NONE_VALUE)
        self.country_filter_var.set(NONE_VALUE)
        self.period_filter_var.set(NONE_VALUE)
        self.ideology_filter_var.set(NONE_VALUE)
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