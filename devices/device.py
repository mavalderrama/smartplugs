from abc import ABC, abstractmethod


class Device(ABC):
    def __init__(self, name: str, hostname: str):
        """
        Device interface
        :param name: name of the device
        :param hostname: hostname or ip the device
        """
        self.device = hostname
        self.name = name

    @abstractmethod
    def toggle(self):
        pass

    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def set_status(self, **kwargs):
        pass

    @abstractmethod
    def schedule(self, **kwargs):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def reboot(self, time_delay):
        pass

    @abstractmethod
    def reset_factory_default(self):
        pass
