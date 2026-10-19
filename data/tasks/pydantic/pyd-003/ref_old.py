from pydantic import BaseModel


class Tag(BaseModel):
    label: str

    class Config:
        anystr_strip_whitespace = True


def make_tag(text):
    return Tag(label=text)
