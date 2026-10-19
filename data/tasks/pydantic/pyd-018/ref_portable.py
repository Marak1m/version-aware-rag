from typing import List

from pydantic import BaseModel


class Scores(BaseModel):
    values: List[int]


def parse_scores(data):
    return Scores(values=data).values
