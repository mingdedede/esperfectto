from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from app.utils.database import get_user_stats
from app.utils.engine import get_barista_rank, get_next_rank_info


class HomeScreen(Screen):
    rank_title = StringProperty("Rookie Barista")
    total_xp = NumericProperty(0)
    total_shots = NumericProperty(0)
    streak = NumericProperty(0)
    next_rank = StringProperty("")
    xp_to_next = NumericProperty(0)
    rank_progress = NumericProperty(0)

    def on_enter(self):
        self.refresh_stats()

    def refresh_stats(self):
        stats = get_user_stats()
        self.total_xp = stats["total_xp"]
        self.total_shots = stats["total_shots"]
        self.streak = stats["current_streak"]
        self.rank_title = get_barista_rank(self.total_xp)

        next_info = get_next_rank_info(self.total_xp)
        self.next_rank = next_info["next_rank"]
        self.xp_to_next = next_info["xp_needed"]
        self.rank_progress = next_info["progress"]

    def start_mission(self):
        self.manager.current = "input"

    def view_history(self):
        self.manager.current = "history"
