from pydantic import BaseModel, conint


class Rating(BaseModel):
    stars: conint(gt=1, lt=5)


def make_rating(stars):
    return Rating(stars=stars)
