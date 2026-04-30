from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from app.utils.database import get_all_sessions, get_favorite_bean


class HistoryScreen(Screen):
    favorite_bean = StringProperty("--")
    favorite_pulls = StringProperty("")
    favorite_rating = StringProperty("")
    sessions = ListProperty([])

    def on_enter(self):
        self.load_data()

    def load_data(self):
        # Favorite bean
        fav = get_favorite_bean()
        if fav:
            label = f"{fav['brand']} {fav['bean_name']}".strip()
            self.favorite_bean = label
            self.favorite_pulls = f"{fav['pull_count']} pulls"
            avg = fav["avg_rating"]
            self.favorite_rating = f"avg {avg}/5" if avg else ""
        else:
            self.favorite_bean = "No shots yet"
            self.favorite_pulls = ""
            self.favorite_rating = ""

        # All sessions
        raw = get_all_sessions(limit=100)
        self.sessions = raw
        self._build_session_list()

    def _build_session_list(self):
        container = self.ids.session_list
        container.clear_widgets()

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, RoundedRectangle
        from kivy.metrics import dp, sp
        from kivy.utils import get_color_from_hex

        for s in self.sessions:
            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                padding=dp(12),
                spacing=dp(4),
            )
            with card.canvas.before:
                Color(rgba=get_color_from_hex("#16213E"))
                bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
            card.bind(pos=lambda w, p, r=bg: setattr(r, "pos", p))
            card.bind(size=lambda w, s, r=bg: setattr(r, "size", s))

            # Row 1: bean name + date
            row1 = BoxLayout(size_hint_y=None, height=dp(22))
            bean_label = f"{s['brand']} {s['bean_name']}".strip()
            row1.add_widget(Label(
                text=bean_label,
                font_size=sp(14),
                bold=True,
                color=get_color_from_hex("#E8C170"),
                halign="left",
                text_size=(None, None),
                size_hint_x=0.65,
            ))
            # Format date nicely
            date_str = s.get("created_at", "")[:10]
            row1.add_widget(Label(
                text=date_str,
                font_size=sp(11),
                color=get_color_from_hex("#8888AA"),
                halign="right",
                text_size=(None, None),
                size_hint_x=0.35,
            ))
            card.add_widget(row1)

            # Row 2: settings
            roast = s.get("roast_level", "").replace("_", "-")
            grind = s.get("rec_grind", "?")
            dose = s.get("rec_dose_grams", "?")
            dial = s.get("rec_dose_dial", "?")
            temp = s.get("rec_temp", "?")
            settings_text = f"{roast}  |  grind {grind}  |  {dose}g  |  dial {dial}  |  {temp}°C"

            card.add_widget(Label(
                text=settings_text,
                font_size=sp(11),
                color=get_color_from_hex("#EAEAEA"),
                halign="left",
                text_size=(None, None),
                size_hint_y=None,
                height=dp(18),
            ))

            # Row 3: ratings
            overall = s.get("rating_overall")
            if overall:
                sweet = s.get("rating_sweetness", "-")
                acid = s.get("rating_acidity", "-")
                bitter = s.get("rating_bitterness", "-")
                body = s.get("rating_body", "-")
                rating_text = (
                    f"sweet {sweet}  acid {acid}  bitter {bitter}  "
                    f"body {body}  |  overall {overall}/5"
                )
                rating_color = "#4ADE80" if overall >= 4 else (
                    "#E8C170" if overall >= 3 else "#F87171"
                )
            else:
                rating_text = "not rated"
                rating_color = "#555577"

            card.add_widget(Label(
                text=rating_text,
                font_size=sp(11),
                color=get_color_from_hex(rating_color),
                halign="left",
                text_size=(None, None),
                size_hint_y=None,
                height=dp(18),
            ))

            container.add_widget(card)

    def go_back(self):
        self.manager.current = "home"
