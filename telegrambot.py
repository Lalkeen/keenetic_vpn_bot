import commands
import telebot


bot = telebot.TeleBot('BOT-TOKEN')

tv_id = 'LGwebOSTV' # Тут название девайса


@bot.message_handler(commands=['start'])
def salam(message) -> None:
    bot.send_message(message.chat.id, f'Salam!')
    bot.send_message(message.chat.id, f'Команды: /on_vpn_on_tv /off_vpn_on_tv')


@bot.message_handler(commands=['on_vpn_on_tv'])
def on_vpn_on_tv(message) -> None:
    bot.send_message(message.chat.id, f'Работаем, братья')

    try:
        commands.move_to_vpn(tv_id) # в скобки передаем устройство
        bot.send_message(message.chat.id, f'VPN на телевизоре включен')
    except:
        commands.exit()
        bot.send_message(message.chat.id, f'Ты ошибся, парень')


@bot.message_handler(commands=['off_vpn_on_tv'])
def off_vpn_on_tv(message) -> None:
    bot.send_message(message.chat.id, f'Работаем, братья')
    try:
        commands.move_back(tv_id) # в скобки передаем устройство
        bot.send_message(message.chat.id, f'VPN на телевизоре выключен')
    except:

        bot.send_message(message.chat.id, f'Ты ошибся, парень')


bot.infinity_polling(timeout=10, long_polling_timeout = 5)
