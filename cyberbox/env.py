import enum

from cyberbox.utils import AutoName


@enum.unique
class Env(AutoName):
    test = enum.auto()
    dev = enum.auto()
    prod = enum.auto()
