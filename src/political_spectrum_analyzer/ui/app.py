from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.domain.models import PersonResult, PersonScores
from political_spectrum_analyzer.services.personalities_service import load_personalities
from political_spectrum_analyzer.services.scoring_service import compute_person_result
from political_spectrum_analyzer.ui.form_frame import FormFrame
from political_spectrum_analyzer.ui.plot_frame import PlotFrame
from political_spectrum_analyzer.ui.start_frame import StartFrame


class WizardApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Political Spectrum Analyzer")
        self.geometry("1000x700")
        self.minsize(860, 620)
        self.configure(bg="#f5f5f5")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#f5f5f5")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background="#f5f5f5")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), background="#f5f5f5")
        style.configure("TLabel", font=("Segoe UI", 10), background="#f5f5f5")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10))

        self.num_people = 0
        self.current_index = 0
        self.people_data: list[PersonResult] = []
        self.personalities = load_personalities(PERSONALITIES_CSV_PATH)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=15, pady=15)

        self.frame_start = StartFrame(self.container, self)
        self.frame_form = FormFrame(self.container, self)
        self.frame_plot = PlotFrame(self.container, self)

        self.show_frame(self.frame_start)

    def show_frame(self, frame: ttk.Frame) -> None:
        for f in (self.frame_start, self.frame_form, self.frame_plot):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def go_to_form(self, nb: int) -> None:
        self.num_people = nb
        self.current_index = 0
        self.people_data.clear()
        self.frame_form.reset_form()
        self.show_frame(self.frame_form)

    def save_person_data(self, name: str, scores: dict[str, int]) -> None:
        person = PersonScores(name=name, scores=scores)
        result = compute_person_result(person)
        self.people_data.append(result)

    def next_person(self) -> None:
        self.current_index += 1
        if self.current_index < self.num_people:
            self.frame_form.reset_form()
        else:
            self.frame_plot.create_plot(self.people_data)
            self.show_frame(self.frame_plot)