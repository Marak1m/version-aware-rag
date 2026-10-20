from pydantic import BaseModel


class Ticker(BaseModel):
    symbol: str

    class Config:
        anystr_upper = True


def make_ticker(symbol):
    return Ticker(symbol=symbol)
