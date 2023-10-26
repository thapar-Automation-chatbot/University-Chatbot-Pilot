import streamlit as st
import requests
import time

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
            "content": "Hi,Ask me anything about Summer semester",
        }
    ]

# Rasa backend URL
RASA_BACKEND_URL = "http://localhost:5069/webhooks/rest/webhook"

# Function to send message to Rasa backend
def get_rasa_response(message):
    payload = {"sender": "user", "message": message}
    response = requests.post(RASA_BACKEND_URL, json=payload)
    return response.json()

# Function to extract buttons from Rasa response
def extract_buttons(rasa_response):
    buttons = rasa_response[0].get("buttons")
    if buttons:
        return buttons
    return None

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
    print(rasa_response)
    try:
        assistant_response = rasa_response[0]["text"]
        buttons = extract_buttons(rasa_response)
    except:
        assistant_response = "Didn't get that"
        buttons = None

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        if buttons:
            for button in buttons:
                st.write(button["title"])
        else:
            message_placeholder = st.empty()
            full_response = ""
            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                full_response += chunk + " "
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Make sure to handle button clicks and user responses to buttons as needed.
