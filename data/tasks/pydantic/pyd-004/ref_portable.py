from pydantic import BaseModel

try:
    from pydantic import model_validator
except ImportError:
    from pydantic import root_validator

    class Range(BaseModel):
        lo: int
        hi: int

        @root_validator(skip_on_failure=True)
        def ordered(cls, values):
            if values["hi"] < values["lo"]:
                raise ValueError("hi must be at least lo")
            return values
else:
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
