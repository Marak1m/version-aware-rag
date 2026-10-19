from pydantic import BaseModel, PyObject


class Hook(BaseModel):
    target: PyObject


def load_hook(path):
    return Hook(target=path)
