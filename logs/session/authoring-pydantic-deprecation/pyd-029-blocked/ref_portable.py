try:
    from pydantic import validate_call as validate_args
except ImportError:
    from pydantic import validate_arguments as validate_args


@validate_args
def scale(value: int, factor: int):
    return value * factor
