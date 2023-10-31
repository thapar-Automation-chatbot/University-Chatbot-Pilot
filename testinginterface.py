import streamlit as st
import requests
import time
import pandas as pd

USER_ID = "123"

FALLBACK_INTENT_RESPONSE_MAP = {
    "Did you mean 'affirm'?": "Did you mean to Confirm",
    "Did you mean 'ask_about_registration'?": "Did you mean to ask about registration ",
    "Did you mean 'ask_about_subject_re_enrollment'?": "Did you mean to ask about subject re enrollment ",
    "Did you mean 'ask_about_tenure'?": "Did you mean to ask about tenure ",
    "Did you mean 'ask_about_timetable'?": "Did you mean to ask about timetable ",
    "Did you mean 'ask_about_upgradation_modes'?": "Did you mean to ask about upgradation modes ",
    "Did you mean 'ask_exam_process'?": "Did you mean to ask exam process ",
    "Did you mean 'ask_fee_details'?": "Did you mean to ask fee details ",
    "Did you mean 'ask_fee_refund'?": "Did you mean to ask fee refund ",
    "Did you mean 'ask_subject_limitation'?": "Did you mean to ask subject limitation ",
    "Did you mean 'confirm_self_study_conditions'?": "Did you mean to confirm self study conditions ",
    "Did you mean 'deny'?": "Did you mean to deny ",
    "Did you mean 'entered_grade'?": "Did you mean to entered grade ",
    "Did you mean 'entered_subject'?": "Did you mean to entered subject ",
    "Did you mean 'explain_grade_improvement_process'?": "Did you mean to ask about the grade improvement process ",
    "Did you mean 'goodbye'?": "Did you mean to goodbye ",
    "Did you mean 'greet'?": "Did you mean to greet ",
    "Did you mean 'inquire_about_grade_upgradation_eligibility'?": "Did you mean to inquire about grade upgradation eligibility ",
    "Did you mean 'inquire_about_medal_scholarship_upgradation_criteria'?": "Did you mean to inquire about medal scholarship upgradation criteria ",
}

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

custom_css = """
<style>


.chat-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f0f0f0;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.user-message {
    background-color: black;
    color: white;
    margin-bottom: 10px;
    border-radius: 5px;
    padding: 10px;
}

.assistant-message {
    display: flex;
    flex-direction: row-reverse;
    background-color: #aaaaff;
    color: #000;
    margin-bottom: 10px;
    border-radius: 5px;
    padding: 10px;
}

.chat-input-box {
    margin-top: 20px;
}
</style>
"""
st.set_page_config(layout="wide")
# Apply custom CSS styles
st.markdown(custom_css, unsafe_allow_html=True)

st.title("Testing Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi, Ask me anything about Summer semester",
        }
    ]

if "tracker_info" not in st.session_state:
    st.session_state.tracker_info = {
        "slots": {
            "current_grade": "null",
            "upgraded_grade": "null",
            "upgradation_mode": "summer",
            "subject": "null",
            "study_mode": "null",
            "fee_type": "null",
            "requested_slot": "null",
            "session_started_metadata": "null",
        },
        "intent": {"name": "intent_name", "confidence": 0},
        "entities": [
            {"entity": "entity_name", "confidence": 0, "value": "entity_value"}
        ],
        "intent_ranking": [{"name": "greet", "confidence": 0.99456387758255}],
        "active_loop": {},
        "latest_action": {},
    }

# Rasa backend URL
RASA_BACKEND_URL = "http://localhost:5015/webhooks/rest/webhook"

RASA_TRACKER_URL = f"http://localhost:5015/conversations/{USER_ID}/tracker"


def handle_buttons(title, payload):
    # print(title)
    st.session_state.messages.append({"role": "user", "content": title})
    rasa_response = get_rasa_response(payload)
    # print(rasa_response)
    try:
        assistant_response = rasa_response[0]["text"]
    except:
        assistant_response = "Try again after sometime"
    with st.chat_message("assistant"):
        print_bot_response(assistant_response)


def print_bot_response(assistant_response):
    message_placeholder = st.empty()
    full_response = ""
    # Simulate stream of response with milliseconds delay
    for chunk in assistant_response.split():
        full_response += chunk + " "
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


