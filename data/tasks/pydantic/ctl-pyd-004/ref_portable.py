from pydantic import BaseModel, confloat


class Progress(BaseModel):
    percent: confloat(ge=0, le=100)


def make_progress(percent):
    return Progress(percent=percent)
