from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty


class ResultsScreen(Screen):
    session_id = NumericProperty(0)
    grind = NumericProperty(4)
    dose_grams = NumericProperty(18.0)
    dose_dial = NumericProperty(25)
    temp = NumericProperty(94)
    explanation = StringProperty("")
    confidence = StringProperty("low")
    bean_label = StringProperty("")
    machine_name = StringProperty("De'Longhi La Specialista Arte")

    # Bean quality score
    bean_score = NumericProperty(0)
    bean_score_label = StringProperty("")
    bean_score_source = StringProperty("")

    def go_to_feedback(self):
        feedback_screen = self.manager.get_screen("feedback")
        feedback_screen.session_id = self.session_id
        feedback_screen.bean_label = self.bean_label
        feedback_screen.reset_ratings()
        self.manager.current = "feedback"

    def go_back(self):
        self.manager.current = "input"
