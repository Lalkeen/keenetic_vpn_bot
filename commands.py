import keenetic

def api_on(mac, host, password):
    addr = '/rci/ip/hotspot/host'
    json = {"mac": mac, 'permit': 'true', 'policy': 'Policy0'}
    router = keenetic.Router(username="admin", password=password, host=host, port=80)
    router.post(addr, json)


def api_off(mac, host, password):
    addr = '/rci/ip/hotspot/host'
    json = {"mac": mac, 'permit': 'true', 'policy': False}
    router = keenetic.Router(username="admin", password=password, host=host, port=80)
    router.post(addr, json)


def wake(mac, host, password):
    addr = '/rci/ip/hotspot/wake'
    json = {'mac': mac}
    router = keenetic.Router(username="admin", password=password, host=host, port=80)
    router.post(addr, json)
    
