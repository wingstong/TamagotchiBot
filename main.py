import time
import datetime
import random
import threading
import telebot
from telebot import types

bot = telebot.TeleBot('')

user_data = {}
user_staff = {}
user_work = {}
user_shop = {}
def update_stats():
    current_time = datetime.datetime.now()

    for user_id in user_data:
        last_update_time = user_data[user_id].get('last_update_time', current_time)
        time_difference = current_time - last_update_time

        if time_difference.total_seconds() >= 3600:
            user_data[user_id]['food'] = max(user_data[user_id]['food'] - 16, 0)
            user_data[user_id]['mood'] = max(user_data[user_id]['mood'] - 18, 0)
            user_data[user_id]['sleep'] = max(user_data[user_id]['sleep'] - 13, 0)
            user_data[user_id]['last_update_time'] = current_time

        if user_data[user_id]['food'] == 0:
            bot.send_message(user_id, "Твоей жабке плохо без еды 🐸🍽️")
        if user_data[user_id]['mood'] == 0:
            bot.send_message(user_id, "Твоя жабка грустит 😢")
        if user_data[user_id]['sleep'] == 0:
            bot.send_message(user_id, "Твоя жабка очень устала.. 😴")

    threading.Timer(3600, update_stats).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    button_start = types.InlineKeyboardButton(text='🐸Начать игру', callback_data='start_game')
    markup.add(button_start)
    bot.send_message(message.chat.id, 'Привет!🌿 Я - Froggo, маленький игровой бот по типу тамагчочи! '
                                      '\n\nЧтобы начать выращивать свою жабку, нажми кнопку \n🐸Начать Игру', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def start_game(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=" Отлично! Самое время дать жабке имя:")
    bot.register_next_step_handler(call.message, create_frog)
def create_frog(message):
    frog_name = message.text
    user_data[message.from_user.id] = {
        'name': frog_name,
        'level': 1,
        'progress': 0,
        'food': 60,
        'mood': 40,
        'sleep': 90,
        'last_update_time': datetime.datetime.now()  #сохранение времени последнего обновления
    }
    user_staff[message.from_user.id] = {
        '🕷': 5,
        '🪲': 5,
        '🪱': 3,
        '🐛': 1,
        '🪰': 0,
        '🦋': 0,
        '🐞': 0
    }
    user_shop[message.from_user.id] = {
        '💊': 0,
        '🧪': 0,
        '🍲': 0,
        '🍕': 0,
        '🍣': 0,
        '🍫': 0
    }
    user_work[message.from_user.id] = {
        '💰': 500
    }

    bot.send_message(message.chat.id, f'Жабка {frog_name} создана! Успехов!')
    update_stats()

@bot.message_handler(commands=['frog'])
def frog_stats(message):
    user_id = message.from_user.id
    if message.from_user.id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    markup = types.InlineKeyboardMarkup()
    feed_button = types.InlineKeyboardButton(text="🪲 Покормить", callback_data="feed")
    play_button = types.InlineKeyboardButton(text="🎲 Поиграть", callback_data="play")
    markup.row(feed_button, play_button)
    sleep_button = types.InlineKeyboardButton(text="💤 Спать", callback_data="sleep")
    markup.row(sleep_button)
    bot.send_sticker(message.chat.id, sticker='CAACAgIAAxkBAAEBX7dlJFwD4OxjcC4ruIIXG8TWogABoEQAAgg8AAJHbiBJmJYxPAtIGRswBA')
    bot.send_message(message.chat.id,f"🐸  Имя: {user_data[user_id]['name']}\n"
                                     f"✨  Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%\n"
                                     f". . . . . . . . . . . . . . .\n\n🌿  Настроение: {user_data[user_id]['mood']}%\n"
                                     f"🪱  Еда: {user_data[user_id]['food']}%\n💤  Сон: {user_data[user_id]['sleep']}%",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "sleep")
def sleep_frog(call):
    markup = types.InlineKeyboardMarkup()
    s_sleep = types.InlineKeyboardButton(text='3 часа', callback_data='short_sleep')
    l_sleep = types.InlineKeyboardButton(text='7 часов', callback_data='long_sleep')
    markup.row(s_sleep, l_sleep)
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
    markup.row(back_button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="💤<b> Сон</b>\n . . . . . . . . . . . . . . . \n\n<i>Самое время отдохнуть. \n"
                               "Отправь жабку спать на \n3 часа (+40% сна) или на \n7 часов (+100% сна)</i>",
                          parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "short_sleep")
def s_sleep(call):
    user_id = call.from_user.id
    if user_data[user_id]['sleep'] == 100:
        bot.answer_callback_query(callback_query_id=call.id, text='Жаба пока не хочет спать...')
        return
    if call.from_user.id in user_data and 'sleep_return' in user_data[call.from_user.id]:
        bot.send_message(call.message.chat.id, "💤 Твоя жабка уже спит")
        return
    if 'work_return' in user_data[call.from_user.id] or 'walk_return' in user_data[call.from_user.id]:
        bot.send_message(call.message.chat.id, "💤 Твоя жабка сейчас не дома")
        return

    current_time = datetime.datetime.now()
    return_time = current_time + datetime.timedelta(seconds=10800) #10800
    return_time_formatted = return_time.strftime("%H:%M")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='💤<b> Сон</b>\n . . . . . . . . . . . . . . . \n\n'
                               '<i>Твоя жабка прилегла\nнемного отдохнуть и вернется\n'
                               'к тебе через несколько часов..  </i>', parse_mode='html')
    bot.answer_callback_query(callback_query_id=call.id,
                              text="Жабка легла спать :)")

    user_data[user_id]['sleep_return'] = return_time
    bot.send_message(call.message.chat.id, f"💤 Жабка проснется в {return_time_formatted}")
    time.sleep(10800)
    user_data[user_id]['sleep'] += 40
    user_data[user_id]['progress'] += 15
    user_data[user_id]['sleep'] = min(user_data[user_id]['sleep'], 100)

    if user_data[user_id]['progress'] >= 100:
        user_data[call.from_user.id]['level'] += 1
        user_data[call.from_user.id]['progress'] = 0
    bot.send_message(call.message.chat.id, f"Твоя жаба проснулась и полна сил!"
                                           f"Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")
    del user_data[user_id]['sleep_return']

