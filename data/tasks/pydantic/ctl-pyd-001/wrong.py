from pydantic import BaseModel, Field


class Job(BaseModel):
    name: str
    retries: int = Field(default=0)


def make_job(name):
    return Job(name=name)
