"""
Esperfectto — Espresso Dial-In Assistant
for De'Longhi La Specialista Arte

Skip the 30-minute micro-adjustment phase.
Enter your bean → get optimal settings → pull → rate → learn.
"""

import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from kivy.config import Config
# Mobile-first: portrait, no resize
Config.set("graphics", "width", "390")
Config.set("graphics", "height", "844")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from app.screens.home import HomeScreen
from app.screens.input import InputScreen
from app.screens.results import ResultsScreen
from app.screens.feedback import FeedbackScreen
from app.screens.history import HistoryScreen
from app.widgets.rating_row import RatingRow  # noqa: F401 — needed for KV
from app.utils.database import init_db


class EsperfecttoApp(App):
    title = "Esperfectto"

    def build(self):
        # Initialize database
        init_db()

        # Load KV file
        kv_path = os.path.join(os.path.dirname(__file__), "kv", "esperfectto.kv")
        Builder.load_file(kv_path)

        # Screen manager with slide transitions
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(InputScreen(name="input"))
        sm.add_widget(ResultsScreen(name="results"))
        sm.add_widget(FeedbackScreen(name="feedback"))
        sm.add_widget(HistoryScreen(name="history"))

        return sm


if __name__ == "__main__":
    EsperfecttoApp().run()
