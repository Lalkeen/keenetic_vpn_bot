from hashlib import md5, sha256
from json import loads

from requests import Session


class ConnectedDevice:
    def __init__(self, dictionary):
        self.__dict__ = {
            key.replace("-", "_"): value for key, value in dictionary.items()
        }

    def __str__(self):
        """Форматирование данных устройства."""
        info = ["{} = {}".format(key, value) for key, value in self.__dict__.items()]
        return "\n".join(info)

    def __getattr__(self, attr):
        return self.__dict__.get(attr)


class Router:
    def __init__(self, username="admin", password="admin", host="192.168.1.1", port=80):
        self.__session = Session()
        self.__endpoint = f"http://{host}:{port}"
        self.__username = username
        self.__password = password
        self.__auth()


    def __auth(self):
        response = self.get("/auth")
        if response.status_code == 401:
            realm = response.headers["X-NDM-Realm"]
            password = f"{self.__username}:{realm}:{self.__password}"
            password = md5(password.encode("utf-8"))
            challenge = response.headers["X-NDM-Challenge"]
            password = challenge + password.hexdigest()
            password = sha256(password.encode("utf-8")).hexdigest()
            response = self.post("/auth", {"login": self.__username, "password": password})
        return response.status_code == 200



    def get(self, address, params={}):
        return self.__session.get(self.__endpoint + address, params=params)

    def post(self, address, data):
        return self.__session.post(self.__endpoint + address, json=data)

    @property
    def connected_devices(self):
        response = self.get("/rci/show/ip/hotspot")
        if response.ok:
            devices = loads(response.text)["host"]
            map(ConnectedDevice, devices)
            return devices

            # return list(
            #     filter(lambda device: device.active, map(ConnectedDevice, devices))
            # )
        else:
            if self.__auth():
                return self.connected_devices
            else:
                return []
