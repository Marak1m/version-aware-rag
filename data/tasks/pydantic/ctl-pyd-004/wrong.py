from pydantic import BaseModel, conint


class Progress(BaseModel):
    percent: conint(ge=0, le=100)


def make_progress(percent):
    return Progress(percent=percent)
