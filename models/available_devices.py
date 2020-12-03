from enum import Enum


class Devices(str, Enum):
    fan = "192.168.50.208"
    tree = "192.168.50.191"
    bed = "192.168.50.161"
