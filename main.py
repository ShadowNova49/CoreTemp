import threading
import telebot
import wmi
import pythoncom
import time
import schedule
from telebot.types import Message
from telebot import types

API_KEY = '5121493952:AAEzxWWOArGWK7uONMj4NC_fkDna-xXcz2g'

bot = telebot.TeleBot(API_KEY)

def get_temp():
    pythoncom.CoInitialize()
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    sensors = w.Sensor()
    pythoncom.CoUninitialize()
    return sensors

def check_temp():
    sensors = get_temp()
    for sensor in sensors:
        if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Package") != -1:
            if sensor.Value >= 40:
                bot.send_message(chat_id, 'Sensor: ' + str(
                    sensor.Identifier) + '\n' + 'ВНИМАНИЕ! ТЕМПЕРАТУРА ПОДНЯЛАСЬ ВЫШЕ 40 ГРАДУСОВ!!!')
            elif sensor.Value >= 32 and sensor.Value < 40:
                bot.send_message(chat_id, 'Sensor: ' + str(
                    sensor.Identifier) + '\n' + 'Температура сервера уже выше 32 градусов!!!')
            elif sensor.Value >= 60:
                bot.send_message(chat_id, 'Sensor: ' + str(sensor.Identifier) + '\n' + '60! ПОМИНКИ.')

def runBot():
    bot.polling()

def runSchedulers():
    schedule.every(5).minutes.do(check_temp)

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=["start"])
def start(message: Message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, "Start checking ...")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Температура")
    markup.add(item1)
    bot.send_message(chat_id, 'Нажми: \nТемпература - для того, чтобы узнать температурные показатели ПК',
                     reply_markup=markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Температура':
        sensors = get_temp()
        for sensor in sensors:
            if sensor.SensorType == u'Temperature' and str(sensor.Name).find("CPU Package") != -1:
                bot.send_message(chat_id, 'Sensor: ' + str(sensor.Identifier) +
                                 '\nCore ' + str(sensor.Name) + '\nValue: ' +
                                 str(sensor.Value) + '\nMax: ' + str(sensor.Max))

if __name__ == '__main__':
    t1 = threading.Thread(target=runBot)
    t2 = threading.Thread(target=runSchedulers)
    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()
