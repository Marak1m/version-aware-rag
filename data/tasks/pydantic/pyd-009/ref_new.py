from pydantic import BaseModel, ConfigDict


class Contact(BaseModel):
    model_config = ConfigDict(str_to_lower=True)

    email: str


def make_contact(email):
    return Contact(email=email)
