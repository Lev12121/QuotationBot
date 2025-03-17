import json
import telebot
from telebot import types
import random
from dotenv import load_dotenv
import os

load_dotenv()

KEY = os.getenv('API_KEY')

bot = telebot.TeleBot(KEY)
user_states = {} # Зберігання запитів на додавання цитат
user_states2 = {} # Зберігання запитів на їх вивід
user_states3 = {} # Зберігання запитів на їх видалення

# Функція для відкриття файлу json
def open_json():
    with open("quotes.json") as f:
        return json.load(f)

# Функція для додавання користувача в json
def add_user(id):
    js = open_json()
    if str(id) not in js.keys():
        js[id] = {}
        with open("quotes.json", 'w') as f:
            json.dump(js, f)

# Функція для додавання цитати
def add_quote(id, author, quote):
    js = open_json()
    if author in js[str(id)].keys():
        js[str(id)][author].append(quote)
    else:
        js[str(id)][author] = [quote]

    with open("quotes.json", 'w') as f:
        json.dump(js, f)

def get_quotes(js, id, author):
    ret = "Ось цитати від цього автора : \n\n"
    for quote in js[str(id)][author]:
        ret += f"*{quote}* \n\n"

    return ret
    


# Головне меню
def main_menu():
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Додати нову цитату")
    item2 = types.KeyboardButton("Вивести цитату зі списку")
    item3 = types.KeyboardButton("Видалити цитату")
    markup.add(item1, item2, item3)
    return markup

# Обробка команди start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Ласкаво просимо до нашого боту! Тут ви можете додавати свої улюблені цитати.", 
    reply_markup=main_menu())
    add_user(message.chat.id)


# Службова команда для отримання id чату
@bot.message_handler(commands=['getid'])
def id(message):
    c_id = message.chat.id
    bot.send_message(c_id, f"ID вашого чату : {c_id}")

# Обробка додавання автора цитати
@bot.message_handler(func=lambda message: message.text == "Додати нову цитату")
def send_response(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Вийти")
    markup.add(item)

    bot.send_message(message.chat.id, "Введіть ім'я автора цитати", reply_markup=markup)
    user_states[message.chat.id] = "author"


# Обробка додавання самої цитати та вихода з меню
@bot.message_handler(func=lambda message: message.chat.id in user_states)
def response(message):
    # Якщо користувач хоче вийти
    if message.text == "Вийти":
        del user_states[message.chat.id]
        bot.send_message(message.chat.id, "Ви в головному меню", reply_markup=main_menu())


    # Якщо автора додано, просимо цитату
    elif user_states[message.chat.id] == "author":
        user_states[message.chat.id] = message.text
        bot.send_message(message.chat.id, "Тепер введіть саму цитату")

    
    # Коли відправили цитату
    else:
        bot.send_message(message.chat.id, "Цитату додано!", reply_markup=main_menu())
        add_quote(message.chat.id, user_states[message.chat.id], message.text)
        del user_states[message.chat.id]


# Якщо запросили цитату
@bot.message_handler(func=lambda message : message.text == "Вивести цитату зі списку") 
def r(message):
    user_states2[message.chat.id] = "choice"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Вивести випадкову цитату")
    item2 = types.KeyboardButton("Знайти цитату за автором")
    item3 = types.KeyboardButton("Вийти")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Виберіть потрібну опцію", reply_markup=markup)

# Обрабка виводу цитати
@bot.message_handler(func=lambda message : message.chat.id in user_states2)
def r2(message):
    chat_id = message.chat.id # id чату

    # Якщо користувач хоче вийти
    if message.text == "Вийти": 
        del user_states2[chat_id]
        bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())

    # Якщо ми обрали спосіб виводу цитати
    elif user_states2[chat_id] == "choice":
        # Якщо ми обрали вивід випадкової цитати
        if message.text == "Вивести випадкову цитату":
            js = open_json()
            try:
                author = random.choice(list(js[str(chat_id)].keys()))
                quote = random.choice(js[str(chat_id)][author])
                bot.send_message(chat_id, f"*{author}* : {quote} \n \n*Ви в головному меню*", reply_markup=main_menu(), parse_mode='Markdown')
            except:
                bot.send_message(message.chat.id, "В списку поки немає жодних цитат :( Додайте їх!", reply_markup=main_menu())
            finally:
                del user_states2[chat_id]

        # Якщо користувач хоче знайти цитату за автором
        elif message.text == "Знайти цитату за автором":
            user_states2[chat_id] = "author"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Вийти")
            markup.add(item1)
            bot.send_message(chat_id, "Введіть ім'я автора", reply_markup=markup)

    # Після вводу імені автора
    elif user_states2[chat_id] == "author":
        js = open_json()
        if js[str(chat_id)].get(message.text) != None:
            bot.send_message(chat_id, get_quotes(js, chat_id, message.text), parse_mode='Markdown')
            bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())
            del user_states2[chat_id]
        else:
            del user_states2[chat_id]
            bot.send_message(chat_id, "Нажаль, цитат від цього автора не знайдено :(", reply_markup=main_menu())


# Якщо запросили видалення цитати
@bot.message_handler(func=lambda message: message.text == "Видалити цитату")
def r3(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Вийти")
    markup.add(item1)
    user_states3[message.chat.id] = 'author'
    bot.send_message(message.chat.id, "Введіть ім'я автора цитати", reply_markup=markup)


# Обробка видалення цитати
@bot.message_handler(func=lambda message: message.chat.id in user_states3.keys())
def r4(message):
    chat_id = message.chat.id
    if message.text == "Вийти":
        del user_states3[chat_id]
        bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())

    # Якщо користувач ввів ім'я автора
    elif user_states3[chat_id] == 'author':
        js = open_json()
        # Якщо імені нема в json
        if js[str(chat_id)].get(message.text) == None:
            del user_states3[chat_id]
            bot.send_message(chat_id, "Нажаль, цитат з цим автором не знайдено :(", reply_markup=main_menu())

        # Якщо такий автор є
        else:
            quotes = js[str(chat_id)][message.text]
            mes = "Оберіть цитату для видалення (Відправте її номер)"
            for i in range(len(quotes)):
                mes += f"\n\n*{i}* : {quotes[i]}"

            user_states3[chat_id] = message.text
            bot.send_message(chat_id, mes, parse_mode='Markdown')

    # Якщо користувач обрав цитату для видалення
    else:
        author = user_states3[chat_id]
        js = open_json()
        try:
            js[str(chat_id)][author].pop(int(message.text))

            if len(js[str(chat_id)][author]) == 0:
                del js[str(chat_id)][author]

            with open('quotes.json', 'w') as f:
                json.dump(js, f)
            bot.send_message(chat_id, "Цитату успішно видалено!", reply_markup=main_menu())
        except:
            bot.send_message(chat_id, "Некорректний запит. Операцію скасовано.", reply_markup=main_menu())
        finally:
            del user_states3[chat_id]








bot.infinity_polling()