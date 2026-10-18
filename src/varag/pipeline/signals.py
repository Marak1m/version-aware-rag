"""Static usage extraction over Python code: the AST core of the signal extractor.

Finds every use of a version-exclusive symbol, keyword argument, argument value or config key,
resolved against the inventory diff. Used by validation step 4, the full extractor
(``pipeline/extract.py``, which adds pins, named versions, errors, migration messages and
weights) and the blend guard (M6).

Resolution, in the order the handoff lists it:
- import aliases (``import numpy as np``, ``from pydantic import Field``);
- attribute chains on resolved aliases (``np.trapz``, ``pd.DataFrame.map``);
- receivers assigned from library constructors and readers (``df = pd.read_csv(...)``),
  annotated parameters (``df: pd.DataFrame``), and local classes that subclass a resolved
  base (``class User(BaseModel)``);
- name heuristics (``df``, ``arr``, ``model``), flagged ``heuristic``;
- bare method names on unresolved receivers through ``method_name_index``, where generic
  names (``append``, ``map``) abstain.

Keyword arguments are bound against the per-version signatures: ``read_csv(squeeze=True)`` is a
usage of ``pandas.read_csv(squeeze)``. Positional arguments are bound to a parameter name when
both versions put that parameter at the same position (user decision 2026-10-18). A literal
argument that a confirmed value rule lists for the callable and parameter is a ``value`` usage of
the rule's side (``resample("M")``). pydantic config keys are read from ``class Config`` bodies,
``model_config`` dict literals and ``ConfigDict(...)`` calls as ``pydantic.Config.<key>``.
Calls whose callee accepts ``**kwargs`` or sits in ``shared_unknown`` abstain. Usage inside a
version guard (``try/except ImportError``, ``hasattr``, ``__version__``) is recorded as guarded
and excluded from the side sets.
"""

from __future__ import annotations

import ast
import textwrap
from dataclasses import dataclass, field

from varag.inventory.diff import BUCKETS, bucket_of
from varag.pipeline.values import POSITIONAL_KINDS, match_value, value_index, value_symbol

SIDE_OF_BUCKET = {"old_only": "old", "new_only": "new", "deprecated_in_new": "deprecated_in_new"}
GUARD_EXCEPTIONS = {"ImportError", "AttributeError", "ModuleNotFoundError"}
MODEL_BASES = ("pydantic.BaseModel", "pydantic.BaseSettings", "pydantic.main.BaseModel")
MODEL_BASE_NAMES = {"BaseModel", "BaseSettings"}

# pandas accessor members are inventoried under the accessor class that defines them. `.dt`
# resolves to one of three classes depending on the dtype, which static analysis cannot see.
ACCESSORS = {
    "str": ("pandas.StringMethods",),
    "cat": ("pandas.CategoricalAccessor",),
    "dt": ("pandas.DatetimeProperties", "pandas.TimedeltaProperties", "pandas.PeriodProperties"),
}
ACCESSOR_HOSTS = ("pandas.Series", "pandas.Index", "pandas.DatetimeIndex", "pandas.DataFrame")

READER_TYPES: dict[str, dict[str, str]] = {
    "pandas": {
        **{f"pandas.{r}": "pandas.DataFrame" for r in (
            "read_csv", "read_table", "read_excel", "read_json", "read_parquet", "read_sql", "read_pickle",
            "read_html", "read_feather", "concat", "merge", "get_dummies", "pivot_table", "crosstab", "DataFrame",
        )},
        "pandas.Series": "pandas.Series",
        "pandas.Index": "pandas.Index",
        "pandas.DatetimeIndex": "pandas.DatetimeIndex",
        "pandas.date_range": "pandas.DatetimeIndex",
        "pandas.to_datetime": "pandas.DatetimeIndex",
        "pandas.DataFrame.set_index": "pandas.DataFrame",
        "pandas.DataFrame.resample": "pandas.Resampler",
        "pandas.Series.resample": "pandas.Resampler",
        "pandas.DataFrame.groupby": "pandas.DataFrameGroupBy",
        "pandas.Series.groupby": "pandas.SeriesGroupBy",
        "pandas.DataFrame.rolling": "pandas.Rolling",
    },
    "numpy": {f"numpy.{r}": "numpy.ndarray" for r in (
        "array", "asarray", "asanyarray", "zeros", "ones", "empty", "full", "arange", "linspace", "logspace",
        "eye", "identity", "zeros_like", "ones_like", "empty_like", "full_like", "fromiter", "frombuffer",
        "loadtxt", "genfromtxt", "concatenate", "stack", "vstack", "hstack", "cumsum", "diff", "sort", "unique",
    )},
    "pydantic": {},
}

