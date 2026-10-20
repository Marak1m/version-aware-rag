from typing import Optional

from pydantic import BaseModel


def build_org_models():
    class Employee(BaseModel):
        name: str
        manager: Optional["Manager"] = None

    class Manager(BaseModel):
        name: str
        reports: int = 0

    Employee.model_rebuild()
    return Employee
