from pydantic import BaseModel, constr


class Ticker(BaseModel):
    symbol: constr(to_upper=True)


def make_ticker(symbol):
    return Ticker(symbol=symbol)
