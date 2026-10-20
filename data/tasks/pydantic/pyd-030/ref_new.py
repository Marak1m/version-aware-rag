from pydantic import TypeAdapter


def parse_ids(values):
    return TypeAdapter(list[int]).validate_python(values)
