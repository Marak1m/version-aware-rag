from pydantic import BaseModel, Field


class Contact(BaseModel):
    email: str = Field(..., to_lower=True)


def make_contact(email):
    return Contact(email=email)
