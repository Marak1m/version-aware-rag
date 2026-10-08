"""Validation steps 6 and 7 skip while their milestone modules are missing, and fail once a
module exists without its check."""

import sys
import types

from varag.bench.validate import HOOKED_STEPS, _hooked_step


def test_missing_module_skips():
    for number in HOOKED_STEPS:
        assert sys.modules.get(HOOKED_STEPS[number][0]) is None
        step = _hooked_step(number, concept=None)
        assert step.status == "skipped" and step.detail


def test_module_without_check_fails(monkeypatch):
    module_name, func_name, _ = HOOKED_STEPS[7]
    monkeypatch.setitem(sys.modules, module_name, types.ModuleType(module_name))
    step = _hooked_step(7, concept=None)
    assert step.status == "fail" and func_name in step.detail


def test_module_with_check_passes_or_fails_on_problems(monkeypatch):
    module_name, func_name, _ = HOOKED_STEPS[6]
    fake = types.ModuleType(module_name)
    setattr(fake, func_name, lambda concept: [])
    monkeypatch.setitem(sys.modules, module_name, fake)
    assert _hooked_step(6, concept=None).status == "pass"
    setattr(fake, func_name, lambda concept: ["clue old_pin infers new"])
    step = _hooked_step(6, concept=None)
    assert step.status == "fail" and "old_pin" in step.detail
