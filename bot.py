import streamlit as st
import requests
import time

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

# Define custom CSS styles
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

# Apply custom CSS styles
st.markdown(custom_css, unsafe_allow_html=True)

st.title("Thapar Query Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi, Ask me anything about Summer semester",
        }
    ]

# Rasa backend URL
RASA_BACKEND_URL = "http://localhost:5015/webhooks/rest/webhook"


def handle_buttons(title,payload):
    # print(title)
    st.session_state.messages.append({"role": "user", "content": title})
    rasa_response = get_rasa_response(payload)
    print(rasa_response)
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
    payload = {"sender": "user", "message": message}
    response = requests.post(RASA_BACKEND_URL, json=payload)
    return response.json()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Get assistant response from Rasa backend
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    rasa_response = get_rasa_response(prompt)

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
            titles ,payloads =[],[]
            cols = st.columns(len(buttons))
            for btn in buttons:
                titles.append(btn['title'])
                payloads.append(btn['payload'])
            for i in range(len(buttons)):
                with cols[i]:
                    btn = buttons[i]
                    st.button(btn["title"], on_click=handle_buttons, args=(btn["title"], btn["payload"]))
            


    # print(st.session_state)
    # Add assistant response to chat history
