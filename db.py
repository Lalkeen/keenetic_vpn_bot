from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import crypto_utils
from models import Device, Router, UserRouter, UserState

DB_PATH = Path(__file__).parent / 'bot.db'

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


# ---------- routers ----------

def get_or_create_router(host, password) -> int:
    password_hash = crypto_utils.hash_password(password)
    with Session() as session:
        router = session.query(Router).filter_by(host=host, password_hash=password_hash).one_or_none()
        if router is not None:
            return router.id
        router = Router(host=host, password_hash=password_hash, password_encrypted=crypto_utils.encrypt_password(password))
        session.add(router)
        session.commit()
        return router.id


def link_user_router(user_id, router_id) -> None:
    with Session() as session:
        link = session.get(UserRouter, (user_id, router_id))
        if link is None:
            session.add(UserRouter(user_id=user_id, router_id=router_id))
            session.commit()


def get_user_routers(user_id):
    """Список (router_id, host) роутеров, доступных пользователю."""
    with Session() as session:
        rows = (
            session.query(Router.id, Router.host)
            .join(UserRouter, UserRouter.router_id == Router.id)
            .filter(UserRouter.user_id == user_id)
            .order_by(Router.id)
            .all()
        )
        return [(row.id, row.host) for row in rows]


def get_router(router_id):
    """(host, password) роутера или None. Пароль расшифровывается на лету."""
    with Session() as session:
        router = session.get(Router, router_id)
        return (router.host, crypto_utils.decrypt_password(router.password_encrypted)) if router else None


def set_current_router(user_id, router_id) -> None:
    with Session() as session:
        state = session.get(UserState, user_id)
        if state is None:
            session.add(UserState(user_id=user_id, current_router_id=router_id))
        else:
            state.current_router_id = router_id
        session.commit()


def get_current_router_id(user_id):
    with Session() as session:
        state = session.get(UserState, user_id)
        return state.current_router_id if state else None


# ---------- devices ----------

def get_devices(router_id):
    """Список (name, mac, wol) устройств роутера."""
    with Session() as session:
        rows = (
            session.query(Device.name, Device.mac, Device.wol)
            .filter(Device.router_id == router_id)
            .order_by(Device.name)
            .all()
        )
        return [(row.name, row.mac, row.wol) for row in rows]


def add_device(router_id, name, mac) -> None:
    with Session() as session:
        device = session.query(Device).filter_by(router_id=router_id, name=name).one_or_none()
        if device is None:
            session.add(Device(router_id=router_id, name=name, mac=mac, wol=0))
        else:
            device.mac = mac
        session.commit()


def delete_device(router_id, name) -> None:
    with Session() as session:
        device = session.query(Device).filter_by(router_id=router_id, name=name).one_or_none()
        if device is not None:
            session.delete(device)
            session.commit()


def set_wol(router_id, mac, enabled) -> None:
    with Session() as session:
        device = session.query(Device).filter_by(router_id=router_id, mac=mac).one_or_none()
        if device is not None:
            device.wol = 1 if enabled else 0
            session.commit()


def is_wol(router_id, mac) -> bool:
    with Session() as session:
        device = session.query(Device).filter_by(router_id=router_id, mac=mac).one_or_none()
        return bool(device and device.wol)