NAME_HINTS: dict[str, dict[str, str]] = {
    "pandas": {"df": "pandas.DataFrame", "frame": "pandas.DataFrame", "data": "pandas.DataFrame",
               "s": "pandas.Series", "ser": "pandas.Series", "series": "pandas.Series",
               "idx": "pandas.Index", "index": "pandas.Index"},
    "numpy": {"arr": "numpy.ndarray", "a": "numpy.ndarray", "array": "numpy.ndarray", "values": "numpy.ndarray",
              "x": "numpy.ndarray", "y": "numpy.ndarray", "data": "numpy.ndarray"},
    "pydantic": {"model": "pydantic.BaseModel", "m": "pydantic.BaseModel", "obj": "pydantic.BaseModel",
                 "instance": "pydantic.BaseModel", "user": "pydantic.BaseModel", "item": "pydantic.BaseModel"},
}


@dataclass(frozen=True)
class Usage:
    symbol: str
    side: str            # old | new | deprecated_in_new
    kind: str            # symbol | keyword | value | config_key | method | import
    line: int
    resolution: str      # resolved | heuristic | name_index
    guarded: bool = False
    uncertain: bool = False     # keyword declared on one side only, but the other side's callee takes **kwargs
    corroborated: bool = False  # a rule set under data/rules/ lists this symbol (rename, removal or deprecation)
    col: int = 0
    end_line: int = 0


@dataclass
class StaticUsages:
    parsed: bool = True
    usages: list[Usage] = field(default_factory=list)
    abstained: list[dict] = field(default_factory=list)

    def _side(self, side: str, include_guarded: bool = False) -> set[str]:
        return {u.symbol for u in self.usages if u.side == side and (include_guarded or not u.guarded)}

    @property
    def old(self) -> set[str]:
        return self._side("old")

    @property
    def new(self) -> set[str]:
        return self._side("new")

    @property
    def deprecated_in_new(self) -> set[str]:
        return self._side("deprecated_in_new")

    @property
    def guarded(self) -> set[str]:
        return {u.symbol for u in self.usages if u.guarded}

    def to_dict(self) -> dict:
        return {
            "parsed": self.parsed,
            "old": sorted(self.old),
            "new": sorted(self.new),
            "deprecated_in_new": sorted(self.deprecated_in_new),
            "guarded": sorted(self.guarded),
            "abstained": self.abstained,
            "usages": [u.__dict__ for u in self.usages],
        }


def parse_code(code: str) -> ast.AST | None:
    for candidate in (code, textwrap.dedent(code)):
        try:
            return ast.parse(candidate)
        except (SyntaxError, ValueError, RecursionError):
            continue
    return None


def _summary(diff: dict, symbol: str) -> dict | None:
    for bucket in BUCKETS:
        if symbol in diff[bucket]:
            return diff[bucket][symbol]
    return None


def _literal(node: ast.AST) -> tuple[bool, object]:
    """(is a literal we match values against, the value): strings and None only."""
    if isinstance(node, ast.Constant) and (isinstance(node.value, str) or node.value is None):
        return True, node.value
    return False, None


