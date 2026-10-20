from typing import ClassVar

from pydantic import BaseModel


class Unit:
    def __init__(self, symbol):
        self.symbol = symbol


class Reading(BaseModel):
    value: float
    unit: ClassVar[Unit] = Unit("m")


def make_reading(value):
    return Reading(value=value)
