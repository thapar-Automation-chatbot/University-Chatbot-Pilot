# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re

#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


POSSIBLE_GRADES = {"a", "b", "c", "e", "f", "i", "x", "ra"}
# add more
PROJECT_BASED_COURSES = {
    "uta013",
    "uta014",
    "ucs749",
    "ucs896",
    "umt893",
    "umt699",
    "uta016",
    "uta024",
    "ulc691",
    "ubt891",
    "uce692",
    "uce795",
}


class ValidateGradeEligibilityForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_grade_eligibility_form"

    def validate_current_grade(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate current grade"""
        if slot_value.lower() not in POSSIBLE_GRADES:
            print(slot_value)
            dispatcher.utter_message("Enter a valid Grade")
            return {"current_grade": None}
        return {"current_grade": slot_value.lower()}


class ActionGradeUpgradeEligibility(Action):
    """to handle grade upgradation"""

    def name(self) -> Text:
        return "action_grade_upgrade_eligiblity"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        current_grade = tracker.get_slot("current_grade")
        upgradation_mode = tracker.get_slot("upgradation_mode")

        if upgradation_mode == "summer":
            if current_grade == "a":
                dispatcher.utter_message(
                    "you cannot improve A/A- grades in summer semester"
                )
            else:
                if current_grade == {"b", "c"}:
                    dispatcher.utter_message(
                        "Students with {} / {}- grades are eligible for grade upgrades in summer semester.".format(
                            current_grade.upper(), current_grade.upper()
                        )
                    )
                else:
                    dispatcher.utter_message(
                        "Students with {} grades are eligible for grade upgrades in summer semester.".format(
                            current_grade.upper()
                        )
                    )

        elif upgradation_mode == "auxiliary":
            if current_grade in {"c", "b"}:
                dispatcher.utter_message(
                    "Only students with E grade or lower can appear for Auxilary Examination"
                )
            else:
                dispatcher.utter_message(
                    "Students with E grade can appear for Auxilary Exams."
                )
        else:
            dispatcher.utter_message("Backlog Case - solve later ")

        []


class ValidateSelfStudyEligibilityForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_self_study_eligibility_form"

    def validate_current_grade(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate current grade"""
        if slot_value.lower() not in POSSIBLE_GRADES:
            print(slot_value)
            dispatcher.utter_message("Enter a valid Grade")
            return {"current_grade": None}
        return {"current_grade": slot_value.lower()}

    def validate_subject(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate subject by regex"""
        regex = r"^(U|u|P|p)[A-Za-z]{2}\d{3}$"
        if not re.match(regex, slot_value):
            dispatcher.utter_message("Enter a valid Code")
            return {"subject": None}
        return {"subject": slot_value.lower()}


class ActionSelfStudyCondition(Action):
    """handle queries related to self and regular mode of study"""

    def name(self) -> Text:
        return "action_self_study_condition"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        current_grade = tracker.get_slot("current_grade")
        subject = tracker.get_slot("subject")
        subject = subject.lower()
        if subject in PROJECT_BASED_COURSES:
            dispatcher.utter_message(
                "The project based courses such as Engineering Design-1, Engineering Design-2, Capstone Project, etc. cannot be offered as self-study mode. And will only be offered in regular mode."
            )
        else:
            if current_grade.lower() in {"c", "b"}:
                dispatcher.utter_message(
                    "Students with B / B- / C / C- grades are eligible for both modes "
                )
            elif current_grade.lower() == "e":
                dispatcher.utter_message(
                    "Students with an E grade can choose self-study mode in {} if they had scored 25 marks or more out of 100".format(
                        subject.upper()
                    )
                )
            else:
                dispatcher.utter_message(
                    "Students with a grade {} are only eligble for Regular mode of study".format(
                        current_grade.upper()
                    )
                )

        return []


class ActionGeneralInfo(Action):
    def name(self):
        return "action_general_info"

    def run(self, dispatcher, tracker, domain):
        # Get the value of the 'purpose' slot
        purpose = tracker.get_slot("purpose")
        print(purpose)
        if purpose == "registration":
            # Provide a response related to registration details
            dispatcher.utter_message(
                "Here's some information about registration details for the summer semester."
            )
        elif purpose == "tenure_of_summer_term":
            # Provide a response related to the tenure of the summer term
            dispatcher.utter_message("The summer term typically lasts for X weeks.")
        elif purpose == "time_table":
            # Provide a response related to the timetable
            dispatcher.utter_message(
                "You can access the summer semester timetable from our website."
            )
        else:
            # Handle unknown 'purpose' values
            dispatcher.utter_message("I'm not sure how to respond to that.")

        return []
