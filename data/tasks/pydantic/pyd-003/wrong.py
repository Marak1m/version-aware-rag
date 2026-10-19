from pydantic import BaseModel


class Tag(BaseModel):
    label: str

    class Config:
        strip_whitespace = True


def make_tag(text):
    return Tag(label=text)
