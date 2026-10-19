from pydantic import BaseModel


class Range(BaseModel):
    lo: int
    hi: int


def make_range(lo, hi):
    if hi < lo:
        raise ValueError("hi must be at least lo")
    return Range(lo=lo, hi=hi)
