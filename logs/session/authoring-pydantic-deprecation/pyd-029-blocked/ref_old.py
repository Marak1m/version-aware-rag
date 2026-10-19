from pydantic import validate_arguments


@validate_arguments
def scale(value: int, factor: int):
    return value * factor
