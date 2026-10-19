"""The rule-based simulated user (handoff L7). It cannot leak the solution: it only knows the
library and the instance's version.

Arms (``user_arm`` in configs/experiment.yaml): ``knows`` replies "I'm on {library} {v*}." and
``unsure`` replies "I'm not sure." Either arm answers only when the question names the library or
the word "version"; otherwise it replies "I'm not sure what you're asking." and the run logs
``question_relevant: false``.

A third arm, ``leak_audit``, exists only for the leak audit (handoff L7): every question is treated
as if it had been replaced by an irrelevant one, so the user always replies "I'm not sure what
you're asking." and nothing about the version reaches the model. Its pass rate must not exceed the
rate the method reaches with an uninformative reply (the ``unsure`` arm).
"""

from __future__ import annotations

from dataclasses import dataclass

ARMS = ("knows", "unsure", "leak_audit")
IRRELEVANT_QUESTION = "Which operating system are you developing on?"


@dataclass
class Reply:
    text: str
    relevant: bool


class SimulatedUser:
    def __init__(self, arm: str, library: str, versions: dict[str, str]):
        if arm not in ARMS:
            raise ValueError(f"user_arm must be one of {ARMS}, not {arm!r}")
        self.arm = arm
        self.library = library
        self.versions = versions

    def relevant(self, question: str) -> bool:
        q = question.lower()
        return self.library.lower() in q or "version" in q

    def reply(self, question: str, target: str | None) -> Reply:
        if self.arm == "leak_audit":
            question = IRRELEVANT_QUESTION
        if not self.relevant(question):
            return Reply("I'm not sure what you're asking.", False)
        if self.arm == "unsure":
            return Reply("I'm not sure.", True)
        # A control has no target version; the knowing user names the old one, deterministically.
        version = self.versions[target or "old"]
        return Reply(f"I'm on {self.library} {version}.", True)