class _Extractor(ast.NodeVisitor):
    def __init__(self, diff: dict, values: dict | None = None):
        self.diff = diff
        self.library = diff["library"]
        self.values = values if values is not None else value_index(self.library)
        self.aliases: dict[str, str] = {}
        self.var_types: dict[str, tuple[str, str]] = {}
        self.class_bases: dict[str, str] = {}
        self.guard_depth = 0
        self.result = StaticUsages()
        self._seen: set[tuple] = set()

    # --- recording -----------------------------------------------------------

    def record(self, symbol: str, kind: str, node: ast.AST | int, resolution: str, uncertain: bool = False,
               side: str | None = None) -> None:
        if side is None:
            bucket = bucket_of(self.diff, symbol)
            side = SIDE_OF_BUCKET.get(bucket or "")
        if side is None:
            return
        key = (symbol, kind, self.guard_depth > 0)
        if key in self._seen:
            return
        self._seen.add(key)
        line = node if isinstance(node, int) else getattr(node, "lineno", 0)
        col = 0 if isinstance(node, int) else getattr(node, "col_offset", 0)
        end = line if isinstance(node, int) else (getattr(node, "end_lineno", None) or line)
        self.result.usages.append(Usage(
            symbol, side, kind, line, resolution, guarded=self.guard_depth > 0, uncertain=uncertain,
            corroborated=symbol in self.diff.get("rule_listed", {}), col=col, end_line=end,
        ))

    def canonical(self, symbol: str, line: int) -> str | None:
        """Map ``pandas.Series.str.contains`` to the accessor class that defines it. For ``.dt``
        the dtype picks the class: when the candidate classes disagree on the bucket, abstain."""
        if self.library != "pandas":
            return symbol
        for accessor, classes in ACCESSORS.items():
            marker = f".{accessor}."
            idx = symbol.find(marker)
            if idx < 0 or symbol[:idx] not in ACCESSOR_HOSTS:
                continue
            member = symbol[idx + len(marker):]
            candidates = [f"{cls}.{member}" for cls in classes]
            existing = [(c, bucket_of(self.diff, c)) for c in candidates if bucket_of(self.diff, c)]
            if not existing:
                return candidates[0]
            if len({b for _, b in existing}) == 1:
                return existing[0][0]
            self.abstain(symbol, line, "accessor member differs by dtype: " + ", ".join(f"{c}={b}" for c, b in existing))
            return None
        return symbol

    def abstain(self, name: str, line: int, reason: str) -> None:
        self.result.abstained.append({"name": name, "line": line, "reason": reason})

    # --- resolution ------------------------------------------------------------

    def resolve_name(self, name: str) -> tuple[str | None, str]:
        if name in self.aliases:
            return self.aliases[name], "resolved"
        if name in self.var_types:
            return self.var_types[name]
        if name in self.class_bases:
            return self.class_bases[name], "resolved"
        hint = NAME_HINTS.get(self.library, {}).get(name)
        if hint:
            return hint, "heuristic"
        return None, "unresolved"

    def resolve_chain(self, node: ast.AST) -> tuple[str | None, str]:
        outer: list[str] = []      # attributes applied after a subscript, e.g. df["a"].dt.week
        cur = node
        while isinstance(cur, ast.Attribute):
            outer.append(cur.attr)
            cur = cur.value
        inner: list[str] = []      # attributes before the subscript
        subscripted = isinstance(cur, ast.Subscript)
        if subscripted:
            cur = cur.value
            while isinstance(cur, ast.Attribute):
                inner.append(cur.attr)
                cur = cur.value
        if isinstance(cur, ast.Name):
            base, resolution = self.resolve_name(cur.id)
        elif isinstance(cur, ast.Call):
            base, resolution = self.call_result_type(cur)
        else:
            return None, "unresolved"
        if base is None:
            return None, "unresolved"
        receiver = ".".join([base, *reversed(inner)])
        if subscripted and receiver == "pandas.DataFrame":
            receiver = "pandas.Series"     # a column of a DataFrame is a Series
        return ".".join([receiver, *reversed(outer)]), resolution

    def call_result_type(self, call: ast.Call) -> tuple[str | None, str]:
        symbol, resolution = self.resolve_chain(call.func)
        if symbol is None:
            return None, "unresolved"
        readers = READER_TYPES.get(self.library, {})
        if symbol in readers:
            return readers[symbol], resolution
        summary = _summary(self.diff, symbol)
        if summary and summary.get("kind") == "class":
            return symbol, resolution
        return None, "unresolved"

    # --- imports ---------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.asname:
                self.aliases[alias.asname] = alias.name
            else:
                top = alias.name.split(".")[0]
                self.aliases[top] = top
            self.record(alias.name, "import", node, "resolved")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not node.module or node.level:
            return
        for alias in node.names:
            if alias.name == "*":
                continue
            symbol = f"{node.module}.{alias.name}"
            self.aliases[alias.asname or alias.name] = symbol
            self.record(symbol, "import", node, "resolved")

    # --- bindings --------------------------------------------------------------

    def _bind_annotation(self, name: str, annotation: ast.AST | None) -> None:
        if annotation is None:
            return
        symbol, resolution = self.resolve_chain(annotation)
        if symbol:
            self.var_types[name] = (symbol, resolution)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
            self._bind_annotation(arg.arg, arg.annotation)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        model_resolution: str | None = None
        for base in node.bases:
            symbol, _ = self.resolve_chain(base)
            if symbol:
                self.class_bases[node.name] = symbol
                self.record(symbol, "symbol", node, "resolved")
                if symbol in MODEL_BASES or self.class_bases.get(symbol.rsplit(".", 1)[-1]) in MODEL_BASES:
                    model_resolution = "resolved"
            elif isinstance(base, ast.Name) and base.id in MODEL_BASE_NAMES:
                model_resolution = model_resolution or "heuristic"     # a BaseModel base that was not imported here
        if model_resolution and self.library == "pydantic":
            self.config_keys(node, model_resolution)
        self.generic_visit(node)

    def config_keys(self, model: ast.ClassDef, resolution: str) -> None:
        """pydantic config keys in a model body (D-f): ``class Config`` assignments, a ``model_config``
        dict literal, or ``model_config = ConfigDict(...)`` keywords, each as ``pydantic.Config.<key>``."""
        for stmt in model.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == "Config":
                for inner in stmt.body:
                    if isinstance(inner, ast.Assign):
                        for target in inner.targets:
                            if isinstance(target, ast.Name):
                                self.record(f"pydantic.Config.{target.id}", "config_key", inner, resolution)
            elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                if not any(isinstance(t, ast.Name) and t.id == "model_config" for t in targets):
                    continue
                value = stmt.value
                if isinstance(value, ast.Dict):
                    for key in value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            self.record(f"pydantic.Config.{key.value}", "config_key", key, resolution)
                elif isinstance(value, ast.Call):
                    for kw in value.keywords:
                        if kw.arg:
                            self.record(f"pydantic.Config.{kw.arg}", "config_key", kw, resolution)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self._bind_annotation(node.target.id, node.annotation)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        value_type: tuple[str | None, str] = (None, "unresolved")
        if isinstance(node.value, ast.Call):
            value_type = self.call_result_type(node.value)
        elif isinstance(node.value, ast.Name):
            value_type = self.var_types.get(node.value.id, (None, "unresolved"))
        for target in node.targets:
            if isinstance(target, ast.Name):
                if value_type[0]:
                    self.var_types[target.id] = (value_type[0], value_type[1])
                else:
                    self.var_types.pop(target.id, None)
        self.generic_visit(node)

    # --- version guards ----------------------------------------------------------

    def visit_Try(self, node: ast.Try) -> None:
        caught = set()
        for handler in node.handlers:
            for name in ast.walk(handler.type) if handler.type else []:
                if isinstance(name, ast.Name):
                    caught.add(name.id)
                elif isinstance(name, ast.Attribute):
                    caught.add(name.attr)
        if caught & GUARD_EXCEPTIONS:
            self.guard_depth += 1
            self.generic_visit(node)
            self.guard_depth -= 1
        else:
            self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        test_src = ast.dump(node.test)
        if "hasattr" in test_src or "__version__" in test_src or "'version'" in test_src.lower():
            self.guard_depth += 1
            for child in [*node.body, *node.orelse]:
                self.visit(child)
            self.guard_depth -= 1
        else:
            self.generic_visit(node)

    # --- usages ----------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        symbol, resolution = self.resolve_chain(node.func)
        if symbol:
            symbol = self.canonical(symbol, node.lineno)
        if symbol:
            self.record(symbol, "symbol", node, resolution)
            self.bind_keywords(symbol, node, resolution)
            self.bind_positionals(symbol, node, resolution)
            if symbol == "pydantic.ConfigDict":
                for kw in node.keywords:
                    if kw.arg:
                        self.record(f"pydantic.Config.{kw.arg}", "config_key", kw, resolution)
        elif isinstance(node.func, ast.Attribute) and resolution == "unresolved":
            self.method_fallback(node.func.attr, node.lineno)
            if node.keywords:
                self.abstain(f"{node.func.attr}(...)", node.lineno, "keywords on unresolved receiver")
        # Visit the receiver expression and the arguments, not the attribute itself.
        func = node.func
        while isinstance(func, ast.Attribute):
            func = func.value
        if isinstance(func, (ast.Call, ast.Subscript)):
            self.visit(func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            self.visit(kw.value)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        symbol, resolution = self.resolve_chain(node)
        if symbol:
            symbol = self.canonical(symbol, node.lineno)
        if symbol:
            self.record(symbol, "symbol", node, resolution)
        inner = node.value
        while isinstance(inner, ast.Attribute):
            inner = inner.value
        if isinstance(inner, (ast.Call, ast.Subscript)):
            self.visit(inner)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load) and node.id in self.aliases:
            self.record(self.aliases[node.id], "symbol", node, "resolved")

    def value_usage(self, symbol: str, param: str, node: ast.AST, resolution: str) -> None:
        """A literal argument that a confirmed value rule lists for this callable and parameter."""
        is_literal, value = _literal(node)
        if not is_literal:
            return
        rule = match_value(self.values, symbol, param, value)
        if rule:
            self.record(value_symbol(symbol, param, value), "value", node, resolution, side=rule["side"])

    def bind_keywords(self, symbol: str, call: ast.Call, resolution: str) -> None:
        """Bind each keyword against the per-version signatures (handoff L3).

        A keyword declared on exactly one side is a usage of that side. When the other side's
        callee accepts **kwargs the call might still run there: the diff keeps such a keyword
        exclusive only when data/rules or an execution probe confirms it (the usage is then
        ``uncertain`` and ``corroborated``, a full exclusive usage); an unconfirmed one is
        shared_unknown and abstains, weight 0 (user decision 2026-10-15). Calls that forward
        **kwargs, and callees in shared_unknown, abstain outright. A keyword's literal value is
        matched against the value rules whatever the keyword's own bucket."""
        if not call.keywords:
            return
        summary = _summary(self.diff, symbol) or {}
        bucket = bucket_of(self.diff, symbol)
        # Value rules are confirmed by execution, so a keyword's literal counts even when the
        # callee's signature could not be read (numpy.array is shared_unknown on 1.26).
        for kw in call.keywords:
            if kw.arg:
                self.value_usage(symbol, kw.arg, kw.value, resolution)
        if bucket in ("old_only", "new_only"):
            return                      # the callable itself is the evidence; its keywords add nothing
        splat = any(kw.arg is None for kw in call.keywords)
        if bucket == "shared_unknown" or splat:
            reason = "callee in shared_unknown" if bucket == "shared_unknown" else "call forwards **kwargs"
            for kw in call.keywords:
                self.abstain(f"{symbol}({kw.arg or '**'})", call.lineno, reason)
            return
        var_kwargs = {"new": bool(summary.get("accepts_var_kwargs")),
                      "old": bool((summary.get("old") or summary).get("accepts_var_kwargs"))}
        for kw in call.keywords:
            param = f"{symbol}({kw.arg})"
            if bucket_of(self.diff, param) == "shared_unknown":
                self.abstain(param, call.lineno, "keyword not confirmed on both sides")
                continue
            side = SIDE_OF_BUCKET.get(bucket_of(self.diff, param) or "")
            other = {"old": "new", "new": "old"}.get(side or "", "new")
            self.record(param, "keyword", kw, resolution, uncertain=bool(side and var_kwargs[other]))

    def positional_names(self, symbol: str, params: list[str]) -> list[str]:
        """The parameter names a positional argument can bind to, in order. Parameters whose kind
        is unknown (a diff built before param_kind existed) are taken as positional-or-keyword."""
        out = []
        for name in params:
            entry = _summary(self.diff, f"{symbol}({name})") or {}
            kind = entry.get("param_kind")
            if kind is None or kind in POSITIONAL_KINDS:
                out.append(name)
            else:
                break
        return out

    def bind_positionals(self, symbol: str, call: ast.Call, resolution: str) -> None:
        """Bind positional literals to a parameter name when both versions put that parameter at
        the same position (user decision 2026-10-18); skip when the positions differ or the
        argument falls into *args. Only value rules apply to a bound position."""
        if not call.args or not self.values:
            return
        summary = _summary(self.diff, symbol) or {}
        if bucket_of(self.diff, symbol) == "shared_unknown" or not summary.get("params"):
            return
        new_names = self.positional_names(symbol, summary.get("params") or [])
        old_names = self.positional_names(symbol, (summary.get("old") or summary).get("params") or summary.get("params") or [])
        for index, arg in enumerate(call.args):
            if isinstance(arg, ast.Starred):
                break
            if index >= len(new_names) or index >= len(old_names):
                break                                   # *args, or more arguments than parameters
            if new_names[index] != old_names[index]:
                continue                                # the positions differ between versions
            self.value_usage(symbol, new_names[index], arg, resolution)

    def method_fallback(self, name: str, line: int) -> None:
        index = self.diff.get("method_name_index", {}).get(name)
        if not index:
            return
        if index.get("generic"):
            self.abstain(name, line, "generic method name on unresolved receiver")
            return
        has_old, has_new = bool(index.get("old")), bool(index.get("new"))
        if has_old and not has_new:
            self.record(f"{index['old'][0]}.{name}", "method", line, "name_index")
        elif has_new and not has_old:
            self.record(f"{index['new'][0]}.{name}", "method", line, "name_index")


def static_usages(code: str, diff: dict, values: dict | None = None) -> StaticUsages:
    tree = parse_code(code)
    if tree is None:
        return StaticUsages(parsed=False)
    extractor = _Extractor(diff, values)
    extractor.visit(tree)
    return extractor.result