@bot.callback_query_handler(func=lambda call: call.data == "long_sleep")
def l_sleep(call):
    user_id = call.from_user.id
    if user_data[user_id]['sleep'] == 100:
        bot.answer_callback_query(callback_query_id=call.id, text='Жаба пока не хочет спать...')
        return
    if 'sleep_return' in user_data[call.from_user.id]:
        bot.send_message(call.message.chat.id, "💤 Твоя жабка уже спит")
        return
    if 'work_return' in user_data[call.from_user.id] or 'walk_return' in user_data[call.from_user.id]:
        bot.send_message(call.message.chat.id, "💤 Твоя жабка сейчас не дома")
        return

    current_time = datetime.datetime.now()
    return_time = current_time + datetime.timedelta(seconds=25200) #25200
    return_time_formatted = return_time.strftime("%H:%M")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='💤<b> Сон</b>\n . . . . . . . . . . . . . . . \n\n<i>Твоя жабка прилегла\nнемного отдохнуть и вернется\nк тебе через несколько часов..  </i>',
                          parse_mode='html')
    bot.answer_callback_query(callback_query_id=call.id,
                              text="Жабка легла спать :)")

    user_data[user_id]['sleep_return'] = return_time
    bot.send_message(call.message.chat.id, f"💤 Жабка проснется в {return_time_formatted}")
    time.sleep(25200)
    user_data[user_id]['sleep'] += 100
    user_data[user_id]['progress'] += 25
    user_data[user_id]['sleep'] = min(user_data[user_id]['sleep'], 100)

    if user_data[user_id]['progress'] >= 100:
        user_data[call.from_user.id]['level'] += 1
        user_data[call.from_user.id]['progress'] = 0
    bot.send_message(call.message.chat.id, f"Твоя жаба проснулась и полна сил! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")
    del user_data[user_id]['sleep_return']

