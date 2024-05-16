import threading
import telebot
from telebot import apihelper

import time
import random

# from config.cfg import basic_config

import requests
import json
import anectodes
import logging

apihelper.READ_TIMEOUT = 35
apihelper.CONNECT_TIMEOUT = 35

bot = telebot.TeleBot("6896373452:AAFgVQcGNIfaG09TCdGPeh_TLKsmnsptP2U")
GEMINI_API_KEY = "AIzaSyA0efxMtuOX-SI-tLZfsGrXh-cG16pV7Pc"

ongoing_polls = {}

# Dictionary to store start times of smoking sessions
start_times = {}

smoke_food_topic_id = 54  # 61

logging.basicConfig(level=logging.INFO)


def call_gemini_api(query):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {"parts": [{"text": query}]}
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Response: {response.text}")
        print(e)
        return "А? Не услышал, еще раз повтори, брат"


@bot.message_handler(commands=['bot'])
def handle_command(message):

    query = message.text.split(maxsplit=1)
    if len(query) > 1:
        response = call_gemini_api(query[1])
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Для обращения ко мне юзай /bot {твой запрос}")


# jokes_url = ['https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Dark,Spooky?format=txt', 'https://icanhazdadjoke.com/']

@bot.message_handler(commands=['joke'])
def send_joke(message):
    chat_id = message.chat.id
    logging.info(f"Received 'joke' command from {chat_id} and topic_id: {smoke_food_topic_id}")
    # headers = {'Accept': 'text/plain'}
    # response = requests.get(url=random.choice(jokes_url), headers=headers)
    # joke = response.text
    bot.send_message(chat_id, random.choice(anectodes.mega_jokes), message_thread_id=smoke_food_topic_id)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    logging.info(f"Received 'start' command from {chat_id} and topic_id: {smoke_food_topic_id}")

    bot.reply_to(message, "Здарова бандиты. Нужна помощь - вводи /help")


# Function to handle the SMOKE button press
@bot.message_handler(commands=['smoke'])
def start_smoke_poll(message):
    chat_id = message.chat.id
    logging.info(f"Received 'smoke' command from {chat_id} and topic_id: {smoke_food_topic_id}")
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


def send_message_about_money(chat_id):
    bot.send_message(chat_id, "Господа, просьба скинуть деньги за обед, если еще не скинули",
                     message_thread_id=smoke_food_topic_id)


@bot.message_handler(commands=['stop'])
def stop_poll(message):
    chat_id = message.chat.id
    logging.info(f"Received 'stop-smoke' command from {chat_id} and topic_id: {smoke_food_topic_id}")
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
    logging.info(f"Received 'alreadyOpened' command from {chat_id} topic_id: {smoke_food_topic_id}")
    if chat_id in ongoing_polls:
        bot.reply_to(message, "Опрос начат: True")
    else:
        bot.reply_to(message, "Опрос начат: False")


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    logging.info(f"Received 'help' command from {chat_id} topic_id: {smoke_food_topic_id}")
    help_text = "/smoke - начать опрос для перекура\n" \
                "/alreadyopened - узнать, начаты ли уже опросы\n" \
                "/stop - завершить перекур\n" \
                "/food - начать опрос для выбора места для обеда\n" \
                "/funny_function - 🤡\n" \
                "/joke - 500 неприличных анекдотов\n" \
                "/bot {запрос} - Бот ответит почти на любой вопрос\n"
    bot.reply_to(message, help_text)


ongoing_food_polls = {}


@bot.message_handler(commands=['food'])
def start_food_poll(message):
    chat_id = message.chat.id
    logging.info(f"Received 'food' command from {chat_id} topic_id: {smoke_food_topic_id}")
    if chat_id not in ongoing_food_polls:
        # Start a new food poll
        poll_message = bot.send_poll(chat_id, "Время обеда, куда идем? 🤔🕐🥩",
                                     options=['Бесказан 🫖',
                                              'Столовая на Абая-Гагарина 🥪',
                                              'Апрель 🤌',
                                              'Asian Barbeque 🍜 🥢',
                                              'Salsabil 😎',
                                              'Хареба  🥟',
                                              'Грузинский двор 🍖',
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
                   # Добавлен таймер, который запускает сообщение о необходимости скинуть деньги за обед
                    money_message_timer = threading.Timer(3600, send_message_about_money, args=[chat_id])
                    money_message_timer.start()
            except Exception as e:
                print("An error occurred while stopping the poll:", e)


@bot.message_handler(func=lambda message: True)
def handle_invalid_commands(message):
    chat_id = message.chat.id
    logging.info(f"Received 'funny_function' command from {chat_id} and topic_id: {smoke_food_topic_id}")
    if message.text.startswith('/'):
        bot.reply_to(message, "Хуйню не пиши, такой команды нет")
    if message.text.startswith('/funny_function'):
        bot.reply_to(message, "Ничего тут нет, иди работай 🫵")


# Start the bot
def start_bot():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            logging.info("Bot is starting...")
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Bot crashed due to: {e}")
            time.sleep(10)


if __name__ == "__main__":
    start_bot()
