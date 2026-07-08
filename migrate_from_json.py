"""Одноразовый перенос данных из alllists.json + .env (ROUTER_HOST/ROUTER_PASSWORD)
в базу данных (bot.db). Запускать один раз после `alembic upgrade head`.

Доступ к роутеру теперь определяется тем, кто ввёл его host+password в бота,
а не отдельным вайтлистом — при переносе роутер просто создаётся в БД,
без привязки к конкретным пользователям.
"""
import json
import os

from dotenv import load_dotenv

import db

load_dotenv()


def main() -> None:
    db_router_id = None
    host = os.environ.get('ROUTER_HOST')
    password = os.environ.get('ROUTER_PASSWORD')
    if host and password:
        db_router_id = db.get_or_create_router(host, password)
        print(f'Роутер {host} -> router_id={db_router_id}')

    if not os.path.exists('alllists.json'):
        print('alllists.json не найден, переносить нечего.')
        return

    with open('alllists.json', 'r') as f:
        alllists = json.load(f)

    maclist = alllists.get('maclist', {})
    wollist = set(alllists.get('wollist', []))

    if db_router_id is not None:
        for name, mac in maclist.items():
            db.add_device(db_router_id, name, mac)
            if mac in wollist:
                db.set_wol(db_router_id, mac, True)
            print(f'Устройство: {name} ({mac}), wol={mac in wollist}')

    print('Готово.')


if __name__ == '__main__':
    main()
