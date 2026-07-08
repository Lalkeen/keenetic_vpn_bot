import json as json_lib

import keenetic


def check_credentials(host, password) -> bool:
    """Проверяет, что роутер отвечает и логин/пароль подходят."""
    try:
        router = keenetic.Router(username="admin", password=password, host=host, port=443)
        response = router.get('/rci/show/ip/hotspot')
        return response.ok
    except Exception:
        return False


def get_policies(host, password):
    """Возвращает {policy_id: description} доступных политик маршрутизации."""
    router = keenetic.Router(username="admin", password=password, host=host, port=443)
    response = router.get('/rci/show/rc/ip/policy')
    if not response.ok:
        return {}
    data = json_lib.loads(response.text)
    return {policy_id: info.get('description', policy_id) for policy_id, info in data.items()}


def set_policy(mac, host, password, policy):
    """policy — id политики (например, 'Policy0') или None для прямого подключения без VPN."""
    addr = '/rci/ip/hotspot/host'
    json = {'mac': mac, 'permit': 'true', 'policy': policy if policy else False}
    router = keenetic.Router(username="admin", password=password, host=host, port=443)
    router.post(addr, json)


def wake(mac, host, password):
    addr = '/rci/ip/hotspot/wake'
    json = {'mac': mac}
    router = keenetic.Router(username="admin", password=password, host=host, port=443)
    router.post(addr, json)