@bot.callback_query_handler(func=lambda call: call.data == "play")
def play_with_frog(call):
    user_id = call.from_user.id
    if user_data[user_id]['mood'] == 100:
        bot.answer_callback_query(callback_query_id=call.id, text='Жаба устала.. Поиграй с ней немного позже')
        return
    play_phrases = ["Вы почесали жабе брюшко\n. . . . \nОна довольно помахала невидимым хвостом",
                    "Вы бросили жабе палочку\n. . . . \nОна принесла ее обратно",
                    "Вы включили жабе сериал\n. . . . \nЕе затянуло на несколько часов",
                    "Вы начали играть с жабой в прятки\n. . . . \nОна проиграла",
                    "Вы начали играть с жабой в прятки\n. . . . \nОна выиграла"]
    # Выбираем случайную фразу из списка
    random_phrase = random.choice(play_phrases)
    bot.send_message(call.message.chat.id, text=random_phrase)

    user_data[user_id]['mood'] += 30
    user_data[user_id]['progress'] += 10
    user_data[user_id]['mood'] = min(user_data[user_id]['mood'], 100)

    if user_data[user_id]['progress'] >= 100:
        user_data[user_id]['level'] += 1
        user_data[user_id]['progress'] = 0

    bot.answer_callback_query(callback_query_id=call.id,
                              text=f"Вы поиграли с жабкой. Уровень: {user_data[user_id]['level']} | "
                                   f"{user_data[user_id]['progress']}%")
    bot.send_message(call.message.chat.id, "Настроение жабки увеличилось на 30%")

