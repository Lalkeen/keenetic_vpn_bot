import commands
import telebot


bot = telebot.TeleBot('BOT-TOKEN')

tv_id = 'LGwebOSTV' # Тут название девайса


@bot.message_handler(commands=['start'])
def salam(message) -> None:
    bot.send_message(message.chat.id, f'Salam!')
    bot.send_message(message.chat.id, f'Команды: /toggle_vpn_on_tv')


@bot.message_handler(commands=['toggle_vpn_on_tv'])
def toggle_vpn_on_tv(message) -> None:
    bot.send_message(message.chat.id, f'Работаем, братья')

    try:
        bot.send_message(message.chat.id, f'{commands.toggle(tv_id)}')
    except:
        commands.exit()
        bot.send_message(message.chat.id, f'Ты ошибся, парень')


bot.infinity_polling(timeout=10, long_polling_timeout = 5)
