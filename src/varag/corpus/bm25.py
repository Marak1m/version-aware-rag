"""Okapi BM25 over chunk text, in-repo and deterministic (ties break on chunk_id)."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN = re.compile(r"[A-Za-z][a-z]+|[A-Z]+(?![a-z])|\d+")


def tokenize(text: str) -> list[str]:
    """Lowercased word pieces; identifiers split on dots, underscores and camel case."""
    return [t.lower() for t in TOKEN.findall(text.replace("_", " "))]


class BM25:
    def __init__(self, docs: list[tuple[str, str]], k1: float = 1.5, b: float = 0.75):
        """``docs`` is a list of (doc_id, text)."""
        self.ids = [d for d, _ in docs]
        self.tfs = [Counter(tokenize(t)) for _, t in docs]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        df = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(docs)
        self.idf = {term: math.log(1 + (n - f + 0.5) / (f + 0.5)) for term, f in df.items()}
        self.k1, self.b = k1, b

    def scores(self, query: str) -> list[tuple[float, str]]:
        terms = tokenize(query)
        out = []
        for doc_id, tf, length in zip(self.ids, self.tfs, self.lengths):
            score = 0.0
            for term in terms:
                f = tf.get(term)
                if not f:
                    continue
                score += self.idf[term] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self.avg or 1)))
            out.append((score, doc_id))
        return out

    def top(self, query: str, k: int, exclude: set[str] = frozenset()) -> list[tuple[str, float]]:
        ranked = sorted(((-s, d) for s, d in self.scores(query) if d not in exclude and s > 0))
        return [(d, -s) for s, d in ranked[:k]]