# Обработчик нажатия на кнопку покормить
@bot.callback_query_handler(func=lambda call: call.data == "feed")
def feed_frog(call):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    food_buttons = []
    for item, count in user_staff[user_id].items():
        if count > 0:
            food_buttons.append(types.InlineKeyboardButton(text=item + f" {count}", callback_data="food_" + item))
    for item, count in user_shop[user_id].items():
        if count > 0:
            food_buttons.append(types.InlineKeyboardButton(text=item + f" {count}", callback_data="food_" + item))
    markup.add(*food_buttons)
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
    markup.row(back_button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери еду:", reply_markup=markup)

# Обработчик нажатия на кнопку с едой
@bot.callback_query_handler(func=lambda call: call.data.startswith("food_"))
def feed_frog_food(call):
    user_id = call.from_user.id
    food_item = call.data.split("_")[1]
    if user_data[user_id]['food'] == 100:
        bot.answer_callback_query(callback_query_id=call.id, text='Жаба объелась... Покорми ее немного позже')
        return

    if food_item in user_staff[user_id] and user_staff[user_id][food_item] > 0:
        user_data[user_id]['progress'] += 10
        user_data[user_id]['food'] += 20
        user_staff[user_id][food_item] -= 1
        user_data[user_id]['food'] = min(user_data[user_id]['food'], 100)

        if user_data[user_id]['progress'] >= 100:
            user_data[user_id]['level'] += 1
            user_data[user_id]['progress'] = 0
        bot.answer_callback_query(callback_query_id=call.id,
                                  text=f"Жабка поела! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")

    elif food_item in user_shop[user_id] and user_shop[user_id][food_item] > 0:
        user_data[user_id]['progress'] += 10
        user_shop[user_id][food_item] -= 1

        if food_item == "💊":
            user_data[user_id]['food'] = 100
            user_data[user_id]['mood'] = 100
            user_data[user_id]['sleep'] = 100
            if user_data[user_id]['progress'] >= 100:
                user_data[user_id]['level'] += 1
                user_data[user_id]['progress'] = 0
            bot.answer_callback_query(callback_query_id=call.id,
                                      text=f"Жабка поела! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")
            return

        if food_item == "🧪":
            user_data[user_id]['food'] = min(user_data[user_id]['food'] + 50, 100)
            user_data[user_id]['mood'] = min(user_data[user_id]['mood'] + 50, 100)
            user_data[user_id]['sleep'] = min(user_data[user_id]['sleep'] + 50, 100)

            if user_data[user_id]['progress'] >= 100:
                user_data[user_id]['level'] += 1
                user_data[user_id]['progress'] = 0
            bot.answer_callback_query(callback_query_id=call.id,
                                      text=f"Жабка поела! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")
            return

        if food_item == "🍲":
            user_data[user_id]['food'] = 100
            if user_data[user_id]['progress'] >= 100:
                user_data[user_id]['level'] += 1
                user_data[user_id]['progress'] = 0
            bot.answer_callback_query(callback_query_id=call.id,
                                      text=f"Жабка поела! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")
            return

        if food_item == "🍕" or "🍣" or "🍫":
            user_data[user_id]['food'] += 20
            user_data[user_id]['food'] = min(user_data[user_id]['food'], 100)
            if user_data[user_id]['progress'] >= 100:
                user_data[user_id]['level'] += 1
                user_data[user_id]['progress'] = 0
            bot.answer_callback_query(callback_query_id=call.id,
                                      text=f"Жабка поела! Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%")


    else:
        bot.answer_callback_query(callback_query_id=call.id, text=f"Упс, закончилось.")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back_button(call):
    user_id = call.from_user.id
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id-1)

    markup = types.InlineKeyboardMarkup()
    feed_button = types.InlineKeyboardButton(text="🪲 Покормить", callback_data="feed")
    play_button = types.InlineKeyboardButton(text="🎲 Поиграть", callback_data="play")
    markup.row(feed_button, play_button)
    sleep_button = types.InlineKeyboardButton(text="💤 Спать", callback_data="sleep")
    markup.row(sleep_button)
    bot.send_sticker(call.message.chat.id, sticker='CAACAgIAAxkBAAEBX7dlJFwD4OxjcC4ruIIXG8TWogABoEQAAgg8AAJHbiBJmJYxPAtIGRswBA')
    bot.send_message(call.message.chat.id,
                     f"🐸  Имя: {user_data[user_id]['name']}\n✨  Уровень: {user_data[user_id]['level']} | {user_data[user_id]['progress']}%\n"
                     f". . . . . . . . . . . . . . .\n\n🌿  Настроение: {user_data[user_id]['mood']}%\n🪱  Еда: {user_data[user_id]['food']}%\n 💤  Сон: {user_data[user_id]['sleep']}%", reply_markup=markup)

@bot.message_handler(commands=['forest'])
def go_to_forest(message):
    if message.from_user.id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    if ('walk_return' in user_data[message.from_user.id] or
            'work_return' in user_data[message.from_user.id]):
        bot.send_message(message.chat.id, "Твоя жабка уже гуляет и скоро вернется!")
        return
    if 'sleep_return' in user_data[message.from_user.id]:
        bot.send_message(message.chat.id,
                         "🌲 <b> Лес</b>\n. . . . . . . . . . . . . . .\n\n<i>💤 Твоя жаба сейчас спит</i>",
                         parse_mode='html')
        return
    if message.from_user.id in user_data and user_data[message.from_user.id]['sleep'] < 40:
        bot.send_message(message.chat.id,
                         "🌲 <b> Лес</b>\n. . . . . . . . . . . . . . .\n\n"
                         "<i>Жаба с радостью бы \nсейчас пошла гулять, \nно она очень хочет спать.. </i>",
                         parse_mode='html')
        return
    markup = types.InlineKeyboardMarkup()
    walk_button = types.InlineKeyboardButton(text="🌲 Гулять", callback_data="walk")
    markup.add(walk_button)
    bot.reply_to(message, f"🌲 <b> Лес</b>\n"
                          f". . . . . . . . . . . . . . .\n\n"
                                      "<i>Отправь жабку гулять\nв лесок неподалеку. "
                          "Она может\nнайти там разные интересные\nштучки!</i>", parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "walk")
