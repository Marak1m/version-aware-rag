from typing import Optional

from pydantic import BaseModel


def build_org_models():
    class Manager(BaseModel):
        name: str
        reports: int = 0

    class Employee(BaseModel):
        name: str
        manager: Optional[Manager] = None

    return Employee
