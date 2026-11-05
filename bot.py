
import os
import logging
import threading

import telebot
from flask import Flask, request

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL topilmadi!")

WEBHOOK_PATH = "/webhook"

# =========================
# BOT
# =========================

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# =========================
# BUSINESS XABARLAR
# =========================

@bot.business_message_handler(func=lambda message: True)
def business_reply(message):

    try:
        print("XABAR KELDI:", message.text)

        if not message.business_connection_id:
            print("Business connection ID topilmadi!")
            return

        text = message.text or ""

        if not text.strip():
            return

        # O'z xabaringizga javob bermaslik
        if message.from_user and message.from_user.is_bot:
            return

        answer = "Salom! 😊 Xabaringiz uchun rahmat. Tez orada javob beramiz."

        bot.send_message(
            chat_id=message.chat.id,
            text=answer,
            business_connection_id=message.business_connection_id
        )

        print("JAVOB YUBORILDI!")

    except Exception as e:
        logging.exception("Javob yuborishda xatolik: %s", e)


# =========================
# WEBHOOK
# =========================

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():

    try:
        json_data = request.get_json(force=True)

        update = telebot.types.Update.de_json(json_data)

        bot.process_new_updates([update])

        return "OK", 200

    except Exception as e:
        logging.exception("Webhook xatosi: %s", e)
        return "ERROR", 500


# =========================
# HEALTH CHECK
# =========================

@app.route("/", methods=["GET"])
def home():
    return "Telegram Business Auto Reply Bot ishlayapti!", 200


# =========================
# WEBHOOK O'RNATISH
# =========================

def setup_webhook():

    url = WEBHOOK_URL.rstrip("/") + WEBHOOK_PATH

    try:
        bot.remove_webhook()
        result = bot.set_webhook(url=url)

        if result:
            print("WEBHOOK O'RNATILDI:", url)
        else:
            print("WEBHOOK O'RNATILMADI!")

    except Exception as e:
        logging.exception("Webhook o'rnatishda xatolik: %s", e)


# =========================
# ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":

    setup_webhook()

    port = int(os.environ.get("PORT", 10000))

    print("BOT ISHGA TUSHDI!")
    print("BOT USERNAME:", bot.get_me().username)

    app.run(
        host="0.0.0.0",
        port=port
    )
