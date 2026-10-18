"""``varag bench make-error-clue``: a failing snippet plus its real traceback (handoff, clue rules).

The snippet (the author's, 5 to 15 lines using the other version's API) runs in the target
environment through the same stripped environment and limits as the harness. The clue file is the
snippet, a blank line, and the captured traceback. The command refuses (user decision 2026-10-18)
when the traceback names nothing exclusive: an exclusive symbol or keyword, a value a confirmed
value rule rejects, or a migration message. The snippet itself must pass the version-number lint;
the traceback is exempt.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from varag.bench.schema import Concept, lint_version_mentions
from varag.config import env_name, load_experiment
from varag.envs.runner import env_python, stripped_env
from varag.pipeline.extract import extract_signals
from varag.pipeline.infer import INFER, infer

TRACEBACK = "Traceback (most recent call last)"


def capture_traceback(library: str, side: str, snippet: str) -> str:
    """Run the snippet in the side's environment and return its stderr traceback."""
    python = env_python(env_name(library, side))
    timeout = int(load_experiment().get("execution", {}).get("timeout_s", 60))
    with tempfile.TemporaryDirectory(prefix="varag-clue-") as tmp:
        path = Path(tmp) / "snippet.py"
        path.write_text(snippet.rstrip() + "\n", encoding="utf-8", newline="\n")
        proc = subprocess.run([str(python), "-I", str(path)], cwd=tmp, env=stripped_env(python, {"TEMP": tmp, "TMP": tmp, "TMPDIR": tmp}),
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode == 0:
        raise RuntimeError(f"the snippet ran without error in {library} {side}; an error clue needs a failure")
    text = proc.stderr.strip()
    if TRACEBACK not in text:
        raise RuntimeError(f"no traceback captured in {library} {side}: {text[-400:]}")
    return re.sub(re.escape(tmp) + r"[\\/]", "", text)


def names_something_exclusive(library: str, clue_text: str) -> list[str]:
    """The exclusive things the traceback names, as the extractor sees them."""
    signals = extract_signals("", clue_text, library)
    return [f"{s.kind}:{s.symbol}" for s in signals.signals if s.source == "error" or s.kind == "message"]


def make_error_clue(concept: Concept, target: str, snippet: str, overlap: str = "off_target") -> dict:
    if concept.exclusivity == "behavior":
        raise RuntimeError("behaviour concepts carry pin and code clues only (docs/DECISIONS.md, 2026-10-18)")
    hits = lint_version_mentions(snippet)
    if hits:
        raise RuntimeError(f"the snippet names a version in prose: {hits}")
    traceback = capture_traceback(concept.library, target, snippet)
    clue_text = snippet.rstrip() + "\n\n" + traceback + "\n"
    named = names_something_exclusive(concept.library, clue_text)
    if not named:
        raise RuntimeError("refused: the traceback names no exclusive symbol, keyword, rejected value or migration message")
    decision = infer(extract_signals("", clue_text, concept.library))
    path = concept.directory / "clues" / f"{target}_error.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text(clue_text, encoding="utf-8", newline="\n")
    return {
        "file": path.relative_to(concept.directory).as_posix(),
        "named": named,
        "decision": f"{decision.kind}" + (f"({decision.side})" if decision.side else ""),
        "infers_target": decision.kind == INFER and decision.side == target,
        "yaml": f"    - {{type: error, file: clues/{target}_error.txt, overlap: {overlap}}}",
    }
