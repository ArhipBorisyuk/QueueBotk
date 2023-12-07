import telebot
from datetime import datetime, timedelta
import time

bot = telebot.TeleBot('6897293870:AAGAYs7VEpDJXmhRG1lpfEPtzff-u4kldw8')

chat_id = '-1001610315602'  # Замените на ID вашей беседы

queue = list()
startTime = None
isRun = False
inProcess = False
gameTime = 120  # время в секундах

# Белый список пользователей, которым разрешено использовать команду !начать
whitelist_start = [5126551821, 921537356, 391589436]  # Замените на реальные идентификаторы пользователей

@bot.message_handler(func=lambda message: True)
def get_text_messages(message):
    global startTime, isRun, inProcess

    command = message.text.split()


    if isRun and datetime.now() >= startTime + timedelta(seconds=gameTime):
        # Выполнять действия, если прошло достаточно времени после начала игры
        isRun = False
        startTime = None
        bot.send_message(message.chat.id, "Игра закончена!")

    if command[0] == "!начать":
        # Проверяем, входит ли пользователь в белый список перед выполнением команды !начать
        if message.from_user.id not in whitelist_start:
            bot.send_message(message.chat.id, "У вас нет прав на использование этой команды.")
            return

        if len(command) < 2:
            bot.send_message(message.chat.id, "Не указана дата и время начала игры.")
            return

        hour_and_minute = command[1].split(":")

        if len(hour_and_minute) != 2:
            bot.send_message(message.chat.id, "Неверный формат времени. Используйте HH:MM.")
            return

        hour = int(hour_and_minute[0])
        minute = int(hour_and_minute[1])

        # Проверяем, не прошло ли указанное время
        new_start_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if new_start_time <= datetime.now():
            bot.send_message(message.chat.id, "Указанное время уже прошло.")
            return

        # Проверяем, активна ли уже игра
        if isRun:
            # Отменяем текущую игру
            bot.send_message(message.chat.id, "Текущая игра отменена.")
            isRun = False
            startTime = new_start_time
            inProcess = None
        else:
            # Устанавливаем startTime как объект datetime
            isRun = True
            startTime = new_start_time

            bot.send_message(message.chat.id, f"Принято!")

            while datetime.now() < startTime:
                if not isRun:
                    return
                time.sleep(1)

            bot.send_message(message.chat.id, f"Игра началась! У вас есть 2 минуты МУХАХАХАХАХ")

            inProcess = True

            # Блокируем выполнение кода на время gameTime
            time.sleep(gameTime)

            users_list = idToUsername(queue, message)
            bot.send_message(message.chat.id, f"Список участников:\n{users_list}")

            clear_queue()
            inProcess = False

    elif command[0] == "!крайний" and inProcess:
        user_id = message.from_user.id

        if user_id not in queue:
            queue.append(user_id)

    elif command[0] == "!крайний" and not inProcess:
        bot.send_message(message.chat.id, f"Рано !")

def idToUsername(user_ids, message):
    users_list = []
    for index, user_id in enumerate(user_ids, start=1):
        user = bot.get_chat_member(message.chat.id, user_id).user
        if user.username:
            users_list.append(f"{index}. @{user.username}")
        else:
            users_list.append(f"{index}. {user.first_name}")

    return "\n".join(users_list)

def clear_queue():
    global startTime, isRun
    startTime = None
    isRun = False
    queue.clear()

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
