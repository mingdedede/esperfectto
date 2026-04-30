from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from app.utils.database import save_feedback, update_stats_after_session
from app.utils.engine import calculate_xp


class FeedbackScreen(Screen):
    session_id = NumericProperty(0)
    bean_label = StringProperty("")
    sweetness = NumericProperty(3)
    acidity = NumericProperty(3)
    bitterness = NumericProperty(3)
    body = NumericProperty(3)
    overall = NumericProperty(3)

    def reset_ratings(self):
        self.sweetness = 3
        self.acidity = 3
        self.bitterness = 3
        self.body = 3
        self.overall = 3

    def submit_feedback(self):
        # Read actual values from RatingRow widgets
        sweetness = self.ids.sweetness_row.rating_value
        acidity = self.ids.acidity_row.rating_value
        bitterness = self.ids.bitterness_row.rating_value
        body = self.ids.body_row.rating_value
        overall = self.ids.overall_row.rating_value

        save_feedback(
            session_id=self.session_id,
            sweetness=sweetness,
            acidity=acidity,
            bitterness=bitterness,
            body=body,
            overall=overall,
        )

        xp = calculate_xp(overall)
        update_stats_after_session(xp)

        self.manager.current = "home"

    def skip_feedback(self):
        update_stats_after_session(10)
        self.manager.current = "home"
