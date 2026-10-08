"""Token counting for the 350-token chunk cap, with the generator's own tokenizer (decision D1).

The tokenizer file is pinned by model revision and sha256 in configs/models.yaml, downloaded on
demand to data/tokenizer/ (gitignored) and refused if its sha256 differs.
"""

from __future__ import annotations

import urllib.request
from functools import lru_cache
from pathlib import Path

from varag.config import load_models, project_root, sha256_file


class TokenizerError(RuntimeError):
    pass


def tokenizer_pin() -> dict:
    return dict(load_models()["tokenizer"])


def tokenizer_path() -> Path:
    pin = tokenizer_pin()
    path = project_root() / pin["local_path"]
    if not path.exists():
        url = f"https://huggingface.co/{pin['repo']}/resolve/{pin['revision']}/{pin['file']}"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "varag"}), timeout=120).read()
        path.write_bytes(data)
    actual = sha256_file(path)
    if actual != pin["sha256"]:
        raise TokenizerError(f"{path} has sha256 {actual}, pinned {pin['sha256']}; delete it to re-download")
    return path


@lru_cache(maxsize=1)
def _tokenizer():
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(tokenizer_path()))


def count_tokens(text: str) -> int:
    return len(_tokenizer().encode(text, add_special_tokens=False).ids)


def tokenizer_provenance() -> dict:
    pin = tokenizer_pin()
    return {"repo": pin["repo"], "revision": pin["revision"], "file": pin["file"], "sha256": pin["sha256"]}
