from pydantic import BaseModel, conint


class Rating(BaseModel):
    stars: conint(ge=1, le=5)


def make_rating(stars):
    return Rating(stars=stars)
