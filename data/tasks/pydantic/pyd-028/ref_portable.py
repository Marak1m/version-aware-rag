from pydantic import BaseModel

try:
    from pydantic import ImportString as ImportPath
except ImportError:
    from pydantic import PyObject as ImportPath


class Hook(BaseModel):
    target: ImportPath


def load_hook(path):
    return Hook(target=path)
