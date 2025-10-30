import os
import json
import requests
import telebot
from telebot import types
from config import routes  # твій словник маршрутів
from config import API     # твій ключ для OpenWeatherMap

# ================== Бот ==================
TOKEN = "7607472848:AAGKkjtE7TYbm-pSUtudtF2usRDOWEkww"
bot = telebot.TeleBot(TOKEN)

# Глобальні змінні для стану
selected_route = None
selected_direction = None

# ================== Клавіатури ==================
def create_keyboard(buttons, back_button=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    if back_button:
        markup.add(types.KeyboardButton("🔙 Головне меню"))
    return markup

# ================== Команди ==================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("👋 Привітатись"))
    markup.add(types.KeyboardButton("❓ Задати питання"))
    bot.send_message(message.chat.id,
                     f"Привіт, {message.from_user.first_name}! Я тестовий бот",
                     reply_markup=markup)

# ================== Обробка тексту ==================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global selected_route, selected_direction

    text = message.text

    if text == "👋 Привітатись":
        bot.send_message(message.chat.id, "Привіт! Протестуй мене і додай кілька власних запитань!")

    elif text == "❓ Задати питання":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Як мене звати?"))
        markup.add(types.KeyboardButton("Мої можливості?"))
        markup.add(types.KeyboardButton("🔙 Головне меню"))
        bot.send_message(message.chat.id, "Задай мені питання", reply_markup=markup)

    elif text == "🔙 Головне меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("👋 Привітатись"))
        markup.add(types.KeyboardButton("❓ Задати питання"))
        bot.send_message(message.chat.id, "Ви повернулись в головне меню", reply_markup=markup)

    elif text == "Як мене звати?":
        bot.send_message(message.chat.id, "I am Batman))")

    elif text == "Мої можливості?":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Розклад маршрутів"))
        markup.add(types.KeyboardButton("🔙 Головне меню"))
        bot.send_message(message.chat.id, "Можу...", reply_markup=markup)

    elif text == "Розклад маршрутів":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("41"))
        markup.add(types.KeyboardButton("🔙 Головне меню"))
        bot.send_message(message.chat.id, "Виберіть '№' маршруту", reply_markup=markup)

    elif text in routes:
        selected_route = text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("В місто"))
        markup.add(types.KeyboardButton("З міста"))
        markup.add(types.KeyboardButton("🔙 Головне меню"))
        bot.send_message(message.chat.id, f"Маршрут №{text}. Виберіть напрямок:", reply_markup=markup)

    elif text in ["В місто", "З міста"]:
        if not selected_route:
            bot.send_message(message.chat.id, "Спершу оберіть маршрут.")
            return

        selected_direction = "to_city" if text == "В місто" else "from_city"
        stops = routes[selected_route][selected_direction]
        markup = create_keyboard(stops)
        bot.send_message(message.chat.id,
                         f"Зупинки маршруту №{selected_route} у напрямку {'до міста' if selected_direction == 'to_city' else 'з міста'}:",
                         reply_markup=markup)

    elif selected_route and selected_direction and text in routes[selected_route][selected_direction]:
        stop_name = text
        image_path = f"Pictures_Zupunka/{stop_name}.png"
        if os.path.exists(image_path):
            with open(image_path, "rb") as img:
                bot.send_photo(message.chat.id, img)
        else:
            bot.send_message(message.chat.id, f"Скріншот для зупинки '{stop_name}' відсутній.")

    else:
        bot.send_message(message.chat.id, "З такою командою я ще незнайомий..")

# ================== Погода ==================
def get_weather(city, chat_id):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = res.json()
        temp = data["main"]["temp"]
        bot.send_message(chat_id, f'Зараз погода: {temp}°C')

        if temp < 0:
            image = 'Pictures/snow.png'
        elif 0 <= temp < 10:
            image = 'Pictures/suny.jpg'
        else:
            image = 'Pictures/sun.jpg'

        if os.path.exists(image):
            with open(image, 'rb') as file:
                bot.send_photo(chat_id, file)
    else:
        bot.send_message(chat_id, "Такого міста не існує")

# ================== Запуск ==================
print("Бот запущений...")
bot.polling(non_stop=True, interval=0)
