import os
from telebot import types
from config import sowa
from config import routes
from config import API
import requests
import json

token = "7607472848:AAGKkjtE7TYbm-pSUtudt2tF2usRDOWEkww"
sowa = telebot.TeleBot(token)

selected_route = None  # Змінна для збереження вибраного маршруту
selected_direction = None  # Змінна для збереження вибраного напрямку

@sowa.message_handler(commands=['start'])  # Створюємо команду
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привітатись")
    btn2 = types.KeyboardButton("❓ Задати питання")
    markup.add(btn1, btn2)
    sowa.send_message(message.chat.id,text="Привіт, {0.first_name}! Я тестовий бот".format(message.from_user),reply_markup=markup)

@sowa.message_handler(content_types=['text'])
def func(message):
    global selected_route, selected_direction  # Використовуємо глобальні змінні

    if message.text == "👋 Привітатись":
        sowa.send_message(message.chat.id, text="Привіт! Протестуй мене і добав кілька власних запитань!)")

    elif message.text == "❓ Задати питання":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Як мене звати?")
        btn2 = types.KeyboardButton("Мої можливості?")
        back = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn1, btn2, back)
        sowa.send_message(message.chat.id, text="Задай мені питання", reply_markup=markup)

    elif message.text == "🔙 Головне меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("👋 Привітатись")
        button2 = types.KeyboardButton("❓ Задати питання")
        markup.add(button1, button2)
        sowa.send_message(message.chat.id, text="Ви повернулись в головне меню", reply_markup=markup)

    elif message.text == "Як мене звати?":
        sowa.send_message(message.chat.id, "I am Batman))")

    elif message.text == "Мої можливості?":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Розклад маршрутів")
        back = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn1, back)
        sowa.send_message(message.chat.id, text="Можу... ", reply_markup=markup)

    elif message.text == "Розклад маршрутів":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("41")
        back = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn1, back)
        sowa.send_message(message.chat.id, "Виберіть '№' маршруту", reply_markup=markup)

    elif message.text in routes:
        selected_route = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("В місто")
        btn2 = types.KeyboardButton("З міста")
        back = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn1, btn2, back)
        sowa.send_message(message.chat.id, f"Маршрут №{message.text}. Виберіть напрямок:", reply_markup=markup)

    elif message.text in ["В місто", "З міста"]:
        selected_direction = "to_city" if message.text == "В місто" else "from_city"
        stops = routes[selected_route][selected_direction]
        markup = create_keyboard(stops)
        sowa.send_message(message.chat.id,f"Зупинки маршруту №{selected_route} у напрямку {'до міста' if selected_direction == 'to_city' else 'з міста'}:",reply_markup=markup)

    elif selected_route and selected_direction and message.text in routes[selected_route][selected_direction]:
        stop_name = message.text
        zup = f"Pictures_Zupunka/{stop_name}.png"  # Шлях до зображення

        if os.path.exists(zup):
            with open(zup, "rb") as img:
                sowa.send_photo(message.chat.id, img)
        else:
            sowa.send_message(message.chat.id, f"Скріншот для зупинки '{stop_name}' відсутній.")

    else:
        sowa.send_message(message.chat.id, text="З такою командою я ще незнайомий..")

def get_weather(message):
    city = message
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        sowa.reply_to(message.text, f'Зараз погода: {temp}°C')

        if temp < 0:
            image = 'Pictures/snow.png'
        elif 0 <= temp < 10:
            image = 'Pictures/suny.jpg'
        else:
            image = 'Pictures/sun.jpg'

        try:
            with open(image, 'rb') as file:
                sowa.send_photo(message.chat.id, file)
        except FileNotFoundError:
            sowa.reply_to(message, "Зображення для цієї погоди відсутнє.")
        else:
            sowa.reply_to(message, f'Такого міста не існує')

# Функція для створення клавіатури
def create_keyboard(buttons, back_button=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    if back_button:
        markup.add(types.KeyboardButton("🔙 Головне меню"))
    return markup


sowa.polling(non_stop=True, interval=0)
