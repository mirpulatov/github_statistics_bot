import time
import os
import datetime
import re
import telebot
import commits_stat

from telebot import types

TOKEN = '604239486:AAGW9MvXqth4cn0_egI_HvDrrp5bb1S8J8Q'

bot = telebot.TeleBot(TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('Week info')
    markup.row('Month info')
    markup.row('HELP!')
    markup.resize_keyboard = True
    bot.send_message(message.chat.id, "Hi, to get info enter first and last date in format:YYYY-MM-DD YYYY-MM-DD",
                     reply_markup=markup)


@bot.message_handler(regexp='HELP!|/help|help')
def handle_help(message):
    bot.reply_to(message, "Enter first and last date in format: YYYY-MM-DD YYYY-MM-DD")


@bot.message_handler(regexp='Week info')
def handle_week(message):
    now_date = str(datetime.datetime.now())[:10]
    start_date = str(datetime.datetime.now() - datetime.timedelta(weeks=1))[:10]
    bot.reply_to(message, "We are generating a plot, please wait a minute")
    rand_num = commits_stat.parse_and_draw(start_date, now_date)
    photo = open('plot' + str(rand_num) + '.png', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()
    os.remove('plot' + str(rand_num) + '.png')


@bot.message_handler(regexp='Month info')
def handle_month(message):
    now_date = str(datetime.datetime.now())[:10]
    start_date = str(datetime.datetime.now() - datetime.timedelta(weeks=4))[:10]
    bot.reply_to(message, "We are generating a plot, please wait a minute")
    rand_num = commits_stat.parse_and_draw(start_date, now_date)
    photo = open('plot' + str(rand_num) + '.png', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()
    os.remove('plot' + str(rand_num) + '.png')


@bot.message_handler(content_types=['text'])
def handle_info(message):

    date_pattern = re.compile('^(?P<date1>\d{4}-\d{2}-\d{2})( (?P<date2>\d{4}-\d{2}-\d{2})|)$', re.I)

    date_match = date_pattern.match(message.text)

    if date_match:
        date_data = date_match.groupdict()

        if date_data.get('data2', None):
            start_date = date_data.get('date1').strip()
            end_date = date_data.get('date2').strip()
            bot.reply_to(message, "We are generating a plot, please wait a minute")
            rand_num = commits_stat.parse_and_draw(start_date, end_date)
            photo = open('plot' + str(rand_num) + '.png', 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            os.remove('plot' + str(rand_num) + '.png')
        else:
            start_date = date_data.get('date1').strip()
            bot.reply_to(message, "We are generating a plot, please wait a minute")
            rand_num = commits_stat.parse_and_draw(start_date)
            photo = open('plot' + str(rand_num) + '.png', 'rb')
            bot.send_photo(message.chat.id, photo)
            photo.close()
            os.remove('plot' + str(rand_num) + '.png')

    else:
        bot.reply_to(message, 'Incorrect date format. Please, try again "YYYY-MM-DD YYYY-MM-DD"')


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(15)
