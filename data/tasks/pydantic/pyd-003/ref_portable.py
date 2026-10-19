from pydantic import BaseModel, constr


class Tag(BaseModel):
    label: constr(strip_whitespace=True)


def make_tag(text):
    return Tag(label=text)
