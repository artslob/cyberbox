from enum import Enum


class AutoName(Enum):
    """ Base class for enums with equal string names and values. """

    def _generate_next_value_(name, start, count, last_values):
        return name
