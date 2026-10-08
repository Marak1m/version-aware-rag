"""Unit tests for chunk composition, example extraction, pydantic docs parsing and BM25."""

from pathlib import Path

from varag.corpus.bm25 import BM25, tokenize
from varag.corpus.chunks import Parts, compact_signature, deprecation_note, description_from_summary, fit, render, with_example
from varag.corpus.examples import doctest_statements, extract_doctest_example, fenced_blocks, pick_block, run_checks
from varag.corpus.pydantic_docs import first_sentence, mention_pattern, resolve_includes, split_sections

EXAMPLES = """
Examples
>>> df = pd.DataFrame([[1, 2.12], [3.356, 4.567]])
>>> df
       0      1
0  1.000  2.120
>>> pd.read_csv('data.csv')  # doctest: +SKIP
>>> df.applymap(lambda x: len(str(x)))
   0  1
>>> df.applymap(lambda x: x,
...             na_action='ignore')
"""


def test_doctest_statements_drop_output_and_join_continuations():
    statements = doctest_statements(EXAMPLES)
    assert statements[0] == "df = pd.DataFrame([[1, 2.12], [3.356, 4.567]])"
    assert statements[-1] == "df.applymap(lambda x: x,\n            na_action='ignore')"
    assert not any("0  1" in s for s in statements)


def test_example_prefix_skips_skip_lines_and_bare_displays():
    code, met = extract_doctest_example(EXAMPLES, "applymap")
    assert code == "df = pd.DataFrame([[1, 2.12], [3.356, 4.567]])\ndf.applymap(lambda x: len(str(x)))"
    assert met is False


def test_keyword_example_is_preferred_and_reported():
    code, met = extract_doctest_example(EXAMPLES, "applymap", keyword="na_action")
    assert met is True and code.endswith("na_action='ignore')")
    code, met = extract_doctest_example(EXAMPLES, "applymap", keyword="nonexistent")
    assert met is False and code.endswith("len(str(x)))")


def test_example_requires_a_use_within_the_cap():
    assert extract_doctest_example(EXAMPLES, "trapz") == (None, False)
    long = "\n".join(f">>> x{i} = {i}" for i in range(20)) + "\n>>> f(x0)"
    assert extract_doctest_example(long, "f", max_statements=12) == (None, False)


def test_keyword_must_be_passed_to_the_named_call_itself():
    from varag.corpus.examples import passes_keyword

    assert passes_keyword("x: str = Field(..., regex='^a$')", "Field", "regex")
    assert passes_keyword("Field(\n    default=1,\n    regex=r'(a)',\n)", "Field", "regex")
    assert not passes_keyword("x: constr(regex='a') = Field(...)", "Field", "regex")
    assert not passes_keyword("Field(default=constr(regex='a'))", "Field", "regex")
    assert not passes_keyword("Field(regex_mode=1)", "Field", "regex")
    assert not passes_keyword("Field(x == regex)", "Field", "regex")


def test_fenced_blocks_and_pick_block():
    md = "Text\n\n```python {test=\"skip\"}\nfrom pydantic import Field\nx = Field(pattern='a')\n```\n\n    ```py\n    y = Field()\n    ```\n"
    blocks = fenced_blocks(md)
    assert blocks == ["from pydantic import Field\nx = Field(pattern='a')", "y = Field()"]
    assert pick_block(blocks, "Field", "pattern") == (blocks[0], True)
    assert pick_block(blocks[1:], "Field", "pattern") == (blocks[1], False)


def test_examples_naming_urls_are_not_run():
    results = run_checks("numpy_old", "numpy", [("a", "pd.read_csv('https://x/y.csv')")])
    assert results["a"].status == "network"


def test_description_and_deprecation_note_from_docstring():
    summary = ("Apply a function to a :class:`DataFrame` elementwise.\n\nMore text.\n\n"
               ".. deprecated:: 2.1.0\n\n   DataFrame.applymap has been deprecated. Use :meth:`DataFrame.map` instead.\n")
    assert description_from_summary(summary) == "Apply a function to a DataFrame elementwise."
    assert deprecation_note(summary.replace("2.1.0\n\n", "2.1.0\n")) == \
        "Deprecated since 2.1.0: DataFrame.applymap has been deprecated. Use DataFrame.map instead."
    assert deprecation_note("No directive here.") is None


