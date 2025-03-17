import json
import telebot
from telebot import types
import random
from dotenv import load_dotenv
import os

load_dotenv()

KEY = os.getenv('API_KEY')

bot = telebot.TeleBot(KEY)
user_states = {} # Хранение запросов на добавление цитат
user_states2 = {} # Хранение запросов на их извлечение
user_states3 = {} # Хранение запросов на их удаление

# Функция для открытия файла json
def open_json():
    with open("quotes.json") as f:
        return json.load(f)

# Функция для добавления в json пользователя
def add_user(id):
    js = open_json()
    if str(id) not in js.keys():
        js[id] = {}
        with open("quotes.json", 'w') as f:
            json.dump(js, f)

# Функция для добавления цитаты
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
    


# Главное меню
def main_menu():
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Додати нову цитату")
    item2 = types.KeyboardButton("Вивести цитату зі списку")
    item3 = types.KeyboardButton("Видалити цитату")
    markup.add(item1, item2, item3)
    return markup

# Обработка команды start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Ласкаво просимо до нашого боту! Тут ви можете додавати свої улюблені цитати.", 
    reply_markup=main_menu())
    add_user(message.chat.id)


# Служебная команда для получения id чата
@bot.message_handler(commands=['getid'])
def id(message):
    c_id = message.chat.id
    bot.send_message(c_id, f"ID вашого чату : {c_id}")

# Обработка добавления новой цитаты (автора)
@bot.message_handler(func=lambda message: message.text == "Додати нову цитату")
def send_response(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Вийти")
    markup.add(item)

    bot.send_message(message.chat.id, "Введіть ім'я автора цитати", reply_markup=markup)
    user_states[message.chat.id] = "author"


# Обработка добавления самой цитаты и выхода из меню
@bot.message_handler(func=lambda message: message.chat.id in user_states)
def response(message):
    # Если хотят выйти
    if message.text == "Вийти":
        del user_states[message.chat.id]
        bot.send_message(message.chat.id, "Ви в головному меню", reply_markup=main_menu())


    # Если автор добавлен, просим цитату
    elif user_states[message.chat.id] == "author":
        user_states[message.chat.id] = message.text
        bot.send_message(message.chat.id, "Тепер введіть саму цитату")

    
    # Когда прислали цитату
    else:
        bot.send_message(message.chat.id, "Цитату додано!", reply_markup=main_menu())
        add_quote(message.chat.id, user_states[message.chat.id], message.text)
        del user_states[message.chat.id]


# Если запросили цитату
@bot.message_handler(func=lambda message : message.text == "Вивести цитату зі списку") 
def r(message):
    user_states2[message.chat.id] = "choice"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Вивести випадкову цитату")
    item2 = types.KeyboardButton("Знайти цитату за автором")
    item3 = types.KeyboardButton("Вийти")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Виберіть потрібну опцію", reply_markup=markup)

# Обработка вывода цитаты
@bot.message_handler(func=lambda message : message.chat.id in user_states2)
def r2(message):
    chat_id = message.chat.id # id чата

    # Если пользователь хочет выйти
    if message.text == "Вийти": 
        del user_states2[chat_id]
        bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())

    # Если мы выбрали способ вывода цитаты
    elif user_states2[chat_id] == "choice":
        # Если мы выбрали вывод случайной цитаты
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

        # Если игрок хочет найти цитату по автору
        elif message.text == "Знайти цитату за автором":
            user_states2[chat_id] = "author"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Вийти")
            markup.add(item1)
            bot.send_message(chat_id, "Введіть ім'я автора", reply_markup=markup)

    # После ввода имени автора
    elif user_states2[chat_id] == "author":
        js = open_json()
        if js[str(chat_id)].get(message.text) != None:
            bot.send_message(chat_id, get_quotes(js, chat_id, message.text), parse_mode='Markdown')
            bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())
            del user_states2[chat_id]
        else:
            del user_states2[chat_id]
            bot.send_message(chat_id, "Нажаль, цитат від цього автора не знайдено :(", reply_markup=main_menu())


# Если запросили удаление цитаты
@bot.message_handler(func=lambda message: message.text == "Видалити цитату")
def r3(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Вийти")
    markup.add(item1)
    user_states3[message.chat.id] = 'author'
    bot.send_message(message.chat.id, "Введіть ім'я автора цитати", reply_markup=markup)


# Обработка удаления цитаты
@bot.message_handler(func=lambda message: message.chat.id in user_states3.keys())
def r4(message):
    chat_id = message.chat.id
    if message.text == "Вийти":
        del user_states3[chat_id]
        bot.send_message(chat_id, "Ви в головному меню", reply_markup=main_menu())

    # Если он ввел имя автора
    elif user_states3[chat_id] == 'author':
        js = open_json()
        # Если его нет
        if js[str(chat_id)].get(message.text) == None:
            del user_states3[chat_id]
            bot.send_message(chat_id, "Нажаль, цитат з цим автором не знайдено :(", reply_markup=main_menu())

        # Если такой автор есть
        else:
            quotes = js[str(chat_id)][message.text]
            mes = "Оберіть цитату для видалення (Відправте її номер)"
            for i in range(len(quotes)):
                mes += f"\n\n*{i}* : {quotes[i]}"

            user_states3[chat_id] = message.text
            bot.send_message(chat_id, mes, parse_mode='Markdown')

    # Если он выбрал цитату для удаления
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