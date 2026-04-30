from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock

from app.utils.bean_data import (
    BEAN_VARIETIES, suggest_brand, is_known_brand, get_countries_for_region,
)


class InputScreen(Screen):
    bean_name = StringProperty("Select bean...")
    brand = StringProperty("")
    roast_level = StringProperty("medium")
    origin = StringProperty("south_american")
    process_method = StringProperty("washed")
    country = StringProperty("")
    country_list = ListProperty([])

    # Validation state
    brand_suggestion = StringProperty("")
    brand_confirmed = BooleanProperty(False)
    validation_error = StringProperty("")

    def on_enter(self):
        self._update_countries()

    def set_roast(self, value: str):
        self.roast_level = value

    def set_origin(self, value: str):
        self.origin = value
        self.country = ""
        self._update_countries()

    def set_process(self, value: str):
        self.process_method = value

    def _update_countries(self):
        countries = get_countries_for_region(self.origin)
        if countries:
            self.country_list = countries
            if self.country not in countries:
                self.country = countries[0]
        else:
            self.country_list = []
            self.country = ""

    def on_brand_text(self, text: str):
        """Called when brand text changes — check for typos."""
        self.brand = text
        self.brand_confirmed = False
        self.brand_suggestion = ""
        self.validation_error = ""

        if not text.strip():
            return

        Clock.unschedule(self._check_brand)
        Clock.schedule_once(self._check_brand, 0.6)

    def _check_brand(self, dt=None):
        if not self.brand.strip():
            return
        if is_known_brand(self.brand):
            self.brand_confirmed = True
            self.brand_suggestion = ""
            return
        suggestion = suggest_brand(self.brand)
        if suggestion:
            self.brand_suggestion = suggestion

    def accept_suggestion(self):
        """User tapped the brand suggestion — accept it."""
        if self.brand_suggestion:
            self.brand = self.brand_suggestion
            self.brand_confirmed = True
            self.brand_suggestion = ""
            if hasattr(self.ids, "brand_input"):
                self.ids.brand_input.text = self.brand

    def confirm_new_brand(self):
        """User confirms this is a new/custom brand."""
        self.brand_confirmed = True
        self.brand_suggestion = ""
        self.validation_error = ""

    def submit(self):
        self.validation_error = ""

        # Validate bean name
        if not self.bean_name or self.bean_name == "Select bean...":
            self.validation_error = "Select a bean variety"
            return

        # Validate brand
        if not self.brand.strip():
            self.validation_error = "Enter a brand / roaster"
            return

        # Check brand
        if not self.brand_confirmed:
            if is_known_brand(self.brand):
                self.brand_confirmed = True
            else:
                suggestion = suggest_brand(self.brand)
                if suggestion:
                    self.brand_suggestion = suggestion
                    self.validation_error = f"Did you mean '{suggestion}'?"
                    return
                else:
                    self.validation_error = "New brand — tap Confirm to proceed"
                    return

        # Validate country for non-blend
        if self.origin not in ("blend",) and not self.country:
            self.validation_error = "Select a country"
            return

        from app.utils.engine import get_recommendation
        from app.utils.database import save_session
        from app.utils.scoring import estimate_bean_score

        rec = get_recommendation(
            roast_level=self.roast_level,
            origin=self.origin,
            process_method=self.process_method,
            bean_name=self.bean_name,
            brand=self.brand,
        )

        bean_score = estimate_bean_score(
            origin_country=self.country,
            bean_variety=self.bean_name,
            roast_level=self.roast_level,
            process_method=self.process_method,
        )

        session_id = save_session(
            bean_name=self.bean_name.strip(),
            brand=self.brand.strip(),
            roast_level=self.roast_level,
            origin=self.origin,
            process_method=self.process_method,
            rec_grind=rec["grind"],
            rec_dose_grams=rec["dose_grams"],
            rec_dose_dial=rec["dose_dial"],
            rec_temp=rec["temp"],
            rec_explanation=rec["explanation"],
        )

        results_screen = self.manager.get_screen("results")
        results_screen.session_id = session_id
        results_screen.grind = rec["grind"]
        results_screen.dose_grams = rec["dose_grams"]
        results_screen.dose_dial = rec["dose_dial"]
        results_screen.temp = rec["temp"]
        results_screen.explanation = rec["explanation"]
        results_screen.confidence = rec["confidence"]
        results_screen.bean_label = f"{self.brand} {self.bean_name}".strip()
        results_screen.bean_score = bean_score["score"]
        results_screen.bean_score_label = bean_score["label"]
        results_screen.bean_score_source = bean_score["source"]

        self.manager.current = "results"

    def go_back(self):
        self.manager.current = "home"
