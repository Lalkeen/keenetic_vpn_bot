import commands
import telebot
from telebt import types
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
import json

bot = telebot.TeleBot('BOT-TOKEN')

host = '192.168.1.1'
password = 'admin'

with open('alllists.json', 'r') as f:
    alllists = json.load(f)

maclist = alllists['maclist']
wollist = alllists['wollist']
whitelist = alllists['whitelist']

@bot.message_handler(commands=['start'])
def salam(message) -> None:
    if message.chat.id in whitelist:
        markup = InlineKeyboardMarkup()
        for button_id, button_text in maclist.items():
            markup.add(telebot.types.InlineKeyboardButton(text=button_id, callback_data=f'del_{button_id}'))
        bot.send_message(message.chat.id, "Выбери устройство, затем действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Ты ошибся дверью, браток')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    markup = InlineKeyboardMarkup()
    for button_id, button_text in maclist.items():
        markup.add(telebot.types.InlineKeyboardButton(text=button_id, callback_data=f'del_{button_id}'))
    if call.data in maclist.values():
        new_markup = InlineKeyboardMarkup()
        new_markup.add(types.InlineKeyboardButton(text='On', callback_data=f'on_{call.data}'))
        new_markup.add(types.InlineKeyboardButton(text='Off', callback_data=f'off_{call.data}'))
        if call.data in wollist:
            new_markup.add(types.InlineKeyboardButton(text='wake', callback_data=f'wake_{call.data}'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=new_markup)
    elif call.data.startswith('on_'):
        mac = call.data.split('_')[1]
        commands.api_on(mac, host, password)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Сделано! Что дальше?", reply_markup=markup)
    elif call.data.startswith('off_'):
        mac = call.data.split('_')[1]
        commands.api_off(mac, host, password)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Сделано! Что дальше?", reply_markup=markup)
    elif call.data.startswith('wake_'):
        mac = call.data.split('_')[1]
        commands.wake(mac, host, password)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Сделано! Что дальше?", reply_markup=markup)
    elif call.data.startswith('addtowol_'):
        mac = call.data.split('_')[1]
        wollist.append(mac)
        alllists["wollist"] = list(wollist)
        with open('alllists.json', 'w') as file:
            json.dump(alllists, file)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Устройство добавлено в список')
        salam(call.message)
    elif call.data == 'notaddtowol':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Устройство не будет добавлено в список')
        salam(call.message)
    elif call.data.startswith('del_'):
        device_name = call.data.split('_')[1]
        if device_name in maclist:
            del maclist[device_name]
            alllists["maclist"] = dict(maclist)
            with open('alllists.json', 'w') as file:
                json.dump(alllists, file)
            bot.send_message(call.message.chat.id, f'Устройство {device_name} удалено из списка')
            salam(call.message)


@bot.message_handler(commands=['reg'])
def reg(message) -> None:
    if message.chat.id in whitelist:
        bot.send_message(message.chat.id,
                         f'Для добавления устройства в список отправь сообщение типа "Имя_устройства МАК_адрес", например: TV 11:11:11:11:11:11')
        bot.register_next_step_handler(message, add_device)


@bot.message_handler(commands=['del'])
def delet(message) -> None:
    markup = InlineKeyboardMarkup()
    for button_id, button_text in maclist.items():
        markup.add(telebot.types.InlineKeyboardButton(text=button_id, callback_data=f'del_{button_id}'))
    if message.chat.id in whitelist:
        bot.send_message(message.chat.id, "Что будем удалять?", reply_markup=markup)


def add_device(message) -> None:
    try:
        device_name, mac_address = message.text.split()
        maclist[device_name] = mac_address
        alllists["maclist"] = dict(maclist)
        with open('alllists.json', 'w') as file:
            json.dump(alllists, file)
        bot.send_message(message.chat.id,
                         f'Устройство {device_name} с МАК-адресом {mac_address} добавлено в список.')
        wol_markup = InlineKeyboardMarkup()
        wol_markup.add(types.InlineKeyboardButton(text='Да', callback_data=f'addtowol_{mac_address}'))
        wol_markup.add(types.InlineKeyboardButton(text='Нет', callback_data='notaddtowol'))
        bot.send_message(message.chat.id, 'Добавить в список wake-on-lan?', reply_markup=wol_markup)
    except ValueError:
        bot.send_message(message.chat.id,
                         'Неверный формат сообщения. Пожалуйста, отправьте сообщение типа "Имя_устройства МАК_адрес".')


@bot.message_handler(commands=['auth'])
def auth(message) -> None:
    bot.send_message(message.chat.id, message.chat.id)


bot.infinity_polling(timeout=10, long_polling_timeout=5)
