import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai
import json
import sys

# === CONFIG ===
TELEGRAM_BOT_TOKEN = ''
GEMINI_API_KEY = ''
LOG_FILE = "chat_logs.jsonl"

# === Gemini Config ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# === Telegram Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text
    user_info = {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "",
    }
    timestamp = datetime.now().isoformat()

    # Generate response from Gemini
    try:
        response = model.generate_content(message)
        reply = response.text.strip()
    except Exception as e:
        reply = f"Gemini error: {e}"

    await update.message.reply_text(reply)

    # Save logs
    log_entry = {
        "timestamp": timestamp,
        "user": user_info,
        "message": message,
        "response": reply
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[{timestamp}] {user_info['name']}: {message}")

# === Start Bot ===
def start_bot():
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()  # DO NOT 'await' this — it's sync!

if __name__ == '__main__':
    start_bot()
