import pytest
from pydantic import ValidationError

from solution import build_org_models


def test_nested_manager_is_validated():
    Employee = build_org_models()
    employee = Employee(name="ada", manager={"name": "grace", "reports": "3"})
    assert employee.name == "ada"
    assert employee.manager.name == "grace"
    assert employee.manager.reports == 3
    assert type(employee.manager).__name__ == "Manager"


def test_manager_is_optional():
    Employee = build_org_models()
    assert Employee(name="bob").manager is None


def test_bad_manager_is_rejected():
    Employee = build_org_models()
    with pytest.raises(ValidationError):
        Employee(name="ada", manager={"reports": "many"})
