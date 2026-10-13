import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
from PIL import Image
import io
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8938001256:AAF1KL9m-XB3pmZveH9qyBADRuDhBTicq0Q")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IKqJCOiqBAf4RTYzWCE9yOFjqa-gP9A91Ug")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Trader Jannat AI** এ স্বাগতম!\n\n"
        "📈 যেকোনো চার্টের স্ক্রিনশট পাঠালেই সংক্ষেপে UP/DOWN সিগন্যাল অ্যানালাইসিস পেয়ে যাবেন।"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 চার্ট অ্যানালাইসিস করা হচ্ছে...")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        prompt = (
            "You are Trader Jannat AI. Analyze this chart image for binary options and output ONLY in this ultra-short format in Bengali/English:\n\n"
            "📊 **Trader Jannat AI Signal** 📊\n\n"
            "● **Pair:** (e.g., EUR/USD or OTC Pair)\n"
            "● **Signal:** 🟢 CALL (UP) or 🔴 PUT (DOWN)\n"
            "● **Timeframe:** 1 Min / 5 Min\n"
            "● **Accuracy:** (e.g., 90%)\n"
            "● **Reason:** (Only 1 short sentence in Bengali)"
        )
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[image, prompt]
        )
        
        await status_msg.edit_text(response.text, parse_mode='Markdown')
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Trader Jannat AI is running...")
    app.run_polling()
