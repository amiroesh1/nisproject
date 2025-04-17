import telebot
from telebot import types
from PIL import Image
import requests
import io

# Твой токен бота
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Сценарные ответы
answers = {
    "привет": "Привет! Я твой StudyBuddy 🤖. Нажми кнопку или задай вопрос.",
    "как дела": "Всё отлично! А у тебя? 😊",
    "помоги": "Нажми на кнопки ниже, чтобы получить помощь."
}

# Команда /start
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

# Обработка текстовых сообщений
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

# Обработка фото
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

# Получение погоды с внешнего API
def send_weather(message):
    response = requests.get("https://wttr.in/?format=3")
    bot.send_message(message.chat.id, f"🌤 Погода: {response.text}")

# Получение цитаты
def send_quote(message):
    try:
        res = requests.get("https://zenquotes.io/api/random")
        quote = res.json()[0]['q'] + " — " + res.json()[0]['a']
        bot.send_message(message.chat.id, f"💡 {quote}")
    except:
        bot.send_message(message.chat.id, "💡 Умная цитата: Никогда не сдавайся!")

# Запуск бота
bot.polling()
