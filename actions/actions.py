# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re


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


POSSIBLE_GRADES = {
    "a",
    "b",
    "c",
    "e",
    "f",
    "i",
    "x",
    "ra",
    "r.a",
}
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

        elif upgradation_mode == "auxiliary" or upgradation_mode == "auxilary":
            if current_grade in {"c", "b"}:
                dispatcher.utter_message(
                    "Only students with E grade or lower can appear for auxiliary Examination"
                )
            else:
                dispatcher.utter_message(
                    "Students with E grade can appear for auxiliary Exams."
                )
        else:
            dispatcher.utter_message("Backlog Case - solve later ")

        [SlotSet("current_grade", None)]


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
        else:
            if slot_value.lower() in PROJECT_BASED_COURSES:
                self.validate_current_grade("X", dispatcher, tracker, domain)
                print(tracker.get_slot("grade"))
                # not working come back to this later
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
        if subject == None or current_grade == None:
            dispatcher.utter_message("Sorry can you reframe the question")
            return [SlotSet("current_grade", None), SlotSet("subject", None)]
        subject = subject.lower()
        if subject in PROJECT_BASED_COURSES:
            if current_grade in {"a"}:
                dispatcher.utter_message(
                    "Students With grades {} / {} cannot apply for Summer semester".format(
                        current_grade.upper(), current_grade.upper()
                    )
                )
            else:
                dispatcher.utter_message(
                    "The project based courses such as Engineering Design-1, Engineering Design-2, Capstone Project, etc. will only be offered in regular mode in Summer Sem"
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
            elif current_grade.lower() == "a":
                dispatcher.utter_message(
                    "Students With grades {} / {} - cannot apply for Summer semester".format(
                        current_grade.upper(), current_grade.upper()
                    )
                )
            else:
                dispatcher.utter_message(
                    "Students with a grade {} are only eligble for Regular mode of study".format(
                        current_grade.upper()
                    )
                )

        return [SlotSet("current_grade", None), SlotSet("subject", None)]


# Himanshu
class ActionHandleFeeDetails(Action):
    def name(self) -> Text:
        return "action_handle_fee_details"

    @staticmethod
    def map_fee_type(fee_type: str) -> str:
        fee_type_mappings = {
            "backlog": "backlog clearance",
            "clearing backlog": "backlog clearance",
            "make up exam": "backlog clearance",
            "retake exam": "backlog clearance",
            "reexamination": "backlog clearance",
            "grade improvement": "grade improvement",
            "enhance grade": "grade improvement",
            "improve marks": "grade improvement",
            "auxiliary exam": "auxiliary ",
            "supplementary exam": "auxiliary ",
            "additional exam": "auxiliary ",
            "thesis": "thesis submission",
            "dissertation": "thesis submission",
            "research project": "thesis submission",
        }
        return fee_type_mappings.get(fee_type.lower(), fee_type)

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        fee_type = tracker.get_slot("fee_type")
        mapped_fee_type = self.map_fee_type(fee_type)
        study_mode = tracker.get_slot("study_mode")
        if fee_type == None and study_mode != None:
            response = "The fee for grade improvement in {} mode is Rs. 15000 per subject.".format(
                study_mode
            )

        # Your logic to handle different fee types goes here
        if mapped_fee_type == "grade improvement":
            response = "The fee for grade improvement is Rs. 15000 per subject"
        elif mapped_fee_type == "backlog clearance":
            response = "The fee for clearing backlog subjects is Rs. 15000 per backlog."
        elif mapped_fee_type == "auxiliary":
            response = "The fee for the auxiliary examination is Rs. 2000 per Exam."
        elif mapped_fee_type == "thesis submission":
            response = "The fee for thesis submission for PG students is Rs. 1000."
        else:
            response = "I'm sorry, but I don't have information about that fee type."

        dispatcher.utter_message(response)
        return [SlotSet("fee_type", None)]


class ActionHandleRegistrationInquiry(Action):
    def name(self) -> Text:
        return "action_handle_registration_inquiry"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the detected entity value
        upgradation_mode = tracker.get_slot("upgradation_mode")

        if upgradation_mode == "summer":
            # Respond to summer registration inquiry
            response = "You can find the Information about registration for summer semester at the link below [Registation Link](https://thapar.edu/pages/event/summer-semester-list)"

        elif upgradation_mode == "auxiliary":
            # Respond to auxiliary registration inquiry
            dispatcher.utter_message(
                "Auxiliary registration information: can be found here [Registration Link]()"
            )

        else:
            dispatcher.utter_message("No info")

        return []


class ActionRespondToTimetableInquiry(Action):
    def name(self):
        return "action_respond_to_timetable_inquiry"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        upgradation_mode = tracker.get_slot("upgradation_mode")

        if not upgradation_mode:
            upgradation_mode = "summer"

        if upgradation_mode == "auxiliary":
            response = "Time table for Auxiliary Exams can be found here "
        elif upgradation_mode == "summer":
            response = "The timetable for the summer semester can be found [here](https://thapar.edu/pages/event/time-table-of-summer-semester-2023)"
        else:
            response = "I'm not sure about the timetable for that program. Please specify if you're asking about auxiliary or summer semester."

        dispatcher.utter_message(response)

        return []


class ActionRespondToTenureInquiry(Action):
    def name(self):
        return "action_respond_to_tenure_inquiry"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        upgradation_mode = tracker.get_slot("upgradation_mode")

        if not upgradation_mode:
            upgradation_mode = "summer"

        if upgradation_mode == "auxiliary":
            response = "The tenure for the auxiliary program varies depending on the specific course. "
        elif upgradation_mode == "summer":
            response = "The duration of the summer semester typically lasts for [X weeks/months]."
        else:
            response = "I'm not sure about the tenure for that program."

        dispatcher.utter_message(response)

        return []


class ActionProvideExamProcess(Action):
    def name(self):
        return "action_provide_exam_process"

    def run(self, dispatcher, tracker, domain):
        # Extract the 'upgradation_mode' entity from the tracker
        upgradation_mode = tracker.get_slot("upgradation_mode")

        # Customize your responses based on the 'upgradation_mode'
        if upgradation_mode == "auxiliary":
            response = "Here is how the examination process works for auxiliary exams."
        elif upgradation_mode == "summer":
            response = (
                "Here is how the examination process works for the summer semester."
            )
        else:
            response = "I'm not sure which examination process you're asking about."

        # Send the response to the user
        dispatcher.utter_message(response)

        return []


class ActionProvideAboutUpgradationModes(Action):
    def name(self):
        return "action_provide_about_upgradation_modes"

    def run(self, dispatcher, tracker, domain):
        # Extract the 'upgradation_mode' entity from the tracker
        upgradation_mode = tracker.get_slot("upgradation_mode")

        # Customize your responses based on the 'upgradation_mode'
        if upgradation_mode == "auxiliary":
            response = "Here is general info about auxi exam:"
        elif upgradation_mode == "summer":
            response = "Here is general info about summer sem"
        else:
            response = "I'm not sure which examination info you're asking about."

        # Send the response to the user
        dispatcher.utter_message(response)

        return []


class ActionProvideAboutSubjectReEnrollment(Action):
    def name(self):
        return "action_provide_about_subject_re_enrollment"

    def run(self, dispatcher, tracker, domain):
        # Extract the 'upgradation_mode' entity from the tracker
        upgradation_mode = tracker.get_slot("upgradation_mode")

        # Customize your responses based on the 'upgradation_mode'
        if upgradation_mode == "auxiliary":
            response = "yes,after auxiliary you can opt for improvment for once during summer sem"
        elif upgradation_mode == "summer":
            response = "Once opted in summer sem same course can't be taken again for improvement next summer sem"
        else:
            response = "I'm not sure which examination info you're asking about."

        # Send the response to the user
        dispatcher.utter_message(response)

        return []


class ActionExplainGradeImprovementProcess(Action):
    def name(self):
        return "action_explain_grade_improvement_process"

    def run(self, dispatcher, tracker, domain):
        # Extract the 'upgradation_mode' entity from the tracker
        upgradation_mode = tracker.get_slot("upgradation_mode")

        # Customize your responses based on the 'upgradation_mode'
        if upgradation_mode == "auxiliary":
            response = "Max grade achievable is C grade"
        elif upgradation_mode == "summer":
            response = "Students are allowed to go for upgradation in the summer semester. However, the maximum grade that can be rewarded depends on the strength of students."
        else:
            response = "I cannot answer that right now"

        # Send the response to the user
        dispatcher.utter_message(response)

        return []
