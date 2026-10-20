from pydantic import BaseModel


class Comment(BaseModel):
    text: str

    class Config:
        max_anystr_length = 20


def make_comment(text):
    return Comment(text=text)
