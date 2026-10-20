from typing import List

from pydantic import RootModel


class Scores(RootModel[List[int]]):
    pass


def parse_scores(data):
    return Scores.model_validate(data).root
