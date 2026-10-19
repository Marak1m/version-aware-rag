from typing import List

from pydantic import BaseModel


class Scores(BaseModel):
    __root__: List[int]


def parse_scores(data):
    return Scores.parse_obj(data).__root__
