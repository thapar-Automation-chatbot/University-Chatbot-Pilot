USER_ID = "123"

import requests
import time
import pandas as pd


RASA_BACKEND_URL = "http://localhost:5015/webhooks/rest/webhook"

RASA_TRACKER_URL = f"http://localhost:5015/conversations/{USER_ID}/tracker"


# Function to send message to Rasa backend
def get_rasa_response(message):
    payload = {"sender": f"{USER_ID}", "message": message}
    response = requests.post(RASA_BACKEND_URL, json=payload)
    tracker_response = requests.get(RASA_TRACKER_URL)
    return response.json(), tracker_response.json()


# function to extract info from the json responses
def extract_info(rasa_response, tracker_response, prompt) -> dict:
    latest_msg = tracker_response.get("latest_message")
    intent = latest_msg.get("intent")
    intent_ranking = latest_msg.get("intent_ranking")
    response = rasa_response[0].get("text")
    resp = {
        "prompt": prompt,
        "response": response,
        "intent": intent,
        "intent_ranking": intent_ranking[:5],
    }
    return resp


resp_list = []
# function call to fetch responses
prompt = "can i take ucs021 in summer sem in self study mode"
rasa_response, tracker_response = get_rasa_response(prompt)
resp_list.append(extract_info(rasa_response, tracker_response, prompt))
