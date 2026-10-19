from pydantic import BaseModel, ConfigDict


class Tag(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label: str


def make_tag(text):
    return Tag(label=text)
