import datetime
import logging.config
import os
import platform
import subprocess
import sys
import threading
import time
import pythoncom
import schedule
import telebot
import wmi
from telebot import types
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

with open(os.path.dirname(os.path.realpath(__file__)) + '/API_token.txt') as file:
    token = file.readline().strip()

#bot = telebot.TeleBot(token)

# logging
logging.basicConfig(filename=os.path.dirname(os.path.realpath(__file__)) + '/log/{}('.format(os.path.splitext(os.path.basename(__file__))[0])+datetime.date.today().isoformat()+').log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[LINE:%(lineno)d] - %(levelname)s - %(message)s')

class CoreTempBot:

    def __init__(self):
        """Start the bot."""

        # Create the EventHandler and pass it your bot's token.
        updater = Updater(token)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram

        # on noncommand i.e message - echo the message on Telegram

        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("tmp", self.tmp))
        dp.add_handler(MessageHandler(Filters.text, self.handle_message))
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()



        logging.info('start programm')
        print("Bot started")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    def start(self, update, context):
        update.message.reply_text('Start checking ...')
        chat_id = update.message.chat_id
        #self.handlers.pop(chat_id, None)
        markup = buttonsInit()
        context.bot.send_message(chat_id=chat_id, text='Выберите задание:', reply_markup=markup)

    def error(self, update, context, error):
        """Log Errors caused by Updates."""
        print("Update '{}' caused error '{}'".format(update, error),
              file=sys.stderr)

    def tmp(self, update, context):
        chat_id = update.message.chat_id
        bot = context.bot

        sensors = get_temp()
        for sensor in sensors:
            if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Package") != -1:
                bot.send_message(chat_id=chat_id, text='Sensor: ' + str(sensor.Identifier) +
                                                       '\nCore ' + str(sensor.Name) + '\nValue: ' +
                                                       str(sensor.Value) + '\nMax: ' + str(sensor.Max))

    def handle_message(self, update, context):
        chat_id = update.message.chat_id
        text = update.message.text
        bot = context.bot

        if text.find("ping") != -1:
            for substr in text.split():
                if str(substr).find('.'):
                    if ping(str(substr)):
                        bot.send_message(chat_id=chat_id, text='Ping ' + str(substr) + ' ended successful!')
        else:
            bot.send_message(chat_id=chat_id, text="кажется вы где-то ошиблись... попробуйте еще раз")

    def send_scheduled_event(self, update, context):
        logging.info('enter send_scheduled_event func')
        result = check_temp_event()
        print(result)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)

    def runSchedulers(self):
        schedule.every(1).minutes.do(self.send_scheduled_event)
        logging.info('scheduler enter')
        while True:
            schedule.run_pending()
            time.sleep(1)

def check_temp_event():
    outputStr = ''
    sensors = get_temp()
    for sensor in sensors:
        if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Package") != -1:
            if sensor.Value >= 40:
                outputStr = 'Sensor: ' + str(
                    sensor.Identifier) + '\n' + 'ВНИМАНИЕ! ТЕМПЕРАТУРА ПОДНЯЛАСЬ ДО ' + str(
                    sensor.Value) + ' ГРАДУСОВ!!!'
            elif sensor.Value >= 32 and sensor.Value < 40:
                outputStr = 'Sensor: ' + str(
                    sensor.Identifier) + '\n' + 'Температура сервера уже ' + str(sensor.Value) + ' градусов!!!'
            elif sensor.Value >= 60:
                outputStr = 'Sensor: ' + str(sensor.Identifier) + '\n' + str(sensor.Value) + '! ПОМИНКИ.'
            # elif sensor.Value <= 25:
            # outputStr = 'Sensor: ' + str(sensor.Identifier) + '\n' + str(sensor.Value)  +  '. На чииииле. На расслабоооооне!'
    return outputStr

def get_temp():
    pythoncom.CoInitialize()
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    sensors = w.Sensor()
    pythoncom.CoUninitialize()
    return sensors

def ping(host):
    parameter = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', parameter, '1', host]
    response = subprocess.call(command)
    if response == 0:
        return True
    else:
        return False

def buttonsInit():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Температура")
    markup.add(item1)
    return markup


if __name__ == '__main__':
    coretemp_bot = CoreTempBot()
    t1 = threading.Thread(target=coretemp_bot.start) #t1.start()   # starting thread 1
    t2 = threading.Thread(target=coretemp_bot.runSchedulers())  # t2.start()  # starting thread 2