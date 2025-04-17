import telebot
from telebot import types
from PIL import Image
import requests
import io
from flask import Flask, request

TOKEN = "7675263394:AAF37007ZwPg5wzC5yeHEaYeUlDDHkDxP_4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

answers = {
    "привет": "Привет! Я твой StudyBuddy 🤖. Нажми кнопку или задай вопрос.",
    "как дела": "Всё отлично! А у тебя? 😊",
    "помоги": "Нажми на кнопки ниже, чтобы получить помощь."
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📖 Шпаргалка")
    btn2 = types.KeyboardButton("🌤 Погода")
    btn3 = types.KeyboardButton("💡 Цитата дня")
    btn4 = types.KeyboardButton("📸 Отправить фото")
    markup.add(btn1, btn2, btn3, btn4)

    instructions = (
        "👋 Привет! Я StudyBuddy — помощник по учёбе.\n\n"
        "Вот что я умею:\n\n"
        "📖 Шпаргалка — быстрая формула по математике.\n"
        "🌤 Погода — текущая погода в твоём городе.\n"
        "💡 Цитата дня — вдохновляющая цитата от известных людей.\n"
        "📸 Отправить фото — я превращу твоё фото в стикер.\n\n"
        "Нажми на нужную кнопку ниже 👇"
    )

    bot.send_message(message.chat.id, instructions, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()

    if text == "привет":
        bot.send_message(message.chat.id, answers["привет"])
    elif text == "как дела":
        bot.send_message(message.chat.id, answers["как дела"])
    elif text == "помоги":
        bot.send_message(message.chat.id, answers["помоги"])
    elif text == "📖 шпаргалка":
        bot.send_message(message.chat.id, "📚 Шпаргалка по матеше: S = πr² — площадь круга 😉")
    elif text == "🌤 погода":
        send_weather(message)
    elif text == "💡 цитата дня":
        send_quote(message)
    elif text == "📸 отправить фото":
        bot.send_message(message.chat.id, "Пожалуйста, отправь фото 📷")
    else:
        bot.send_message(message.chat.id, "🤔 Не понял, попробуй снова или нажми на кнопку.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image = Image.open(io.BytesIO(downloaded_file))
    image = image.resize((512, 512))
    image.save('user_photo.webp', 'WEBP')

    with open('user_photo.webp', 'rb') as sticker_file:
        bot.send_sticker(message.chat.id, sticker_file)

    bot.reply_to(message, "📸 Фото получено и превращено в стикер! 🎉")

def send_weather(message):
    lat = 51.1694
    lon = 71.4491
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url)
        data = res.json()
        if "current_weather" in data:
            temp = data["current_weather"]["temperature"]
            wind = data["current_weather"]["windspeed"]
            bot.send_message(message.chat.id, f"🌤 Погода: {temp}°C, ветер {wind} км/ч")
        else:
            bot.send_message(message.chat.id, "🌥 Не удалось получить погоду.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка при получении данных о погоде.")

def send_quote(message):
    try:
        res = requests.get("https://zenquotes.io/api/random")
        quote = res.json()[0]['q'] + " — " + res.json()[0]['a']
        bot.send_message(message.chat.id, f"💡 {quote}")
    except:
        bot.send_message(message.chat.id, "💡 Умная цитата: Никогда не сдавайся!")

# 📩 Получение апдейтов от Telegram через Webhook
@app.route(f"/{TOKEN}", methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# ✅ Установка Webhook при первом запуске
@app.route("/", methods=['GET'])
def setup_webhook():
    webhook_url = f"https://<ТВОЙ-РЕНДЕР-URL>.onrender.com/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return "Webhook set", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