# Function to send message to Rasa backend
def get_rasa_response(message):
    payload = {"sender": f"{USER_ID}", "message": message}
    response = requests.post(RASA_BACKEND_URL, json=payload)
    tracker_response = requests.get(RASA_TRACKER_URL)
    return response.json(), tracker_response.json()


# Function to Extract stuff from tracker Info
def update_tracker_info(response):
    new_slots = response.get("slots")
    latest_msg = response.get("latest_message")
    intent = latest_msg.get("intent")
    entites = latest_msg.get("entities")
    intent_ranking = latest_msg.get("intent_ranking")
    latest_action = response.get("latest_action")
    active_loop = response.get("active_loop")
    text = latest_msg.get("text")
    st.session_state.tracker_info = {
        "slots": new_slots,
        "intent": intent,
        "entities": entites,
        "intent_ranking": intent_ranking,
        "active_loop": active_loop,
        "latest_action": latest_action,
        "text": text,
    }


def display_tracker_info():
    # st.title("Tracker Info")

    tracker_info = st.session_state.tracker_info

    tab_list = st.tabs(
        [
            "Slots",
            "Intent",
            "Intent Ranking",
            "Active Loop",
            "Entities",
            "Latest Action",
            "Add in file",
        ]
    )
    # selected_tab = st.radio("Select Tab:", tabs)

    with tab_list[0]:
        slot_df = pd.DataFrame(tracker_info["slots"], index=["values"]).transpose()
        st.dataframe(slot_df, use_container_width=True)
    with tab_list[1]:
        intent = pd.DataFrame(tracker_info["intent"], index=["name"])
        if not intent.empty:
            intent.set_index("name", inplace=True)
            st.dataframe(intent, use_container_width=True)
    with tab_list[2]:
        intent_ranking = pd.DataFrame(tracker_info["intent_ranking"][:5])
        if not intent_ranking.empty:
            intent_ranking.set_index("name", inplace=True)
            st.dataframe(intent_ranking, use_container_width=True)
    with tab_list[3]:
        active_loop = pd.DataFrame(tracker_info["active_loop"], index=[0]).transpose()
        if not active_loop.empty:
            st.dataframe(active_loop, use_container_width=True)
    with tab_list[4]:
        entities = pd.DataFrame(tracker_info["entities"])
        if not entities.empty:
            st.dataframe(entities, use_container_width=True)
    with tab_list[5]:
        latest_action = pd.DataFrame(
            tracker_info["latest_action"], index=[0]
        ).transpose()
        if not latest_action.empty:
            st.dataframe(latest_action, use_container_width=True)
    with tab_list[6]:
        df = pd.read_csv("wrongQs.csv",index_col=False)
        text = tracker_info.get('text')
        intent_dict = tracker_info["intent"]
        intent_name = intent_dict.get('name')
        confidence = intent_dict.get('confidence')
        if st.button("Click to add to file"):
            with open("wrongQs.csv",'+a') as file:
                file.write('{},{},{} \n'.format(text,intent_name,confidence))
        st.dataframe(df,use_container_width=True,hide_index=True)


# Display chat messages from history on app rerun
chatcol, infocol = st.columns(2)
with chatcol:
    for message in st.session_state.messages:
        with st.container():
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Get assistant response from Rasa backend
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    rasa_response, tracker_response = get_rasa_response(prompt)
    update_tracker_info(tracker_response)

    # print(tracker_response)
    # print(rasa_response)
    try:
        assistant_response = rasa_response[0]["text"]
        buttons = rasa_response[0].get("buttons")
    except:
        assistant_response = "Try again after sometime"
        buttons = None
    assistant_response = FALLBACK_INTENT_RESPONSE_MAP.get(
        assistant_response, assistant_response
    )
    # Display user message in chat message container
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        print_bot_response(assistant_response)
        if buttons:
            titles, payloads = [], []
            cols = st.columns(len(buttons))
            for btn in buttons:
                titles.append(btn["title"])
                payloads.append(btn["payload"])
            for i in range(len(buttons)):
                with cols[i]:
                    btn = buttons[i]
                    st.button(
                        btn["title"],
                        on_click=handle_buttons,
                        args=(btn["title"], btn["payload"]),
                    )


with infocol:
    # st.write(st.session_state.tracker_info)

    display_tracker_info()
