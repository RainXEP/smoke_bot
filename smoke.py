import threading
import telebot
import time
import random

import requests

import anectodes

from config.cfg import basic_config

bot = telebot.TeleBot(basic_config.bot_token)


ongoing_polls = {}

# Dictionary to store start times of smoking sessions
start_times = {}

smoke_food_topic_id = 61


## jokes_url = ['https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Dark,Spooky?format=txt', 'https://icanhazdadjoke.com/']

@bot.message_handler(commands=['joke'])
def send_joke(message):
    chat_id = message.chat.id
    # headers = {'Accept': 'text/plain'}
    # response = requests.get(url=random.choice(jokes_url), headers=headers)
    # joke = response.text
    bot.send_message(chat_id, random.choice(anectodes.mega_jokes), message_thread_id=smoke_food_topic_id)


# Function to handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    print("chat_id:", message.chat.id)
    bot.reply_to(message, "Здарова бандиты. Нужна помощь - вводи /help")


# Function to handle the SMOKE button press
@bot.message_handler(commands=['smoke'])
def start_smoke_poll(message):
    chat_id = message.chat.id

    if chat_id not in ongoing_polls:
        # Start a new poll
        poll_message = bot.send_poll(message.chat.id, "it's time to smoke",
                                     options=['Go-Go-Go 🏃‍', 'Нет, я "очень" занят 🙅', 'Уже тут 👋'],
                                     is_anonymous=False,
                                     open_period=600,
                                     message_thread_id=smoke_food_topic_id)  # выбор конкретного топика, в нашем случае это ветка smoke/food
        ongoing_polls[chat_id] = poll_message.poll.id
        start_times[chat_id] = time.time()

        # Set a timer to automatically stop the poll after 4 minutes
        bot.send_message(message.chat.id, "Перекур будет закрыт автоматически через 45 минут.",
                         message_thread_id=smoke_food_topic_id, disable_notification=True)
        bot.send_message(message.chat.id, "Чтобы завершить перекур вручную, используйте команду /stop",
                         message_thread_id=smoke_food_topic_id, disable_notification=True)
        bot.send_message(message.chat.id, "Ждем минуты 3 и выходим на улицу :)", message_thread_id=smoke_food_topic_id,
                         disable_notification=True)
        timer = threading.Timer(2700, stop_poll, args=[message])
        timer.start()

        # Set a timer to send a message after 3 minutes
        message_timer = threading.Timer(180, send_end_message, args=[chat_id])
        message_timer.start()
    else:
        bot.reply_to(message, "Опрос уже запущен. Пожалуйста, дождитесь завершения текущего опроса.")


def send_end_message(chat_id):
    bot.send_message(chat_id, "Больше не ждем, мы пошли ;)", message_thread_id=smoke_food_topic_id)


@bot.message_handler(commands=['stop'])
def stop_poll(message):
    chat_id = message.chat.id
    if chat_id in ongoing_polls:
        start_time = start_times.get(chat_id, 0)
        current_time = time.time()
        duration = int(current_time - start_time)  # Duration in seconds
        minutes, seconds = divmod(duration, 60)
        bot.reply_to(message, f"Всем спасибо, возвращайтесь к своим задачам")
        del ongoing_polls[chat_id]
        del start_times[chat_id]
    else:
        bot.reply_to(message, "В данный момент нет активных перекуров.")


@bot.message_handler(commands=['alreadyopened'])
def already_opened_poll(message):
    chat_id = message.chat.id
    if chat_id in ongoing_polls:
        bot.reply_to(message, "Опрос начат: True")
    else:
        bot.reply_to(message, "Опрос начат: False")


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "/smoke - начать опрос для перекура\n" \
                "/alreadyopened - узнать, начаты ли уже опросы\n" \
                "/stop - завершить перекур\n" \
                "/food - начать опрос для выбора места для обеда\n" \
                "/funny_function - 🤡\n" \
                "/joke - 500 неприличных анекдотов"
    bot.reply_to(message, help_text)


ongoing_food_polls = {}


@bot.message_handler(commands=['food'])
def start_food_poll(message):
    chat_id = message.chat.id

    if chat_id not in ongoing_food_polls:
        # Start a new food poll
        poll_message = bot.send_poll(chat_id, "Время обеда, куда идем? 🤔🕐🥩",
                                     options=['Бесказан (Плов-лагман примерно, дешево и быстро) 🫖',
                                              'Столовая на Абая-Гагарина (джаст э регуляр столовая, вариант плотного и недорого обеда) 🥪',
                                              'Апрель (а когда не обедали) 🤌',
                                              'Asian Barbeque (что-то на азиатском) 🍜 🥢',
                                              'Salsabil (V.I.P BesKazan)  😎',
                                              'Хареба (Дорого, но бизнес ланчи по 2к вроде как) 🥟',
                                              'Грузинский двор (А почему нет?) 🍖',
                                              'Обед с собой 🌝 / Иду обедать с другими',
                                              'На хате пообедаю ✌️🚶‍',
                                              'Кальян раздуть в чайхане 🤙'],
                                     is_anonymous=False,
                                     message_thread_id=smoke_food_topic_id)
        ongoing_food_polls[chat_id] = poll_message.message_id

        timer = threading.Timer(900, stop_food_poll, args=[chat_id, poll_message.message_id])
        timer.start()
    else:
        bot.reply_to(message, "Опрос на выбор места обеда уже запущен. Пожалуйста, дождитесь его завершения.")


def stop_food_poll(chat_id, message_id):
    if chat_id in ongoing_food_polls:
        poll_message_id = ongoing_food_polls.pop(chat_id)
        if poll_message_id:
            try:
                poll_results = bot.stop_poll(chat_id, message_id)
                if poll_results:
                    options_with_max_votes = [option for option in poll_results.options if option.voter_count == max(
                        option.voter_count for option in poll_results.options)]
                    filtered_options = [option for option in options_with_max_votes if
                                        option.text not in ['Обед с собой 🌝 / Иду обедать с другими',
                                                            'На хате пообедаю ✌️🚶‍']]
                    if len(filtered_options) > 0:
                        winning_option = random.choice(filtered_options).text
                    else:
                        winning_option = random.choice(options_with_max_votes).text
                    bot.send_message(chat_id,
                                     f"Место выбрано - решили что {winning_option} лучший вариант сегодня. Приятного аппетита!",
                                     message_thread_id=smoke_food_topic_id)
            except Exception as e:
                print("An error occurred while stopping the poll:", e)


@bot.message_handler(func=lambda message: True)
def handle_invalid_commands(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "Хуйню не пиши, такой команды нет")
    if message.text.startswith('/funny_function'):
        bot.reply_to(message, "Ничего тут нет, иди работай 🫵")


# Start the bot
bot.polling()
