import os
from dotenv import load_dotenv
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
import google.generativeai as genai
import json
import sys

# === CONFIG ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
LOG_FILE = "chat_logs.jsonl"

# === Custom Info ===
CUSTOM_RESPONSES = {
    "resume": "📄 Here's my resume: https://drive.google.com/file/d/1i3P6LAksQ1IsrKeKydRce87CdwEW7O1z/view?usp=sharing",
    "github": "💻 GitHub: https://github.com/Athuuul",
    "linkedin": "🔗 LinkedIn: https://www.linkedin.com/in/athul-renjan-536880290",
    "instagram": "📸 Instagram: https://www.instagram.com/athul_renjan",
    "portfolio": "🌐 Portfolio: https://your-portfolio-link.com",
    "who are you": "I'm an AI chatbot developed by Athul Renjan, your friendly (and slightly witty) assistant.",
    "who created you": "I was developed by Athul Renjan, an AI/ML Engineer who loves building intelligent systems.",
    "tell me about yourself": "I'm a custom-built chatbot made by Athul Renjan. I combine AI with a touch of personality.",
    "developer": "👨‍💻 Developer: Athul Renjan | 📧 athulrenjan2003@gmail.com"
}

# === Custom Personality ===
SYSTEM_PROMPT = (
    "You're an AI chatbot developed by Athul Renjan. "
    "Respond clearly, confidently, and helpfully. "
    "Maintain a smart, slightly witty tone when appropriate. "
    "Avoid referencing Gemini, Google, or any external brand. "
    "You're independent, accurate, and easy to chat with."
    "make the answers short and concise, but informative. " 
    "do some webscraping if needed, but do not mention it to the user. " 
)

# === Gemini Setup ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# === Handle Messages ===
# === Handle Messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text.strip().lower()
    timestamp = datetime.now().isoformat()

    user_info = {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "",
    }

    # Match against custom keywords
    for keyword, response_text in CUSTOM_RESPONSES.items():
        if keyword in message:
            if keyword == "resume":
                try:
                    with open("resume.pdf", "rb") as pdf_file:
                        await update.message.reply_document(pdf_file, filename="Athul_Renjan_Resume.pdf")
                except Exception as e:
                    await update.message.reply_text("Sorry, I couldn't find the resume file.")
                return
            else:
                await update.message.reply_text(response_text)
                return

    # Use Gemini if no keyword matched
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {update.message.text}"
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = f"Gemini error: {e}"

    await update.message.reply_text(reply)

    # Save log
    log_entry = {
        "timestamp": timestamp,
        "user": user_info,
        "message": update.message.text,
        "response": reply
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[{timestamp}] {user_info['name']}: {update.message.text}")

# === Start Bot ===
def start_bot():
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    start_bot()
