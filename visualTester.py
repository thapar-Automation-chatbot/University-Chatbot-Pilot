import streamlit as st
import requests

FALLBACK_INTENT_RESPONSE_MAP = {
    "Did you mean 'affirm'?": "Did you mean to Confirm",
    "Did you mean 'ask_about_registration'?": "Did you mean to ask about registration",
    "Did you mean 'ask_about_subject_re_enrollment'?": "Did you mean to ask about subject re-enrollment",
    "Did you mean 'ask_about_tenure'?": "Did you mean to ask about tenure",
    "Did you mean 'ask_about_timetable'?": "Did you mean to ask about the timetable",
    "Did you mean 'ask_about_upgradation_modes'?": "Did you mean to ask about upgradation modes",
    "Did you mean 'ask_exam_process'?": "Did you mean to ask about the exam process",
    "Did you mean 'ask_fee_details'?": "Did you mean to ask about fee details",
    "Did you mean 'ask_fee_refund'?": "Did you mean to ask about fee refund",
    "Did you mean 'ask_subject_limitation'?": "Did you mean to ask about subject limitations",
    "Did you mean 'confirm_self_study_conditions'?": "Did you mean to confirm self-study conditions",
    "Did you mean 'deny'?": "Did you mean to deny",
    "Did you mean 'entered_grade'?": "Did you mean you entered a grade",
    "Did you mean 'entered_subject'?": "Did you mean you entered a subject",
    "Did you mean 'explain_grade_improvement_process'?": "Did you mean to ask about the grade improvement process",
    "Did you mean 'goodbye'?": "Did you mean to say goodbye",
    "Did you mean 'greet'?": "Did you mean to greet",
    "Did you mean 'inquire_about_grade_upgradation_eligibility'?": "Did you mean to inquire about grade upgradation eligibility",
    "Did you mean 'inquire_about_medal_scholarship_upgradation_criteria'": "Did you mean to inquire about medal scholarship upgradation criteria",
}

# Define a list of questions to simulate a conversation
questions = [
    "Can students with grades of B, B-, C, and C- take upgradation in the summer semester?",
    "Under what conditions can students with an E grade opt for self-study mode in the summer semester?",
    "What is the maximum grade a student with an E grade can achieve in the auxiliary examination?",
    "How will subjects running in both self and regular modes be handled, and what is the faculty's payment structure in such cases?",
    "What's the maximum number of subjects a student can take in both regular and self-study modes, and are there any special circumstances in which this cap can be exceeded?",
    "Is it possible to round off marks obtained as 24.9, and what is the policy for fee refund once the summer semester has started?",
    "Can a student register for the same course for improvement after having already improved the grade?",
    "Are project-based courses like Engineering Design-1 and Capstone Project offered in self-study mode, and if not, what mode are they offered in?",
    "How do improved grades during the summer semester affect eligibility for medals, scholarships, or upgradation?",
    "What is the proposed revision in the thesis submission fees for PG (M.E. / M.Tech. / MSc. / MA) students?",
    "Can you explain the process for students to be eligible for grade improvement in the summer semester?",
    "How does the auxiliary examination differ from the regular summer semester examination?",
    "Is there any specific criteria for students to apply for upgradation in their grades?",
    "What is the fee structure for students who want to clear backlog cases in the summer semester?",
    "Are there any restrictions on the subjects that can be taken in self-study mode during the summer semester?",
    "Can you clarify the eligibility criteria for medals, scholarships, or upgradation based on grades?",
    "What are the requirements for students to appear for the EST examination of the summer semester?",
    "How are faculty assignments determined for subjects running in both self and regular modes?",
    "Can you explain the procedure for students to apply for upgradation and the process for consideration?",
    "Are there any changes proposed for the upcoming summer semester that were not mentioned in the document?",
    "Can students with an F grade participate in the regular summer semester, and if so, are there any limitations?",
    "What is the process for students who wish to participate in the auxiliary examination in July and January?",
    "How do students inquire about grade upgradation eligibility and subject re-enrollment?",
    "Can students with X grade participate in the regular summer semester, and are there any specific conditions for them?",
    "Is there a limit on the maximum number of subjects a student can take in the auxiliary examination?",
    "What are the criteria for students to be considered for a medal, scholarship, or upgradation based on their grades?",
    "How can students with an E grade improve their grades in the summer semester?",
    "Is there a deadline for students to plan and register for the subjects they want to take in the regular and self-study modes?",
    "Is there any mode of study for students with grade X in the regular summer semester?",
    "What is the role of the EST examination in the summer semester and auxiliary examination, and how do these relate to students' grades?",
    "Can students be allowed to take a maximum of three subjects in both regular and self-study modes?",
    "Can you provide more information about the marks/grades needed to be considered for medals, scholarships, and upgradation in the summer semester?",
    "Is there a specific fee for students who want to improve their grades or clear backlog cases in the summer semester?",
    "Can students with grades of A take upgradation in the summer semester?",
]

st.markdown(
    """
    <style>
    .stButton>button {
        position: fixed;
        top:400px;
        left:200px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize a variable to keep track of the current question index
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
# Rest of your code
st.title(f"Thapar Query Bot - On Q : {st.session_state.current_question_index}")

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


def handle_buttons(title, payload):
    # title = btn["title"]
    # payload = btn["payload"]
    # print(title)
    st.session_state.messages.append({"role": "user", "content": title})
    rasa_response = get_rasa_response(payload)
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


# Function to handle the "Next" button
def handle_next():
    current_question_index = st.session_state.current_question_index
    st.session_state.current_question_index += 1
    if current_question_index < len(questions):
        # Display the next question and simulate the conversation
        next_question = questions[current_question_index]
        st.session_state.messages.append({"role": "user", "content": next_question})
        with st.chat_message("user"):
            st.markdown(
                f'<div class="user-message">{next_question}</div>',
                unsafe_allow_html=True,
            )
        rasa_response = get_rasa_response(next_question)
        try:
            assistant_response = rasa_response[0]["text"]
            buttons = rasa_response[0].get("buttons")
        except:
            assistant_response = "Try again after sometime"
            buttons = None
        assistant_response = FALLBACK_INTENT_RESPONSE_MAP.get(
            assistant_response, assistant_response
        )
        with st.chat_message("assistant"):
            print_bot_response(assistant_response)
            if buttons:
                for btn in buttons:
                    st.button(
                        btn["title"],
                        on_click=handle_buttons,
                        args=(btn["title"], btn["payload"]),
                    )
    else:
        # Display a message when all questions have been asked
        with st.chat_message("assistant"):
            st.markdown("All questions have been asked.")


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

    try:
        assistant_response = rasa_response[0]["text"]
        buttons = rasa_response[0].get("buttons")
    except:
        assistant_response = "Try again after sometime"
        buttons = None
    assistant_response = FALLBACK_INTENT_RESPONSE_MAP.get(
        assistant_response, assistant_response
    )
    with st.chat_message("assistant"):
        print_bot_response(assistant_response)
        if buttons:
            for btn in buttons:
                st.button(
                    btn["title"],
                    on_click=handle_buttons,
                    args=(btn["title"], btn["payload"]),
                )

# Add the "Next" button to the app
if st.button(f"Next {st.session_state.current_question_index}"):
    handle_next()

# ... Rest of your code, including user input handling and message display
