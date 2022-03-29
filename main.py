import telebot
import wmi
import pythoncom
import threading
import time
import schedule
import logging
import platform
import subprocess
import os
import sys
from telebot.types import Message
from telebot import types

with open(os.path.dirname(os.path.realpath(__file__)) + '/API_token.txt') as file:
    TOKEN = file.readline().strip()

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

def get_temp():
    pythoncom.CoInitialize()
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    sensors = w.Sensor()
    pythoncom.CoUninitialize()
    return sensors

def check_temp():
    sensors = get_temp()
    for sensor in sensors:
        if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Core #1") != -1 and str(sensor.Name).find(
                "CPU Core #10") == -1:
            outputStr = ''
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
            with open('chat_id.txt', 'r', encoding='UTF-8') as f:
                for id in f:
                    bot.send_message(id, outputStr)

def runBot():
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            logging.error('error: {}'.format(sys.exc_info()[0]))
            time.sleep(5)

def runSchedulers():
    schedule.every(10).minutes.do(check_temp)

    while True:
        schedule.run_pending()
        time.sleep(1)

def checkUser(chat_id: str):
    check = bool(False)
    with open('chat_id.txt', 'r', encoding='UTF-8') as f:
        for id in f:
            if int(id) == int(chat_id):
                check = bool(True)
                break
    with open('chat_id.txt', 'a', encoding='UTF-8') as f:
        if check == False:
            chat_id = chat_id + '\n'
            f.write(chat_id)

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
    item1 = types.KeyboardButton("Температура Server-10")
    item2 = types.KeyboardButton("Ping Server-77 File")
    item3 = types.KeyboardButton("Ping Server-1 Buh")
    item4 = types.KeyboardButton("Ping Server-2 Adonis")
    item5 = types.KeyboardButton("Ping Server-3 Old DNS")
    item6 = types.KeyboardButton("Ping Server-7 Clinic")
    item7 = types.KeyboardButton("Ping ter-admin1")
    item8 = types.KeyboardButton("Ping Server-10 DNS")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    markup.add(item5)
    markup.add(item6)
    markup.add(item7)
    markup.add(item8)
    return markup

@bot.message_handler(commands=["start"])
def start(message: Message):
    checkUser(str(message.chat.id))
    bot.reply_to(message, "Start checking ...")
    markup = buttonsInit()
    bot.send_message(message.chat.id, 'Выберите задание:',
                     reply_markup=markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Температура Server-10':
        sensors = get_temp()
        for sensor in sensors:
            if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Core #1") != -1 and str(
                    sensor.Name).find("CPU Core #10") == -1:
                bot.send_message(message.chat.id, 'Sensor: ' + str(sensor.Identifier) +
                                 '\nCore ' + str(sensor.Name) + '\nValue: ' +
                                 str(sensor.Value) + '\nMax: ' + str(sensor.Max))

    elif message.text.strip() == 'Ping Server-77 File':
        if ping('192.168.55.77'):
            bot.send_message(message.chat.id, 'Ping Server-77 File ended successful!')

    elif message.text.strip() == 'Ping Server-1 Buh':
        if ping('192.168.55.1'):
            bot.send_message(message.chat.id, 'Ping Server-1 Buh ended successful!')

    elif message.text.strip() == 'Ping Server-2 Adonis':
        if ping('192.168.55.2'):
            bot.send_message(message.chat.id, 'Ping Server-2 Adonis ended successful!')

    elif message.text.strip() == 'Ping Server-3 Old DNS':
        if ping('192.168.55.3'):
            bot.send_message(message.chat.id, 'Ping Server-3 Old DNS ended successful!')

    elif message.text.strip() == 'Ping Server-7 Clinic':
        if ping('192.168.55.7'):
            bot.send_message(message.chat.id, 'Ping Server-7 Clinic ended successful!')

    elif message.text.strip() == 'Ping ter-admin1':
        if ping('192.168.55.135'):
            bot.send_message(message.chat.id, 'Ping ter-admin1 ended successful!')

    elif message.text.strip() == 'Ping Server-10 DNS':
        if ping('192.168.54.200'):
            bot.send_message(message.chat.id, 'Ping Server-10 DNS ended successful!')

if __name__ == '__main__':
    t1 = threading.Thread(target=runBot)
    t2 = threading.Thread(target=runSchedulers)
    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()
