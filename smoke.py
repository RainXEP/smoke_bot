import threading
import telebot
import time
import random

bot = telebot.TeleBot('6896373452:AAFgVQcGNIfaG09TCdGPeh_TLKsmnsptP2U')

ongoing_polls = {}

# Dictionary to store start times of smoking sessions
start_times = {}


# Function to handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Здарова бандиты. Нужна помощь - вводи /help")


# Function to handle the SMOKE button press
@bot.message_handler(commands=['smoke'])
def start_smoke_poll(message):
    chat_id = message.chat.id
    if chat_id not in ongoing_polls:
        # Start a new poll
        poll_message = bot.send_poll(chat_id, "it's time to smoke",
                                     options=['Go-Go-Go 🏃‍', 'Нет, я "очень" занят 🙅', 'Уже тут 👋'],
                                     is_anonymous=False,
                                     open_period=600)  # 10 minutes
        ongoing_polls[chat_id] = poll_message.poll.id
        start_times[chat_id] = time.time()

        # Set a timer to automatically stop the poll after 4 minutes
        bot.send_message(chat_id, "Перекур будет закрыт автоматически через 45 минут.")
        bot.send_message(chat_id, "Чтобы завершить перекур вручную, используйте команду /stop.")
        bot.send_message(chat_id, "Ждем минуты 3 и выходим на улицу :)")
        timer = threading.Timer(2700, stop_poll, args=[message])
        timer.start()

        # Set a timer to send a message after 3 minutes
        message_timer = threading.Timer(180, send_end_message, args=[chat_id])
        message_timer.start()
    else:
        bot.reply_to(message, "Опрос уже запущен. Пожалуйста, дождитесь завершения текущего опроса.")


def send_end_message(chat_id):
    bot.send_message(chat_id, "Больше не ждем, мы пошли ;) ")


# Function to handle poll updates
@bot.message_handler(content_types=['poll'])
def handle_poll_update(poll):
    chat_id = poll.chat.id
    poll_id = poll.id

    if chat_id in ongoing_polls.values() and poll_id == ongoing_polls[chat_id]:
        # Check if poll is closed
        if poll.is_closed:
            # Get the number of votes for each option
            option_votes = {option.text: option.voter_count for option in poll.options}

            # Check if any option received 100% votes
            if option_votes.get('Го-го-го', 0) == poll.total_voter_count:
                bot.send_message(chat_id, "Все согласились! Отсчет времени начинается.")
                # Start counting time spent in break
                start_times[chat_id] = time.time()
            elif option_votes.get('Го-го-го', 0) == 1:
                bot.send_message(chat_id, "Сорри, ты одинок, кури сам")
            else:
                # Send users who voted for 'Го-го-го'
                users_voted = [user.user for user in poll.options[0].voters]
                for user in users_voted:
                    bot.send_message(chat_id, f"{user.first_name} проголосовал за то, чтобы покурить, красава")
                users_voted_no = [user.user for user in poll.options[1].voters]
                for user in users_voted_no:
                    bot.send_message(chat_id, f"{user.first_name} пиздец как сильно занят, поэтому не выйдет")


@bot.message_handler(commands=['stop'])
def stop_poll(message):
    chat_id = message.chat.id
    if chat_id in ongoing_polls:
        start_time = start_times.get(chat_id, 0)
        current_time = time.time()
        duration = int(current_time - start_time)  # Duration in seconds
        minutes, seconds = divmod(duration, 60)
        bot.reply_to(message, f"Время потраченное на перекур: {minutes:02d}:{seconds:02d}")
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
    help_text = "/smoke - Начать опрос\n" \
                "/alreadyopened - Узнать, начаты ли какие-нибудь опросы\n" \
                "/stop - Завершить перекур\n" \
                "/food - Начать опрос для выбора места для обеда\n" \
                "/funny_function - 🤡"
    bot.reply_to(message, help_text)


ongoing_food_polls = {}


@bot.message_handler(commands=['food'])
def start_food_poll(message):
    chat_id = message.chat.id
    if chat_id not in ongoing_food_polls:
        # Start a new food poll
        poll_message = bot.send_poll(chat_id, "Время обеда, что делаем? 🤔🕐🥩",
                                     options=['Бесказан (Плов-лагман примерно, дешево и быстро) 🫖',
                                              'Столовая на Абая-Гагарина (джаст э регуляр столовая, вариант плотного и недорого обеда) 🥪',
                                              'Апрель (а когда не обедали) 🤌',
                                              'Asian Barbeque (что-то на азиатском) 🍜 🥢',
                                              'обед с собой 🌝 ',
                                              'Sorry guys, ORAZA 🕌',
                                              'На хате пообедаю ✌️🚶‍',
                                              'Кальян раздуть в чайхане 🤙'],
                                     is_anonymous=False)
        ongoing_food_polls[chat_id] = poll_message.message_id

        timer = threading.Timer(1200, stop_food_poll, args=[chat_id, poll_message.message_id])  # И здесь
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
                                        option.text not in ['обед с собой 🌝 ', 'Sorry guys, ORAZA 🕌',
                                                            'На хате пообедаю ✌️🚶‍']]
                    if len(filtered_options) > 0:
                        winning_option = random.choice(filtered_options).text
                    else:
                        winning_option = random.choice(options_with_max_votes).text
                    bot.send_message(chat_id, f"Место выбрано - решили что {winning_option} лучший вариант сегодня. Приятного аппетита!")
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
