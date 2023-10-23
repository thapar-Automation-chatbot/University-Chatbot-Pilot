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

        return [SlotSet("current_grade", None), SlotSet("subject", None)]


# khushi
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


# arshit
class ActionProvideGeneralInfo(Action):
    def name(self) -> Text:
        return "action_provide_general_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        month = tracker.get_slot("month")

        # Your logic to handle different fee types goes here
        if month == "January":
            response = "The auxiliary examination in January follows a similar pattern to the July exam,reapperaing in auxi exam and clearing backlog with max of c grade ."
        elif month == "July":
            response = "The auxiliary examination is a special opportunity for students to again re-appear in exam either during july(summer sem) or during january for est to clear backlogs with max of c grade ."
        else:
            response = "NO auxiliary examination during this month"

        dispatcher.utter_message(response)
        return []

    # def run(
    #     self,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> List[Dict[Text, Any]]:
    #     intent = tracker.latest_message["intent"].get("name")
    #     if intent == "General_info_Auxiliary":
    #         dispatcher.utter_message(
    #             "The auxiliary examination is a special opportunity for students to again re-appear in exam either during july(summer sem) or during january for est to clear backlogs with max of c grade ."
    #         )
    #     elif intent == "General_info_Auxiliary_January":
    #         dispatcher.utter_message(
    #             "The auxiliary examination in January follows a similar pattern to the July exam,reapperaing in auxi exam and clearing backlog with max of c grade ."
    #         )
    #     return []


class ActionProvideExamProcess(Action):
    def name(self) -> Text:
        return "action_provide_exam_process"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        month = tracker.get_slot("month")

        # Your logic to handle different month types goes here
        if month == "January":
            response = "To proceed with the auxiliary exam procedure for january, please visit the following website: https://www.thapar.edu/aboutus/pages/university."
        elif month == "July":
            response = "To proceed with the auxiliary exam procedure for july, please visit the following website: https://www.thapar.edu/aboutus/pages/university."
        else:
            response = "No auxiliary examination during this month"

        dispatcher.utter_message(response)
        return []

    # def run(
    #     self,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> List[Dict[Text, Any]]:
    #     intent = tracker.latest_message["intent"].get("name")
    #     if intent == "Auxiliary_exam_process":
    #         dispatcher.utter_message(
    #             "To proceed with the auxiliary exam procedure, please visit the following website: https://www.thapar.edu/aboutus/pages/university."
    #         )
    #     elif intent == "Auxiliary_exam_process_January":
    #         dispatcher.utter_message(
    #             "To apply for the January auxiliary examination,please visit the following website: https://www.thapar.edu/aboutus/pages/university."
    #         )
    #     return []


class ActionHandleSubjectReEnrollmentAuxiliaryYes(Action):
    def name(self) -> Text:
        return "action_handle_subject_re_enrollment_auxiliary_yes"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            "Yes, you can re-enroll after auxiliary exam,for summer summer sem."
        )
        return []


class ActionHandleSubjectReEnrollmentSummerNo(Action):
    def name(self) -> Text:
        return "action_handle_subject_re_enrollment_summer_no"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            "No, re-enrollment after the summer semester is not allowed for same course if improved once during summer sem."
        )
        return []


class ActionExamEvaluationProcess(Action):
    def name(self) -> Text:
        return "action_exam_evaluation_process"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        response = "The evaluation process for MST/EST/Sessional exams typically involves a combination of factors, including written exams, assignments, and class participation. Grading is based on a scale from similar to normal sem [A] to [F], with [A] representing the highest grade. The specific evaluation criteria may vary depending on the course and instructor. If you need more detailed information, please reach out to your course instructor."
        dispatcher.utter_message(response)
        return []


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
            "auxiliary exam": "auxiliary examination",
            "supplementary exam": "auxiliary examination",
            "additional exam": "auxiliary examination",
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

        # Your logic to handle different fee types goes here
        if mapped_fee_type == "grade improvement":
            response = "The fee for grade improvement is Rs. 15000."
        elif mapped_fee_type == "backlog clearance":
            response = "The fee for clearing backlog subjects is Rs. 15000."
        elif mapped_fee_type == "auxiliary examination":
            response = "The fee for the auxiliary examination is Rs. 2000."
        elif mapped_fee_type == "thesis submission":
            response = "The fee for thesis submission for PG students is Rs. 1000."
        else:
            response = "I'm sorry, but I don't have information about that fee type."

        dispatcher.utter_message(response)
        return []
