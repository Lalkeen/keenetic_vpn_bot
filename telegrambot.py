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
    
maclist = alllists['maclist'] # список устройств
wollist = alllists['wollist'] # wake on lan list - возможность будить устройство 
whitelist = alllists['whitelist'] # вайтлист пользователей. получить айди командой /auth

markup = InlineKeyboardMarkup()
for button_id, button_text in maclist.items():
    markup.add(telebot.types.InlineKeyboardButton(text=button_id, callback_data=button_text))

@bot.message_handler(commands=['start'])
def salam(message) -> None:
    if message.chat.id in whitelist:
        bot.send_message(message.chat.id, f'Salam!')
        bot.send_message(message.chat.id, "Select option:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Ты ошибся дверью, браток')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
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

@bot.message_handler(commands=['auth'])
def auth(message) -> None:
    bot.send_message(message.chat.id, message.chat.id)

bot.infinity_polling(timeout=10, long_polling_timeout = 5)

