from pydantic import BaseModel, root_validator


class Range(BaseModel):
    lo: int
    hi: int

    @root_validator
    def ordered(cls, values):
        if values.get("hi") is not None and values.get("lo") is not None and values["hi"] < values["lo"]:
            raise ValueError("hi must be at least lo")
        return values


def make_range(lo, hi):
    return Range(lo=lo, hi=hi)
