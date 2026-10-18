"""Closed-choice question templates (handoff, policy notes) and the reply parser."""

from __future__ import annotations

import re

from varag.config import load_libraries

NOT_SURE = re.compile(r"\b(not sure|unsure|no idea|don't know|dont know|do not know)\b", re.I)
NUMBER = re.compile(r"\b[vV]?(\d+)(?:\.\d+)*\b")


def major(version: str) -> str:
    return version.split(".")[0]


def module_name(library: str) -> str:
    return load_libraries()["libraries"][library]["module"]


def uncertain_question(library: str, versions: dict[str, str]) -> str:
    module = module_name(library)
    return (f"Which version of {library} are you on: {major(versions['old'])}.x or {major(versions['new'])}.x? "
            f"The answer differs between them. You can check with "
            f"`python -c \"import {module}; print({module}.__version__)\"`. "
            f"If you are not sure, say so and I will give both.")


def conflict_question(library: str, versions: dict[str, str], pin: str, symbol: str, symbol_side: str) -> str:
    other_major = major(versions[symbol_side])
    return (f"Your requirements say {pin}, but your code uses {symbol}, which only exists in {library} "
            f"{other_major}.x. Which is installed: {major(versions['old'])}.x or {major(versions['new'])}.x?")


def parse_version(reply: str, versions: dict[str, str]) -> str | None:
    """``old`` or ``new`` when the reply names exactly one side's major version; None for "not
    sure" or an unusable reply."""
    if NOT_SURE.search(reply):
        return None
    majors = {side: major(v) for side, v in versions.items()}
    found = {side for m in NUMBER.finditer(reply) for side, mj in majors.items() if m.group(1) == mj}
    return found.pop() if len(found) == 1 else None