def go_walk(call):
    user_data[call.from_user.id]['progress'] += 15
    if user_data[call.from_user.id]['progress'] >= 100:
        user_data[call.from_user.id]['level'] += 1
        user_data[call.from_user.id]['progress'] = 0

    current_time = datetime.datetime.now()
    return_time = current_time + datetime.timedelta(seconds=7200)
    return_time_formatted = return_time.strftime("%H:%M")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='🌲 <b> Лес</b>\n . . . . . . . . . . . . . . . \n\n'
                               '<i>Твоя жабка гуляет и \nвернется через 2 часа!</i>', parse_mode='html')
    bot.answer_callback_query(callback_query_id=call.id,
                              text=f"Твоя жаба скоро к тебе вернётся! "
                                   f"Уровень: {user_data[call.from_user.id]['level']} | {user_data[call.from_user.id]['progress']}%")

    user_data[call.from_user.id]['walk_return'] = return_time
    bot.send_message(call.message.chat.id, f"<i>💤 Жабка вернётся из леса в {return_time_formatted}</i>", parse_mode='html')
    time.sleep(7200)
    found_items = random.sample(user_staff[call.from_user.id].items(), random.randint(1, 4))
    found_items_message = ("🏡 Твоя жабка вернулась из леса!\n"
                           "Смотри, что она нашла:\n\n")
    for item, count in found_items:
        found_count = random.randint(1, 5)
        user_staff[call.from_user.id][item] += found_count
        found_items_message += f"- {item.capitalize()}: {found_count}\n"
    bot.send_message(call.message.chat.id, found_items_message)
    del user_data[call.from_user.id]['walk_return']

