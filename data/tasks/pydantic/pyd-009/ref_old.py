from pydantic import BaseModel


class Contact(BaseModel):
    email: str

    class Config:
        anystr_lower = True


def make_contact(email):
    return Contact(email=email)
