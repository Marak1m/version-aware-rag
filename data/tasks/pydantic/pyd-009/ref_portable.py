from pydantic import BaseModel, constr


class Contact(BaseModel):
    email: constr(to_lower=True)


def make_contact(email):
    return Contact(email=email)
