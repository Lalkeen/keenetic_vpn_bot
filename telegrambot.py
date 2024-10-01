import commands
import telebot


bot = telebot.TeleBot('BOT-TOKEN')

host = '192.168.1.1'
password = 'admin'
tv_id = 'LGwebOSTV'
tv_mac = '11:11:11:11:11:11'


@bot.message_handler(commands=['start'])
def salam(message) -> None:
    bot.send_message(message.chat.id, f'Salam!')
    bot.send_message(message.chat.id, f'Команды: /api_off_on_tv /api_on_on_tv')

@bot.message_handler(commands=['api_on_on_tv'])
def api_on_on_tv(message) -> None:
    bot.send_message(message.chat.id, f'Работаем, братья')

    try:
        bot.send_message(message.chat.id, f'{commands.api_on(tv_mac, host, password)}')
    except:
        commands.exit()
        bot.send_message(message.chat.id, f'Ты ошибся, парень')

@bot.message_handler(commands=['api_off_on_tv'])
def api_on_on_tv(message) -> None:
    bot.send_message(message.chat.id, f'Работаем, братья')

    try:
        bot.send_message(message.chat.id, f'{commands.api_off(tv_mac, host, password)}')
    except:
        commands.exit()
        bot.send_message(message.chat.id, f'Ты ошибся, парень')



bot.infinity_polling(timeout=10, long_polling_timeout = 5)
