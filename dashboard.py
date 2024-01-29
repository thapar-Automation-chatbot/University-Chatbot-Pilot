import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

# Define the Rasa endpoint URL
RASA_ENDPOINT_URL = "http://localhost:5015/model/parse"


INTENT_RESPONSE_MAP = {
    "affirm": " Confirm",
    "ask_about_registration": " ask about registration ",
    "ask_about_subject_re_enrollment": " ask about subject re enrollment ",
    "ask_about_tenure": " ask about tenure ",
    "ask_about_timetable": " ask about timetable ",
    "ask_about_upgradation_modes": " ask about upgradation modes ",
    "ask_exam_process": " ask exam process ",
    "ask_fee_details": " ask fee details ",
    "ask_fee_refund": " ask fee refund ",
    "ask_subject_limitation": " ask subject limitation ",
    "confirm_self_study_conditions": " confirm self study conditions ",
    "deny": " deny ",
    "entered_grade": " entered grade ",
    "entered_subject": " entered subject ",
    "explain_grade_improvement_process": " ask about the grade improvement process ",
    "goodbye": " goodbye ",
    "greet": " greet ",
    "inquire_about_grade_upgradation_eligibility": " inquire about grade upgradation eligibility ",
    "inquire_about_medal_scholarship_upgradation_criteria": " inquire about medal scholarship upgradation criteria ",
}

st.title("Rasa NLU Dashboard")

# Create a form to enter a text message
if prompt := st.chat_input("What is up?"):
    if prompt:
        # Send a POST request to the Rasa endpoint
        payload = {"text": prompt}
        response = requests.post(RASA_ENDPOINT_URL, json=payload)

        if response.status_code == 200:
            data = response.json()

            # Display the top 5 intents and their scores in a block
            intents = data.get("intent_ranking", [])
            st.subheader(prompt)
            st.subheader(intents[0])
            st.subheader("Top 5 Intents:")

            intent_data = pd.DataFrame(
                {
                    "Intent": [
                        INTENT_RESPONSE_MAP[intent["name"]] for intent in intents[:5]
                    ],
                    "Confidence": [intent["confidence"] for intent in intents[:5]],
                }
            )
            intent_data.set_index("Intent", inplace=True)

            l, r = st.columns([3, 1])
            with l:
                st.bar_chart(intent_data)
            with r:
                # Display entities
                entities = data.get("entities", [])
                if entities:
                    st.subheader("Entities:")
                    for entity in entities:
                        st.write(
                            f"Entity: {entity['entity']}, Value: {entity['value']}"
                        )
        else:
            st.error(
                f"Failed to get a response from Rasa. Status code: {response.status_code}"
            )
    else:
        st.warning("Please enter a message to analyze.")

