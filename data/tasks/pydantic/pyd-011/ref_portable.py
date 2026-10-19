from pydantic import BaseModel, constr


class Comment(BaseModel):
    text: constr(max_length=20)


def make_comment(text):
    return Comment(text=text)