@bot.message_handler(commands=['storage'])
def show_storage(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    storage_text = ("⛺️ <b> Инвентарь</b>\n. . . . . . . . . . . . . . .\n\n")
    for item, count in user_work[user_id].items():
        storage_text += f"{item}: {count}\n"
    for item, count in user_staff[user_id].items():
        storage_text += f"{item}: {count}\n"
    for item, count in user_shop[user_id].items():
        storage_text += f"{item}: {count}\n"
    bot.reply_to(message, storage_text, parse_mode='html')

@bot.message_handler(commands=['work'])
def go_to_work(message):
    if message.from_user.id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    if message.from_user.id in user_data:
        if user_data[message.from_user.id]['level'] < 7:
            bot.send_message(message.chat.id,
                             "Твоя жабка еще слишком маленькая \nдля работы, подожди хотя бы до 7 уровня^^ ")
            return
        if 'work_return' in user_data[message.from_user.id]:
            bot.send_message(message.chat.id, "Не беспокойся, с твоей жабой \nвсе хорошо, она скоро вернется:)")
            return
        if 'sleep_return' in user_data[message.from_user.id]:
            bot.send_message(message.chat.id,
                             "🖥 <b> Работа</b>\n. . . . . . . . . . . . . . .\n\n<i>💤 Твоя жаба сейчас спит</i>",
                             parse_mode='html')
            return
        if 'walk_return' in user_data[message.from_user.id]:
            bot.send_message(message.chat.id,
                             "🖥 <b> Работа</b>\n. . . . . . . . . . . . . . .\n\n<i>💤 Твоя жаба сейчас гуляет</i>",
                             parse_mode='html')
            return
        if user_data[message.from_user.id]['sleep'] < 40:
            bot.send_message(message.chat.id,
                             "🖥 <b> Работа</b>\n. . . . . . . . . . . . . . .\n\n"
                             "<i>Твоя жабка устала \nи хочет спать, сейчас \nона не может пойти \nна работу :( </i>",
                             parse_mode='html')
            return
    markup = types.InlineKeyboardMarkup()
    work_button = types.InlineKeyboardButton(text="🖥 Работать", callback_data="work")
    markup.add(work_button)
    bot.reply_to(message, f"🖥 <b> Работа</b>\n"
                          f". . . . . . . . . . . . . . .\n\n"
                          "<i>Твоя жаба подросла и теперь\nсама может ходить на работу\nи зарабатывать монетки!</i>",
                 parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "work")
def work(call):
    user_data[call.from_user.id]['progress'] += 20
    if user_data[call.from_user.id]['progress'] >= 100:
        user_data[call.from_user.id]['level'] += 1
        user_data[call.from_user.id]['progress'] = 0

    current_time = datetime.datetime.now()
    return_time = current_time + datetime.timedelta(seconds=10800) #10800
    return_time_formatted = return_time.strftime("%H:%M")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='🖥 <b> Работа </b>\n . . . . . . . . . . . . . . . \n\n'
                               '<i>Твоя жаба отправилась на\nзаработки и вернётся через 3 часа... </i>',
                          parse_mode='html')
    bot.answer_callback_query(callback_query_id=call.id,
                              text=f"Твоя жаба скоро к тебе вернётся!"
                                   f"Уровень: {user_data[call.from_user.id]['level']} | {user_data[call.from_user.id]['progress']}%")

    user_data[call.from_user.id]['work_return'] = return_time
    bot.send_message(call.message.chat.id, f"💤 Жабка вернётся с работы в {return_time_formatted}")
    time.sleep(10800)
    found_items = user_work[call.from_user.id].items()
    found_items_message = ("🏡 Твоя жабка вернулась с работы!\n"
                           "Смотри, сколько она заработала:\n\n")
    for item, count in found_items:
        found_count = random.randint(20, 100)
        user_work[call.from_user.id][item] += found_count
        found_items_message += f"- {item.capitalize()}: {found_count}\n"
    bot.send_message(call.message.chat.id, found_items_message)
    del user_data[call.from_user.id]['work_return']

