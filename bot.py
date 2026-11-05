import os
import telebot

from flask import Flask, request, abort
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL topilmadi!")

if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET topilmadi!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# Sayt ishlayotganini tekshirish
@app.route("/", methods=["GET"])
def home():
    return "Telegram Business bot ishlayapti!", 200


# Telegram webhook manzili
@app.route("/webhook", methods=["POST"])
def webhook():
    # So'rov Telegramdan kelganini tekshirish
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret != WEBHOOK_SECRET:
        abort(403)

    if not request.is_json:
        abort(400)

    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])

    return "OK", 200


# /start komandasi
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Salom! Bot ishlayapti 😊"
    )


# Business ulanishini tekshirish
@bot.business_connection_handler()
def connection(message):
    print("BUSINESS ULANISH KELDI!")
    print("Faol:", message.is_enabled)
    print("Ruxsatlar:", message.rights)


# Shaxsiy akkauntga kelgan xabarlarga javob
@bot.business_message_handler(content_types=["text"])
def auto_reply(message):
    print("XABAR:", message.text)

    try:
        bot.send_message(
            chat_id=message.chat.id,
            text="Assalomu alaykum! Iymona sizga aloqaga chiqadi 😊",
            business_connection_id=message.business_connection_id
        )

        print("JAVOB YUBORILDI!")

    except Exception as e:
        print("XATOLIK:", repr(e))


# Webhookni Telegramga ulash
webhook_url = WEBHOOK_URL.rstrip("/") + "/webhook"

bot.remove_webhook()

result = bot.set_webhook(
    url=webhook_url,
    secret_token=WEBHOOK_SECRET,
    allowed_updates=[
        "message",
        "business_connection",
        "business_message"
    ]
)

print("Webhook o'rnatildi:", result)
print("Webhook manzili:", webhook_url)