from pydantic import BaseModel, model_validator


class Range(BaseModel):
    lo: int
    hi: int

    @model_validator(mode="after")
    def ordered(self):
        if self.hi < self.lo:
            raise ValueError("hi must be at least lo")
        return self


def make_range(lo, hi):
    return Range(lo=lo, hi=hi)
