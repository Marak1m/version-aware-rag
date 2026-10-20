from pydantic import BaseModel


class Ticker(BaseModel):
    symbol: str

    class Config:
        case_sensitive = False


def make_ticker(symbol):
    return Ticker(symbol=symbol)
