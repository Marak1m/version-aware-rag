from pydantic import BaseModel, ConfigDict


class Comment(BaseModel):
    model_config = ConfigDict(str_max_length=20)

    text: str


def make_comment(text):
    return Comment(text=text)
