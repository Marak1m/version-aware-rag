import pandas as pd


def one_tag_per_row(tags):
    return tags.explode()
