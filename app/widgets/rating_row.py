from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty


class RatingRow(BoxLayout):
    """A 1-5 rating row with label and toggle buttons.

    When a toggle is pressed, `rating_value` updates automatically.
    Parent screens read `rating_value` on submit.
    """
    label_text = StringProperty("")
    rating_value = NumericProperty(3)

    def set_rating(self, value: int):
        self.rating_value = value
