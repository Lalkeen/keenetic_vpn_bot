import keenetic

def api_on(mac, host, password):
    addr = '/rci/ip/hotspot/host'
    json = {"mac":'', 'permit': 'true', 'policy': 'Policy0'}
    json['mac'] = mac
    router = keenetic.Router(username="admin", password=password, host=host, port=80)
    for device in router.connected_devices:
        if device['mac'] == json['mac']:
            print("______________________________")
            print(device)
    router.post(addr, json)
    return "На устройстве включен ВПН"

def api_off(mac, host, password):
    addr = '/rci/ip/hotspot/host'
    json = {"mac": '', 'permit': 'true', 'policy': False}
    json['mac'] = mac
    router = keenetic.Router(username="admin", password=password, host=host, port=80)
    for device in router.connected_devices:
        if device['mac'] == json['mac']:
            print("______________________________")
            print(device)
    router.post(addr, json)
    return "На устройстве выключен ВПН"