def parts(**kw):
    base = dict(fqn="pandas.DataFrame.map", library="pandas", version="3.0.6", kind="method", title="DataFrame.map",
                signature="(self, func, na_action=None, **kwargs)", description="Apply a function elementwise.",
                deprecation_note="Deprecated since 9.0: gone.")
    base.update(kw)
    return Parts(**base)


def test_render_order_and_flags():
    text = render(parts(example="df.map(str)"))
    lines = text.splitlines()
    assert lines[0] == "[pandas 3.0.6 | api] DataFrame.map"
    assert lines[1:5] == ["pandas.DataFrame.map", "Version: pandas 3.0.6",
                          "Signature: DataFrame.map(self, func, na_action=None, **kwargs)", "Apply a function elementwise."]
    assert lines[5].startswith("Deprecated") and lines[-1] == "df.map(str)"
    untagged = render(parts(), show_version_tags=False, strip_deprecation_notes=True)
    assert "3.0.6" not in untagged and "Deprecated" not in untagged


def test_compact_signature_keeps_named_parameters():
    params = [{"name": f"p{i}", "default": None if i == 0 else "1"} for i in range(10)]
    assert compact_signature(params[:2], True) == "(p0, p1=1, **kwargs)"
    assert compact_signature(params, False, keep={"p9"}, limit=2) == "(p0, p1=1, p9=1, ...)"


def word_count(text):
    return len(text.split())


def test_fit_trims_description_then_signature():
    params = [{"name": f"param_{i}", "default": "None"} for i in range(60)]
    long_sig = "(" + ", ".join(f"param_{i}: 'Annotation[int]' = None" for i in range(60)) + ")"
    composed = fit(parts(signature=long_sig, description=" ".join(["word"] * 80)), word_count, params, False,
                   keep_params={"param_59"}, cap=60)
    assert composed.trims == ["description", "signature_annotations", "signature_params"]
    assert composed.n_tokens <= 60 and "param_59=None" in composed.parts.signature and "..." in composed.parts.signature
    assert with_example(composed, "x " * 100, word_count, cap=60) is None
    assert with_example(fit(parts(), word_count, [], False, set()), "df.map(str)", word_count).parts.example == "df.map(str)"


def test_pydantic_sections_ignore_headings_in_code_and_resolve_includes(tmp_path: Path):
    examples = tmp_path / "docs" / "examples"
    examples.mkdir(parents=True)
    (examples / "schema_main.py").write_text("from pydantic import Field\nx = Field(regex='a')\n", encoding="utf-8")
    md = resolve_includes("# Schema\n\nIntro with `Field`.\n\n## Field customization\n\nUse `regex`.\n\n{!.tmp_examples/schema_main.md!}\n"
                          "```py\n# not a heading\n```\n", tmp_path)
    sections = split_sections("docs/usage/schema.md", md, "sha")
    assert [s.heading for s in sections] == ["Schema", "Field customization"]
    assert sections[1].blocks[0].startswith("from pydantic import Field")
    assert sections[1].blocks[1] == "# not a heading"
    assert mention_pattern("dict").search("call `model.dict(by_alias=True)` here")
    assert not mention_pattern("dict").search("call `model_dict` here")
    assert first_sentence("!!! note\n    x\n\nThe [Field][pydantic.Field] function is used. More.") == "The Field function is used."


def test_bm25_is_deterministic_and_splits_identifiers():
    assert tokenize("np.cumsum running_total DataFrame") == ["np", "cumsum", "running", "total", "data", "frame"]
    index = BM25([("b", "cumulative sum of elements"), ("a", "cumulative sum of elements"), ("c", "matrix inverse")])
    assert [d for d, _ in index.top("cumulative sum", 2)] == ["a", "b"]
    assert [d for d, _ in index.top("cumulative sum", 2, exclude={"a"})] == ["b"]
    assert index.top("unrelated words", 3) == []
