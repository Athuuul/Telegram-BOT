import streamlit as st
import json
import time
from datetime import datetime

st.set_page_config(page_title="Live Telegram Logs", layout="wide")

LOG_FILE = "chat_logs.jsonl"

st.title("📡 Live Telegram Bot Log Dashboard")

placeholder = st.empty()

def load_logs():
    logs = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
    except FileNotFoundError:
        pass
    return logs

while True:
    logs = load_logs()
    if not logs:
        st.warning("No logs yet. Send a message to the bot.")
        time.sleep(2)
        continue

    with placeholder.container():
        st.subheader(f"Total Interactions: {len(logs)}")
        users = {}
        for log in logs:
            user_id = log['user']['id']
            users[user_id] = log['user']['name']

        st.write(f"👥 Unique Users: {len(users)}")
        for log in reversed(logs[-20:]):  # Show last 20 logs
            timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            user = log["user"]["name"]
            message = log["message"]
            response = log["response"]
            with st.expander(f"{timestamp} - {user}"):
                st.markdown(f"**User message:** {message}")
                st.markdown(f"**Bot response:** {response}")
    
    time.sleep(3)
