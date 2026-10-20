from pydantic import BaseModel, ConfigDict


class Ticker(BaseModel):
    model_config = ConfigDict(str_to_upper=True)

    symbol: str


def make_ticker(symbol):
    return Ticker(symbol=symbol)