@bot.callback_query_handler(func=lambda call: call.data == "backs")
def back_to_shop(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    markup = types.InlineKeyboardMarkup()
    pill_button = types.InlineKeyboardButton(text="💊 за 800💰", callback_data="item_pill")
    potion_button = types.InlineKeyboardButton(text="🧪 за 499💰", callback_data="item_potion")
    markup.row(pill_button, potion_button)
    soup_button = types.InlineKeyboardButton(text="🍲 за 300💰", callback_data="item_soup")
    pizza_button = types.InlineKeyboardButton(text="🍕 за 150💰", callback_data="item_pizza")
    markup.row(soup_button, pizza_button)
    sushi_button = types.InlineKeyboardButton(text="🍣 за 150💰", callback_data="item_sushi")
    choco_button = types.InlineKeyboardButton(text="🍫 за 150💰", callback_data="item_choco")
    markup.row(sushi_button, choco_button)

    bot.send_message(call.message.chat.id, f"💰 <b> Магазин</b>\n"
                                      ". . . . . . . . . . . . . . .\n\n"
                                      "<i>Здесь ты можешь купить\nразные полезные штуки</i>", parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['shop'])
def shop(message):
    if message.from_user.id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    markup = types.InlineKeyboardMarkup()
    pill_button = types.InlineKeyboardButton(text="💊 за 800💰", callback_data="item_pill")
    potion_button = types.InlineKeyboardButton(text="🧪 за 499💰", callback_data="item_potion")
    markup.row(pill_button, potion_button)
    soup_button = types.InlineKeyboardButton(text="🍲 за 300💰", callback_data="item_soup")
    pizza_button = types.InlineKeyboardButton(text="🍕 за 150💰", callback_data="item_pizza")
    markup.row(soup_button, pizza_button)
    sushi_button = types.InlineKeyboardButton(text="🍣 за 150💰", callback_data="item_sushi")
    choco_button = types.InlineKeyboardButton(text="🍫 за 150💰", callback_data="item_choco")
    markup.row(sushi_button, choco_button)

    bot.send_message(message.chat.id, f"💰 <b> Магазин</b>\n"
                                      ". . . . . . . . . . . . . . .\n\n"
                                      "<i>Здесь ты можешь купить\nразные полезные штуки</i>", parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_descr(call):
    item = call.data.split("_")[1]
    description_message = ""
    if item == "pill":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n"
                                "<i>💊 - Волшебная пилюля, \nповышающая все характеристики\nжабы на 100%</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 800💰</i>")
    elif item == "potion":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n"
                                "<i>🧪 - Необычное зелье, \nповышающее все характеристики\nжабы на 50%</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 499💰</i>")
    elif item == "soup":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n"
                                "<i>🍲 - Домашний супчик, \nповышающий сытость жабки на 100%</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 300💰</i>")
    elif item == "pizza":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n <i>🍕 - Обычная пицца, \nвкусная, сытная, калорийная</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 150💰</i>")
    elif item == "sushi":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n"
                                "<i>🍣 - Роллы филадельфия, \nвыбор настоящих гурманов</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 150💰</i>")
    elif item == "choco":
        description_message = "💰 <b> Магазин</b>\n"
        description_message += (". . . . . . . . . . . . . . .\n\n"
                                "<i>🍫 - Молочная шоколадка, \nсамое то, чтобы внезапно порадовать \nсвою жабку</i>"
                                "\n\n. . . . . . . . . . . . . . .\n<i>Цена: 150💰</i>")

    markup = types.InlineKeyboardMarkup()
    buy_button = types.InlineKeyboardButton(text="Купить", callback_data=f"buy_{item}")
    backs_button = types.InlineKeyboardButton(text="Назад", callback_data="backs")
    markup.row(buy_button, backs_button)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=description_message, parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    user_id = call.from_user.id
    item = call.data.split("_")[1]
    if item == "pill":
        if user_work[user_id]['💰'] >= 800:
            user_shop[user_id]['💊'] += 1
            user_work[user_id]['💰'] -= 800
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")

    elif item == "potion":
        if user_work[user_id]['💰'] >= 499:
            user_shop[user_id]['🧪'] += 1
            user_work[user_id]['💰'] -= 499
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")

    elif item == "soup":
        if user_work[user_id]['💰'] >= 300:
            user_shop[user_id]['🍲'] += 1
            user_work[user_id]['💰'] -= 300
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")

    elif item == "pizza":
        if user_work[user_id]['💰'] >= 150:
            user_shop[user_id]['🍕'] += 1
            user_work[user_id]['💰'] -= 150
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")

    elif item == "sushi":
        if user_work[user_id]['💰'] >= 150:
            user_shop[user_id]['🍣'] += 1
            user_work[user_id]['💰'] -= 150
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")

    elif item == "choco":
        if user_work[user_id]['💰'] >= 150:
            user_shop[user_id]['🍫'] += 1
            user_work[user_id]['💰'] -= 150
            bot.answer_callback_query(callback_query_id=call.id, text="Товар уже у тебя в инвентаре!")
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Ой, у тебя не хватает монеток...")\

@bot.message_handler(commands=['donate'])
def send_donate(message):
    if message.from_user.id not in user_data:
        bot.send_message(message.chat.id, "У тебя еще нет жабки :(\nСоздай ее с помощью команды /start")
        return
    bot.reply_to(message, f"🔮 <b> Поддержать</b>\n"
                          f". . . . . . . . . . . . . . .\n\n"
                          f"<i>Номер карты (Тинькофф)</i>\n"
                          f"<code> 5536914159646789 </code>\n"
                          f". . . . . . . . . . . . . . .\n\n"
                          f"<i>Ваша поддержка помогает\nботу развиваться 💕</i>" ,parse_mode='html')

bot.polling(none_stop=True)