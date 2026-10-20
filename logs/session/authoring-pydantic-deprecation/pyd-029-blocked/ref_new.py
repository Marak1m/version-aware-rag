from pydantic import validate_call


@validate_call
def scale(value: int, factor: int):
    return value * factor
