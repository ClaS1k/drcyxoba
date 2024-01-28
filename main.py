import json
import telebot
import time
import mysql
import re

import config

from mysql import connector
from telebot import types
from sql import *
from re import search
from datetime import datetime

from flask import Flask, request

TELEGRAM_TOKEN = "6405760533:AAETDpDK03yCjjcC7Z7Kw9zoeqRrJeBro2g"

# создаём приложение Flask
application = Flask(__name__)
flask_started = False

# Создаем экземпляр бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    user_data = m.from_user
    user_id = m.chat.id

    sql = "SELECT * FROM `users` WHERE `id`='"+str(user_id)+"'"
    result = sql_query(sql)

    if(len(result) == 0):
        sql = "INSERT INTO `users`(`id`, `phone`, `name`, `surname`, `lastname`, `status`, `role`, `ClinicIQ_id`) VALUES ('" + str(user_id) + "','Not_selected','Not_selected','Not_selected','Not_selected','await_phone', 'user', '0')"
        sql_query(sql)

        data = {
            "action":"sign_up"
        }

        markup = types.InlineKeyboardMarkup()

        btn = types.InlineKeyboardButton("Создать профиль", callback_data=json.dumps(data))
        markup.add(btn)

        bot.send_message(m.chat.id, "Для начала приважем ваш телеграм к профилю. Укажите номер, который вы использовали в клинике.", reply_markup = markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Мои записи 📆")
        btn2 = types.KeyboardButton("Как доехать 🗺️")
        btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
        btn4 = types.KeyboardButton("Записаться на приём ⌚️")

        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(m.chat.id, "Вы уже зарегестрированы! Добро пожаловать назад!", reply_markup = markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_data = message.from_user
    user_id = user_data.id

    sql = "SELECT * FROM `users` WHERE `id`='"+str(user_id)+"'"
    result = sql_query(sql)

    status = result[0][5]
    role = result[0][6]

    if(role == "admin"):
        if message.text == "Главное меню ⬅️":
            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='" + str(message.chat.id) + "'"
            sql_query(sql)

            sql = "UPDATE `config` SET `value`='none' WHERE `param`='await_import'"
            sql_query(sql)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Заявки 📑")
            btn2 = types.KeyboardButton("Рассылка ✉️")
            btn3 = types.KeyboardButton("Импорт данных 💽")

            markup.add(btn1, btn2, btn3)

            bot.send_message(message.chat.id, "Чем займёмся?",  reply_markup=markup)
            
            return

        if message.text == "Импорт данных 💽":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Пациенты 🙎‍♂️")
            btn2 = types.KeyboardButton("Визиты 🎟")
            btn3 = types.KeyboardButton("Сотрудники 🧑‍⚕️")
            btn4 = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn1, btn2, btn3, btn4)

            bot.send_message(message.chat.id, "Что импортируем?",  reply_markup=markup)

            return

        if message.text == "Пациенты 🙎‍♂️":
            sql = "UPDATE `config` SET `value`='users' WHERE `param`='await_import'"
            
            result = sql_query(sql)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            btn = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn)

            bot.send_message(message.chat.id, "Пришлите json файл",  reply_markup=markup)

            return

        if message.text == "Визиты 🎟":
            sql = "UPDATE `config` SET `value`='appointments' WHERE `param`='await_import'"
            
            result = sql_query(sql)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            btn = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn)

            bot.send_message(message.chat.id, "Пришлите json файл",  reply_markup=markup)

            return

        if message.text == "Сотрудники 🧑‍⚕️":
            sql = "UPDATE `config` SET `value`='employes' WHERE `param`='await_import'"
            
            result = sql_query(sql)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            btn = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn)

            bot.send_message(message.chat.id, "Пришлите json файл",  reply_markup=markup)

            return

        if message.text == "Рассылка ✉️":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Шаблоны 🛠️")
            btn2 = types.KeyboardButton("Сборка 🧩")
            btn3 = types.KeyboardButton("Старт 📮")
            btn4 = types.KeyboardButton("Визиты 📆")
            btn5 = types.KeyboardButton("Помощь 🗿")
            btn6 = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

            bot.send_message(message.chat.id, "Выберите действие",  reply_markup=markup)

            return
        
        if message.text == "Визиты 📆":
            data = {
                "action":"approve_visits_sendler"
            }

            markup = types.InlineKeyboardMarkup()

            btn = types.InlineKeyboardButton("Подтвердить", callback_data=json.dumps(data))
            markup.add(btn)

            bot.send_message(message.chat.id, "Подтвердите старт рассылки напоминаний о визитах.", reply_markup=markup)
            return
        
        if message.text == "Старт 📮":
            #продолжить тут
            sql = "SELECT * FROM `config` WHERE `param`='pattern'"
            result = sql_query(sql)

            sql = "SELECT * FROM `sendler` WHERE `id`='" + str(result[0][1]) + "'"
            result = sql_query(sql)

            pattern_text = result[0][1]

            reg_exp = "[%][a-zA-Z]*[%]"

            variables_list = re.findall(reg_exp, pattern_text)

            sql = "SELECT * FROM `postman`"
            result = sql_query(sql)

            bot.send_message(message.chat.id, "Рассылка запущена")

            i = 0

            for row in result:
                getter_id = row[0]
                data = json.loads(row[1])

                sql = "SELECT * FROM `users` WHERE `id`='" + str(getter_id) + "'"
                res = sql_query(sql)

                user_data = res[0]

                unique_string = pattern_text

                unique_string = re.sub("%username%", user_data[2], unique_string)
                unique_string = re.sub("%usersurname%", user_data[3], unique_string)
                unique_string = re.sub("%userpatronymic%", user_data[4], unique_string)

                for item in data["variables"]:
                    unique_string = re.sub(item["key"], item["value"], unique_string)

                bot.send_message(getter_id, unique_string)
            
                i += 1
            
            bot.send_message(message.chat.id, "Рассылка завершена. " + str(i) + " получателей.")

            return

        if message.text == "Сборка 🧩":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Добавить клиента 🙎🏼‍♂️")
            btn2 = types.KeyboardButton("Список получателей 👨‍👦‍👦")
            btn3 = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn1, btn2, btn3)

            bot.send_message(message.chat.id, "Выберите действие",  reply_markup=markup)

            return
        
        if message.text == "Список получателей 👨‍👦‍👦":
            sql = "SELECT * FROM `postman`"
            result = sql_query(sql)

            response = "Список получателей: \n\n"

            for row in result:
                getter_id = row[0]

                sql = "SELECT * FROM `users` WHERE `id`='" + str(getter_id) + "'"
                user_data = sql_query(sql)

                response = response + user_data[0][2] + " " + user_data[0][3] + " (" + user_data[0][1] + ") \n"

            bot.send_message(message.chat.id, response)

            return

        if message.text == "Добавить клиента 🙎🏼‍♂️":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn3 = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn3)

            sql = "UPDATE `users` SET `status`='find_postman_users' WHERE `id`='" + str(message.chat.id) + "'"

            sql_query(sql)

            bot.send_message(message.chat.id, "Укажите последние 4 цифры номера телефона",  reply_markup=markup)

            return

        if message.text == "Шаблоны 🛠️":
            sql = "SELECT * FROM `sendler`"
            result = sql_query(sql)

            data = {
                "action":"create_sendler_pattern"
            }

            markup = types.InlineKeyboardMarkup()

            btn = types.InlineKeyboardButton("Создать шаблон", callback_data=json.dumps(data))
            markup.add(btn)

            for row in result:
                data = {
                    "action":"get_sendler_pattern",
                    "pattern_id":row[0]
                }

                btn = types.InlineKeyboardButton("Шаблон " + str(row[0]), callback_data=json.dumps(data))
                markup.add(btn)
            
            bot.send_message(message.chat.id, "Выберите шаблон, который хотите посмотреть или создайте новый.", reply_markup=markup)

            return

        if message.text == "Помощь 🗿":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Шаблоны 🛠️")
            btn2 = types.KeyboardButton("Сборка 🧩")
            btn3 = types.KeyboardButton("Старт 📮")
            btn4 = types.KeyboardButton("Визиты 📆")
            btn5 = types.KeyboardButton("Помощь 🗿")
            btn6 = types.KeyboardButton("Главное меню ⬅️")

            markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

            bot.send_message(message.chat.id, config.POSTMAN_HELP_TEXT, reply_markup=markup)
            
            return
        
        if message.text == "Заявки 📑":
            sql = "SELECT * FROM `reports` WHERE `status`='await'"
            result = sql_query(sql)

            if(len(result) == 0):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

                btn1 = types.KeyboardButton("Заявки 📑")
                btn2 = types.KeyboardButton("Рассылка ✉️")
                btn3 = types.KeyboardButton("Импорт данных 💽")

                markup.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, "Заявок в данный момент нет.",  reply_markup=markup)
            else:
                text = ""
                markup = types.InlineKeyboardMarkup()

                for row in result:
                    sql = "SELECT * FROM `users` WHERE `id`='" + str(row[1]) + "'"
                    user_data = sql_query(sql)

                    text = text + "Заявка " + str(row[0]) + " от " + str(user_data[0][2]) + " (" + str(user_data[0][1]) + ") \n\n"

                    data = {
                        "action":"reply_to_client",
                        "report_id":row[0]
                    }

                    btn = types.InlineKeyboardButton("Заявка " + str(row[0]), callback_data=json.dumps(data))
                    markup.add(btn)

                bot.send_message(message.chat.id, text, reply_markup=markup)

            return

        if message.text == "Закончить чат":
            sql = "SELECT * FROM `reports` WHERE `admin_id`='" + str(user_id) + "' AND `status`='working'"
            result = sql_query(sql)

            admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Заявки 📑")
            btn2 = types.KeyboardButton("Рассылка ✉️")
            btn3 = types.KeyboardButton("Импорт данных 💽")

            admin_markup.add(btn1, btn2, btn3)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Мои записи 📆")
            btn2 = types.KeyboardButton("Как доехать 🗺️")
            btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
            btn4 = types.KeyboardButton("Записаться на приём ⌚️")

            markup.add(btn1, btn2, btn3, btn4)

            bot.send_message(message.chat.id, "Вы закончили чат", reply_markup=admin_markup)
            bot.send_message(result[0][1], "Чат закончен администратором.", reply_markup=markup)

            sql = "UPDATE `reports` SET `status`='closed' WHERE `id`='" + str(result[0][0]) + "'"
            sql_query(sql)

            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='"+ str(result[0][1]) +"'"
            sql_query(sql)

            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='"+ str(result[0][2]) +"'"
            sql_query(sql)

            return
            
        if status == "in_admin_chat":
            text = message.text

            sql = "SELECT * FROM `reports` WHERE `admin_id`='"+str(user_id)+"' AND `status`='working'"
            result = sql_query(sql)

            reporter_id = result[0][1]

            sql = "SELECT * FROM `users` WHERE `id`='"+str(reporter_id)+"'"
            result = sql_query(sql)

            reporter_chat_id = result[0][0]
            bot.send_message(reporter_chat_id, text)

            return
        
        if status == "await_postman_pattern":
            text = message.text

            sql = "INSERT INTO `sendler`(`text`) VALUES ('" + str(text) + "')"
            result = sql_query(sql)
            
            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='" + str(message.chat.id) + "'"

            sql_query(sql)

            bot.send_message(message.chat.id, "Шаблон успешно добавлен!")
            
            return

        if status == "find_postman_users":
            text = message.text

            sql = "SELECT * FROM `users` WHERE LOCATE('" + str(text) + "', `phone`)"
            
            result = sql_query(sql)

            if(len(result)==0):
                bot.send_message(message.chat.id, "Пользователи не найдены!")
                return
            
            markup = types.InlineKeyboardMarkup()

            for row in result:
                data = {
                    "action":"add_client",
                    "client_id":row[0]
                }
                
                btn = types.InlineKeyboardButton(str(row[3]) + " " + str(row[2]), callback_data=json.dumps(data))
                markup.add(btn)

            bot.send_message(message.chat.id, "Выберите клиента", reply_markup=markup)

            return

        if status == "adding_client_to_build":
            text = message.text

            sql = "SELECT * FROM `config` WHERE `param`='pattern'"
            result = sql_query(sql)

            pattern_id = result[0][1]

            sql = "SELECT * FROM `sendler` WHERE `id`='"+ str(pattern_id) +"'"
            result = sql_query(sql)

            pattern_text = result[0][1]

            reg_exp = "[%][a-zA-Z]*[%]"

            variables_list = re.findall(reg_exp, pattern_text)

            sql = "SELECT * FROM `postman` WHERE `status`='building'"

            result = sql_query(sql)
            
            postman_id = 0
            data = []

            for row in result:
                data = json.loads(row[1])

                if data["author"] == message.chat.id:
                    postman_id = row[0]
                    break

            for match in variables_list:
                if (match == "%username%" or match == "%usersurname%" or match == "%userpatronymic%"):
                    continue
                
                is_created = False

                for idx, value in enumerate(data["variables"]):
                     if value["key"] == match and value["value"] == "not_setted":
                        data["variables"][idx]["value"] = text
                        is_created = True
                        break

                if is_created:
                    sql = "UPDATE `postman` SET `chat_variables`='"+ json.dumps(data, ensure_ascii=False) +"' WHERE `user_id`='" + str(postman_id) + "'"
                    sql_query(sql)

                    is_all_ready = True
                    await_key = ""

                    for item in data["variables"]:
                        if item["value"] == "not_setted":
                            await_key = item["key"]
                            is_all_ready = False
                            break

                    if is_all_ready:
                        sql = "UPDATE `postman` SET `status`='ready' WHERE `user_id`='" + str(postman_id) + "'"
                        sql_query(sql)

                        sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='" + str(message.chat.id) + "'"
                        sql_query(sql)

                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton("Шаблоны 🛠️")
                        btn2 = types.KeyboardButton("Сборка 🧩")
                        btn3 = types.KeyboardButton("Старт 📮")
                        btn4 = types.KeyboardButton("Помощь 🗿")
                        btn5 = types.KeyboardButton("Главное меню ⬅️")

                        markup.add(btn1, btn2, btn3, btn4, btn5)

                        bot.send_message(message.chat.id, "Клиент успешно добавлен в сборку!",  reply_markup=markup)

                        return
                    else:
                        bot.send_message(message.chat.id, "Укажите значение для " + await_key)

                        return

                    break       
        
        sql = "UPDATE `config` SET `value`='none' WHERE `param`='await_import'"
        sql_query(sql)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Заявки 📑")
        btn2 = types.KeyboardButton("Рассылка ✉️")
        btn3 = types.KeyboardButton("Импорт данных 💽")

        markup.add(btn1, btn2, btn3)

        bot.send_message(message.chat.id, "Чем займёмся?",  reply_markup=markup)

        return

    if status == "in_chat":
        if message.text == "Закончить чат":
            sql = "SELECT * FROM `reports` WHERE `user_id`='" + str(user_id) + "' AND `status`='working'"
            result = sql_query(sql)

            admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Заявки 📑")
            btn2 = types.KeyboardButton("Рассылка ✉️")
            btn3 = types.KeyboardButton("Импорт данных 💽")

            admin_markup.add(btn1, btn2, btn3)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Мои записи 📆")
            btn2 = types.KeyboardButton("Как доехать 🗺️")
            btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
            btn4 = types.KeyboardButton("Записаться на приём ⌚️")

            markup.add(btn1, btn2, btn3, btn4)

            bot.send_message(message.chat.id, "Вы закончили чат", reply_markup=markup)
            bot.send_message(result[0][2], "Чат закончен клиентом.", reply_markup=admin_markup)

            sql = "UPDATE `reports` SET `status`='closed' WHERE `id`='" + str(result[0][0]) + "'"
            sql_query(sql)

            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='"+ str(result[0][1]) +"'"
            sql_query(sql)

            sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='"+ str(result[0][2]) +"'"
            sql_query(sql)

            return

        text = message.text

        sql = "SELECT * FROM `reports` WHERE `user_id`='"+str(user_id)+"' AND `status`='working'"
        result = sql_query(sql)

        admin_id = result[0][2]

        sql = "SELECT * FROM `users` WHERE `id`='"+str(admin_id)+"'"
        result = sql_query(sql)

        admin_chat_id = result[0][0]
        bot.send_message(admin_chat_id, text)

    if status == "await_phone":
        phone = message.text

        pattern = "^(\+7|8)[\- ]?\(?\d{3}\)?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}$"

        if re.match(pattern, phone):
            query = phone[-7:]
            
            sql = "SELECT * FROM `ClinicIQ_users` WHERE LOCATE('" + query + "', `phone`)"
            result = sql_query(sql)

            if(len(result) == 0):
                bot.send_message(message.chat.id, "Номер не найден. укажите другой номер.")
                return

            markup = types.InlineKeyboardMarkup()

            for row in result:
                data = {
                    "action":"select_profile",
                    "clinic_id":row[0]
                }
                
                btn = types.InlineKeyboardButton(str(row[2]) + " " + str(row[3]), callback_data=json.dumps(data))
                markup.add(btn)

            bot.send_message(message.chat.id, "Подтвердите имя.", reply_markup=markup)

            return
        else:
            bot.send_message(message.chat.id, "Не корректный номер! Попробуйте ещё раз.")

    if status == "await_name":
        name = message.text

        sql = "UPDATE `signup_tickets` SET `name`='" + name + "' WHERE `user_id`='" + str(user_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='await_birthdate' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Укажите дату рождения")

    if status == "await_birthdate":
        birth_date = message.text

        sql = "UPDATE `signup_tickets` SET `birth_date`='" + birth_date + "' WHERE `user_id`='" + str(user_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='await_phone_signup' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Укажите номер телефона")

    if status == "await_phone_signup":
        phone = message.text

        pattern = "^(\+7|8)[\- ]?\(?\d{3}\)?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}$"

        if re.match(pattern, phone):
            sql = "UPDATE `signup_tickets` SET `phone`='" + phone + "' WHERE `user_id`='" + str(user_id) + "'"
            sql_query(sql)

            sql = "UPDATE `users` SET `status`='await_service' WHERE `id`='" + str(message.chat.id) + "'"
            sql_query(sql)

            bot.send_message(message.chat.id, "Какую услугу вы хотели-бы получить?")

            return
        else:
            bot.send_message(message.chat.id, "Не корректный номер! Попробуйте ещё раз.")

    if status == "await_service":
        service = message.text

        sql = "UPDATE `signup_tickets` SET `service`='" + service + "' WHERE `user_id`='" + str(user_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='await_promo' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Откуда вы о нас узнали?")

    if status == "await_promo":
        promo = message.text

        sql = "UPDATE `signup_tickets` SET `promo`='" + promo + "', `status`='1' WHERE `user_id`='" + str(user_id) + "'"
        sql_query(sql)

        sql = "SELECT * FROM `signup_tickets` WHERE `user_id`='" + str(user_id) + "'"
        result = sql_query(sql)

        signup_ticket = result[0]

        admin_notification = "Поступила заявка на регистрацию. \n\n"
        admin_notification += "Телеграм: " + ("@" + signup_ticket[3], "username отсутствует")[signup_ticket[3] == "not_setted"] + " \n"
        admin_notification += "ФИО: " + signup_ticket[2] + " \n"
        admin_notification += "Дата рождения: " + signup_ticket[4] + " \n"
        admin_notification += "Телефон: " + signup_ticket[5] + " \n"
        admin_notification += "Услуга: " + signup_ticket[6] + " \n"
        admin_notification += "Откуда узнал(-а): " + signup_ticket[7] + " \n"

        sql = "UPDATE `users` SET `status`='await_phone' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Заявка на регистрацию создана! Ожидайте сообщение от @IDDrCyxoBa")

        sql = "SELECT * FROM `users` WHERE `role`='admin'"
        result = sql_query(sql)

        for row in result:
            chat_id = row[0]
            bot.send_message(chat_id, admin_notification)

    if status == "await_request_service":
        service = message.text

        sql = "SELECT * FROM `users` WHERE `id`='" + str(user_id) + "'"
        result = sql_query(sql)

        request_user = result[0]

        request_username = ("@" + user_data.username, "username не установлен")[user_data.username == None]

        request_text = "Поступил новый запрос на запись ко врачу. \n\n"
        request_text += "Имя: " + request_user[2] + " " + request_user[3] + " \n"
        request_text += "Телеграм: " + request_username + " \n"
        request_text += "Телефон: " + request_user[1] + " \n"
        request_text += "Услуга: " + service

        sql = "SELECT * FROM `users` WHERE `role`='admin'"
        result = sql_query(sql)

        for row in result:
            chat_id = row[0]
            bot.send_message(chat_id, request_text)

        sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Заявка отправлена администратору! Ожидайте сообщение от @IDDrCyxoBa")

    if message.text == "Как доехать 🗺️":
        bot.send_location(message.chat.id, "55.800099", "37.535709")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Мои записи 📆")
        btn2 = types.KeyboardButton("Как доехать 🗺️")
        btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
        btn4 = types.KeyboardButton("Записаться на приём ⌚️")

        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(message.chat.id, config.ADDRESS_TEXT, reply_markup=markup)

    if message.text == "Мои записи 📆":
        sql = "SELECT * FROM `users` WHERE `id`='" + str(user_id) + "'"
        result = sql_query(sql)

        clinic_id = result[0][7]

        sql = "SELECT * FROM `ClinicIQ_appointments` WHERE `date`>NOW() - INTERVAL 24 HOUR AND `clinic_user_id`='" + str(clinic_id) + "' ORDER BY `date` ASC"
        result = sql_query(sql)

        if(len(result) == 0):
            bot.send_message(message.chat.id, "Нет предстоящих записей")
            return

        response = "Ваши предстоящие визиты: \n\n"

        for row in result:
            employe_id = row[2]
            meet_date = str(row[3])
            time_start = str(row[4])
            time_end = str(row[5])

            time_start = time_start.split(":")
            time_start = time_start[0] + ":" + time_start[1]

            time_end = time_end.split(":")
            time_end = time_end[0] + ":" + time_end[1]

            sql = "SELECT * FROM `ClinicIQ_employes` WHERE `id`='" + str(employe_id) + "'"
            result = sql_query(sql)

            employe_short_name = result[0][2]
            
            response = response + meet_date + " " + time_start + "-" + time_end + " \nВрач: " + employe_short_name

        bot.send_message(message.chat.id, response)
        return

    if message.text == "Связаться с админом 👨‍💻":
        now = datetime.now()
        current_time = int(now.strftime("%H"))

        if(current_time < 9 or current_time > 23):
            bot.send_message(message.chat.id, config.NOT_WORKING_HOURS_TEXT)
            return

        sql = "SELECT * FROM `reports` WHERE `user_id`='"+ str(user_id) +"' AND `status`='await'";
        result = sql_query(sql)

        if(len(result) > 0):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Мои записи 📆")
            btn2 = types.KeyboardButton("Как доехать 🗺️")
            btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")

            markup.add(btn1, btn2, btn3)

            bot.send_message(message.chat.id, "Ожидание администратора...", reply_markup=markup)
            
            return

        sql = "INSERT INTO `reports`(`user_id`, `admin_id`, `status`) VALUES ('" + str(user_id) + "','0','await')";
        sql_query(sql)

        sql = "SELECT * FROM `users` WHERE `id`='" + str(user_id) + "'"
        result = sql_query(sql)

        request_user = result[0]

        request_username = ("@" + user_data.username, "username не установлен")[user_data.username == None]

        request_text = "Поступил новый запрос на обратную связь. \n\n"
        request_text += "Имя: " + request_user[2] + " " + request_user[3] + " \n"
        request_text += "Телеграм: " + request_username + " \n"
        request_text += "Телефон: " + request_user[1]

        sql = "SELECT * FROM `users` WHERE `role`='admin'"
        result = sql_query(sql)

        for row in result:
            chat_id = row[0]
            bot.send_message(chat_id, request_text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Мои записи 📆")
        btn2 = types.KeyboardButton("Как доехать 🗺️")
        btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
        btn4 = types.KeyboardButton("Записаться на приём ⌚️")

        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(message.chat.id, "Заявка создана! Ожидайте администратора.", reply_markup=markup)

    if message.text == "Записаться на приём ⌚️":
        sql = "UPDATE `users` SET `status`='await_request_service' WHERE `id`='" + str(message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(message.chat.id, "Какую услугу вы хотите получить?")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    sql = "SELECT * FROM `config` WHERE `param`='await_import'"
    result = sql_query(sql)

    await_import_type = result[0][1]

    if(await_import_type == "none"):
        bot.send_message(message.chat.id, "Импорт файла не ожидается.")
        return

    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = './upload/' + message.document.file_name;
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        with open(src, encoding="utf-8-sig") as json_file:
            data = json.load(json_file)

            bot.send_message(message.chat.id, "Файл обрабатывается. Подождите.")

            match await_import_type:
                case "users":
                    is_first = True

                    for item in data:
                        if is_first:
                            if item[2] != "ПЕРВЫЙ ВИЗИТ":
                                bot.send_message(message.chat.id, "Неправильный файл")
                                return

                            sql = "TRUNCATE `ClinicIQ_users`";
                            sql_query(sql)

                            is_first = False
                        else:
                            if(len(item) != 25):
                                continue
                            sql = "INSERT INTO `ClinicIQ_users`(`id`, `card_number`, `name`, `surname`, `lastname`, `male`, `phone`) VALUES ('" + str(item[0]) + "','" + str(item[1]) + "','" + str(item[4]) + "','" + str(item[3]) + "','" + str(item[5]) + "','" + str((0, 1)[item[6] == "М"]) + "','" + str(item[8]) + "')"
                            sql_query(sql)

                case "appointments":
                    is_first = True
            
                    for item in data:
                        if is_first:
                            if item[2] != "ID ВИЗИТА":
                                bot.send_message(message.chat.id, "Неправильный файл")
                                return

                            sql = "TRUNCATE `ClinicIQ_appointments`";
                            sql_query(sql)

                            is_first = False
                        else:
                            if(len(item) != 9):
                                continue

                            date = item[4].split(".")

                            date = date[2] + "-" + date[1] + "-" + date[0]

                            sql = "INSERT INTO `ClinicIQ_appointments`(`id`, `clinic_user_id`, `employe_id`, `date`, `time_start`, `time_end`, `reason`, `comment`) VALUES ('" + str(item[2]) + "','" + str(item[0]) + "','" + str(item[3]) + "','" + date + "','" + str(item[5]) + "','" + str(item[6]) + "','" + str(item[7]) + "','" + str(item[8]) + "')"
                            sql_query(sql)

                case "employes":
                    is_first = True

                    for item in data:
                        if is_first:
                            if item[0] != "ID СОТРУДНИКА":
                                bot.send_message(message.chat.id, "Неправильный файл")
                                return
                            
                            sql = "TRUNCATE `ClinicIQ_employes`";
                            sql_query(sql)

                            is_first = False
                        else:
                            sql = "INSERT INTO `ClinicIQ_employes`(`id`, `full_name`, `short_name`) VALUES ('" + str(item[0]) + "','" + item[2] + " " + item[1] + " " + item[3] + "','" + item[9] + "')"
                            sql_query(sql)

            sql = "UPDATE `config` SET `value`='users' WHERE `param`='await_import'"
            result = sql_query(sql)

            bot.send_message(message.chat.id, "Импорт данных завершен")
            return

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, e)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = json.loads(call.data)

    if(data['action'] == "sign_up"):
        sql = "SELECT * FROM `signup_tickets` WHERE `user_id`='" + str(call.message.chat.id) + "'"
        result = sql_query(sql)

        if(len(result) != 0):
            sql = "DELETE FROM `signup_tickets` WHERE `user_id`='" + str(call.message.chat.id) + "'"
            sql_query(sql)

        chat_data = bot.get_chat(call.message.chat.id)

        username = (chat_data.username, "not_setted")[chat_data.username == None]

        sql = "INSERT INTO `signup_tickets`(`user_id`, `name`, `username`, `birth_date`, `phone`, `service`, `promo`, `status`) VALUES ('" + str(call.message.chat.id) + "','-','" + username + "','-','-','-','-','0')"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='await_name' WHERE `id`='" + str(call.message.chat.id) + "'"
        sql_query(sql)

        bot.send_message(call.message.chat.id, "Укажите ваше ФИО")

    if(data['action'] == "approve_visits_sendler"):
        sql = "SELECT * FROM `ClinicIQ_appointments` WHERE `date`=CURDATE() + INTERVAL 24 HOUR"
        result = sql_query(sql)

        if(len(result) == 0):
            bot.send_message(call.message.chat.id, "На сегодня нет записей.")
            return
        
        bot.send_message(call.message.chat.id, "Обработка " + str(len(result)) + " записей на завтра. Ожидайте.")

        count = 0

        for row in result:
            clinic_user_id = row[1]

            sql = "SELECT * FROM `users` WHERE `ClinicIQ_id`='" + str(clinic_user_id) + "'"
            res = sql_query(sql)

            if(len(res) == 0):
                continue

            appointment_id = row[0]
            getter_id = res[0][0]
            employe_id = row[2]
            time_start = str(row[4])
            time_end = str(row[5])

            time_start = time_start.split(":")
            time_start = time_start[0] + ":" + time_start[1]

            time_end = time_end.split(":")
            time_end = time_end[0] + ":" + time_end[1]

            sql = "SELECT * FROM `ClinicIQ_employes` WHERE `id`='" + str(employe_id) + "'"
            res_emp = sql_query(sql)

            employe_short_name = res_emp[0][2]

            data = {
                "action":"decline_appointment",
                "appointment_id": appointment_id
            }

            markup = types.InlineKeyboardMarkup()

            btn = types.InlineKeyboardButton("Отменить запись", callback_data=json.dumps(data))
            markup.add(btn)

            message = "У вас завтра запись на посещение с " + time_start + " до " + time_end + ". \n\nВрач: " + employe_short_name
            bot.send_message(getter_id, message, reply_markup = markup)
            count += 1
        
        bot.send_message(call.message.chat.id, "Всего обработано " + str(len(result)) + " записей. Отправлено " + str(count) + " напоминаний.")

    if(data['action'] == "decline_appointment"):
        appointment_id = data['appointment_id']

        sql = "SELECT * FROM `ClinicIQ_appointments` WHERE `id`='" + str(appointment_id) + "'"
        result = sql_query(sql)

        appointment_data = result[0]
        
        sql = "SELECT * FROM `users` WHERE `ClinicIQ_id`='" + str(appointment_data[1]) + "'"
        result = sql_query(sql)

        appointment_user = result[0]

        sql = "SELECT * FROM `ClinicIQ_employes` WHERE `id`='" + str(appointment_data[2]) + "'"
        result = sql_query(sql)

        appointment_employe = result[0]

        admin_message = appointment_user[2] + " " + appointment_user[3] + " (" + appointment_user[1] + ") отменил запись на " + str(appointment_data[3]) + " " + str(appointment_data[4]) + " к " + str(appointment_employe[2])

        sql = "SELECT * FROM `users` WHERE `role`='admin'"
        result = sql_query(sql)

        for row in result:
            chat_id = row[0]
            bot.send_message(chat_id, admin_message)

    if(data['action'] == "select_profile"):
        client_id = data['clinic_id']

        sql = "SELECT * FROM `users` WHERE `ClinicIQ_id`='" + str(client_id) + "'"
        result = sql_query(sql)

        if(len(result) > 0):
            bot.send_message(call.message.chat.id, "Этот профиль уже привязан к телеграм!")
            return

        sql = "SELECT * FROM `ClinicIQ_users` WHERE `id`='" + str(client_id) + "'"
        result = sql_query(sql)
        
        sql = "UPDATE `users` SET `phone`='" + str(result[0][6]) + "', `name`='" + str(result[0][2]) + "', `surname`='" + str(result[0][3]) + "', `lastname`='" + str(result[0][4]) + "', `ClinicIQ_id`='" + str(client_id) + "', `status`='main_menu' WHERE `id`='" + str(call.message.chat.id) + "'"
        sql_query(sql)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Мои записи 📆")
        btn2 = types.KeyboardButton("Как доехать 🗺️")
        btn3 = types.KeyboardButton("Связаться с админом 👨‍💻")
        btn4 = types.KeyboardButton("Записаться на приём ⌚️")

        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(call.message.chat.id, "Добрый день! Чем я могу помочь?",  reply_markup=markup)

    if(data['action'] == "add_client"):
        client_id = data['client_id']

        sql = "DELETE FROM `postman` WHERE `user_id`='" + str(client_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='adding_client_to_build' WHERE `id`='" + str(call.message.chat.id) + "'"
        sql_query(sql)


        sql = "SELECT * FROM `config` WHERE `param`='pattern'"

        result = sql_query(sql)

        pattern_id = result[0][1]

        sql = "SELECT * FROM `sendler` WHERE `id`='" + str(pattern_id) + "'"

        result = sql_query(sql)

        pattern_text = result[0][1]

        reg_exp = "[%][a-zA-Z]*[%]"

        variables_list = re.findall(reg_exp, pattern_text)

        not_reserved_vars = []
        is_not_reserved_created = False
        for match in variables_list:
            if (match == "%username%" or match == "%usersurname%" or match == "%userpatronymic%"):
                continue
            
            not_reserved_vars.append({
                "key":match,
                "value":"not_setted"
            })

            if is_not_reserved_created == False:
                message = "Укажите значение переменной " + str(match) + "" 
                bot.send_message(call.message.chat.id, message)

                is_not_reserved_created = True

        if is_not_reserved_created:
            data = {
                "author":call.message.chat.id,
                "variables":not_reserved_vars
            }

            sql = "INSERT INTO `postman`(`user_id`, `chat_variables`, `status`) VALUES ('"+ str(client_id) +"','" + json.dumps(data) + "', 'building')"
            print(sql)
            sql_query(sql)

            return

        data = {
            "author":call.message.chat.id,
            "variables":[]
        }

        sql = "INSERT INTO `postman`(`user_id`, `chat_variables`, `status`) VALUES ('"+ str(client_id) +"','" + json.dumps(data) + "', 'building')"
        sql_query(sql)

        sql = "UPDATE `postman` SET `status`='ready' WHERE `user_id`='" + str(client_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='main_menu' WHERE `id`='" + str(call.message.chat.id) + "'"
        sql_query(sql)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Шаблоны 🛠️")
        btn2 = types.KeyboardButton("Сборка 🧩")
        btn3 = types.KeyboardButton("Старт 📮")
        btn4 = types.KeyboardButton("Помощь 🗿")
        btn5 = types.KeyboardButton("Главное меню ⬅️")

        markup.add(btn1, btn2, btn3, btn4, btn5)

        bot.send_message(call.message.chat.id, "Клиент успешно добавлен в сборку!",  reply_markup=markup)

        return
        
    if(data['action'] == "create_sendler_pattern"):
        sql = "UPDATE `users` SET `status`='await_postman_pattern' WHERE `id`='" + str(call.message.chat.id) + "'"

        sql_query(sql)

        bot.send_message(call.message.chat.id, "Создайте текст шаблона. Для использования переменных используйте %variable_name%.")

        return

    if(data['action'] == "get_sendler_pattern"):
        pattern_id = data['pattern_id']

        sql = "SELECT * FROM `sendler` WHERE `id`='" + str(pattern_id) + "'"

        result = sql_query(sql)

        if(len(result) == 0):
            bot.send_message(call.message.chat.id, "Шаблон не найден!")

            return

        pattern_text = result[0][1]

        markup = types.InlineKeyboardMarkup()

        data = {
            "action":"set_pattern_as_main",
            "pattern_id":pattern_id
        }

        btn = types.InlineKeyboardButton("Выбрать шаблон", callback_data=json.dumps(data))
        markup.add(btn)
            
        bot.send_message(call.message.chat.id, pattern_text, reply_markup=markup)

        return

    if(data['action'] == "set_pattern_as_main"):
        pattern_id = data['pattern_id']

        sql = "UPDATE `config` SET `value`='" + str(pattern_id) + "'"

        sql_query(sql)

        sql = "TRUNCATE `postman`"

        sql_query(sql)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton("Шаблоны 🛠️")
        btn2 = types.KeyboardButton("Сборка 🧩")
        btn3 = types.KeyboardButton("Старт 📮")
        btn4 = types.KeyboardButton("Помощь 🗿")
        btn5 = types.KeyboardButton("Главное меню ⬅️")

        markup.add(btn1, btn2, btn3, btn4, btn5)


        bot.send_message(call.message.chat.id, "Шабон " + str(pattern_id) + " выбран. Сборка очищена.", reply_markup=markup)

        return

    if(data['action'] == "reply_to_client"):
        report_id = data['report_id']

        sql = "SELECT * FROM `reports` WHERE `status`='await' AND `id`='" + str(report_id) + "'"
        result = sql_query(sql)

        if(len(result) == 0):
            bot.send_message(call.message.chat.id, "Запрос не найден или устарел!")
            return
        
        report_data = result[0]

        report_user_id = report_data[1]

        sql = "SELECT * FROM `users` WHERE `id`='"+str(report_user_id)+"'"
        result = sql_query(sql)

        user_data = result[0]
        report_user_chat_id = user_data[0]

        sql = "UPDATE `reports` SET `status`='working', `admin_id`='"+str(call.message.chat.id)+"' WHERE `id`='" + str(report_id) + "'"
        sql_query(sql)

        sql = "UPDATE `users` SET `status`='in_chat' WHERE `id`='"+ str(report_user_id) +"'"
        sql_query(sql)

        sql="UPDATE `users` SET `status`='in_admin_chat' WHERE `id`='"+ str(call.message.chat.id) +"'"
        sql_query(sql)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn = types.KeyboardButton("Закончить чат")

        markup.add(btn)

        bot.send_message(report_user_chat_id, "Администратор вошёл в чат!", reply_markup=markup)

        bot.send_message(call.message.chat.id, "Вы вошли в чат по заявке " + str(report_id) + "!", reply_markup=markup)

@application.route('/', methods=['POST'])
def request_worker():
    return 'test'

while True:
    try:
        bot.polling(non_stop=True, interval=0)
        application.run(host="0.0.0.0", port=33)
    except Exception as e:
        print(e)
        time.sleep(5)
        continue