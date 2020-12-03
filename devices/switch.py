from .device import Device


class Switch(Device):
    def __init__(self, name: str, hostname: str):
        super().__init__(name, hostname)

    def toggle(self):
        raise NotImplemented

    def turn_on(self):
        raise NotImplemented

    def turn_off(self):
        raise NotImplemented

    def get_status(self):
        raise NotImplemented

    def set_status(self, **kwargs):
        raise NotImplemented

    def schedule(self, **kwargs):
        raise NotImplemented
