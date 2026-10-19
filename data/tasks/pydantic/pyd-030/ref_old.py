from pydantic import parse_obj_as


def parse_ids(values):
    return parse_obj_as(list[int], values)
