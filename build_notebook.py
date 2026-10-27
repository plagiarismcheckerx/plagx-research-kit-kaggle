"""Builds plagx-research-kit.ipynb from the cells below. Run: python build_notebook.py"""
import json
from pathlib import Path

PCX = "https://plagiarismcheckerx.com/?utm_source=kaggle&utm_medium=notebook&utm_campaign=plagx-research-kit"

cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")})


def code(text):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.strip("\n")})


md(f"""
# Plagx Research Kit: citation and source-log tutorial with academic research templates

*A free academic writing utility by Plagiarism Checker X.*

This notebook shows how to keep a **source log** while you research and turn it into a correct **APA 7** or **MLA 9** reference list. It also checks that every in-text citation in a draft has a matching source, and gives you templates you can download:

1. **Source log** (CSV): one row per source you read
2. **Literature matrix** (CSV): compare sources by method, findings and gaps
3. **Annotated bibliography** (Markdown): built from your log
4. **Research plan** (Markdown): question, scope, search terms and timeline

Everything runs locally in this notebook. All example sources are **made up** for the tutorial, and none of the DOIs are real.

Citations are formatted with [Plagx Cite](https://pypi.org/project/plagx-cite/), an MIT-licensed open-source package with no dependencies.
""")

md("""
## 1. Setup

`plagx-cite` is installed from the attached [plagx-cite-wheel](https://www.kaggle.com/datasets/plagiarismcheckerx/plagx-cite-wheel) dataset, so no internet is needed. Outside Kaggle it is installed from PyPI.
""")

code("""
import glob, subprocess, sys

wheels = glob.glob("/kaggle/input/**/plagx_cite-*.whl", recursive=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-deps", *(wheels[:1] or ["plagx-cite==0.2.1"])])
""")

code("""
import csv
import re
from pathlib import Path

import pandas as pd
from plagx_cite import (format_bibliography, format_reference, cite_in_text,
                        check_references, to_bibtex, __version__)

OUT = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("output")
OUT.mkdir(exist_ok=True)
print("plagx-cite", __version__, "| output folder:", OUT)
""")

md("""
## 2. The source log

Log a source **as soon as you read it**, not when you write the reference list. The columns below are the minimum you need to cite a source and find it again later.

| Column | What to write |
|---|---|
| `id` | Short key you use in your notes, e.g. `smith2020` |
| `type` | `article-journal`, `book`, `chapter` or `webpage` |
| `authors` | `Family, Given; Family, Given` |
| `year`, `title`, `container` | Year, title, and journal/book/site name |
| `volume`, `issue`, `pages`, `publisher`, `doi`, `url`, `accessed` | Whatever applies |
| `notes`, `quote`, `quote_page` | Your summary and any exact quote **with its page number** |

Recording the page number with every quote is the habit that saves the most time later.
""")

code('''
SOURCE_LOG_COLUMNS = ["id", "type", "authors", "year", "title", "container", "volume", "issue",
                      "pages", "publisher", "doi", "url", "accessed", "notes", "quote", "quote_page"]

# Fictional example sources for this tutorial only.
example_log = [
    {"id": "smith2020", "type": "article-journal", "authors": "Smith, John Allen; Lee, Kate", "year": "2020",
     "title": "Feedback timing and revision quality in undergraduate essays", "container": "Journal of Academic Writing",
     "volume": "12", "issue": "3", "pages": "45-67", "doi": "10.1234/jaw.2020.045",
     "notes": "Early feedback led to more substantive revisions.", "quote": "Students revised structure, not just wording.", "quote_page": "52"},
    {"id": "garcia2018", "type": "book", "authors": "Garcia, Maria", "year": "2018",
     "title": "Writing from sources: A practical guide", "publisher": "Example University Press",
     "notes": "Chapter 4 covers paraphrasing and note-taking."},
    {"id": "okafor2022", "type": "webpage", "authors": "Okafor, Chidi", "year": "2022",
     "title": "Keeping a research log that works", "container": "Example Writing Centre",
     "url": "https://example.org/research-log", "accessed": "2026-10-01",
     "notes": "Practical tips; useful for the methods section."},
    {"id": "smith2020b", "type": "article-journal", "authors": "Smith, John A.; Lee, Kate", "year": "2020",
     "title": "Feedback Timing and Revision Quality in Undergraduate Essays", "container": "Journal of Academic Writing",
     "volume": "12", "issue": "3", "pages": "45-67", "doi": "https://doi.org/10.1234/JAW.2020.045",
     "notes": "Logged twice by mistake. The checker should catch this."},
    {"id": "chen2021", "type": "article-journal", "authors": "Chen, Wei", "year": "",
     "title": "Peer review in large writing courses", "container": "Teaching in Higher Education Review",
     "volume": "7", "pages": "101-118", "notes": "Year still missing. Look it up before submitting."},
]

log = pd.DataFrame(example_log, columns=SOURCE_LOG_COLUMNS).fillna("")
log[["id", "type", "authors", "year", "title"]]
''')

md("""
To use **your own** log, upload a CSV with the same columns as a Kaggle dataset and load it instead:

```python
log = pd.read_csv("/kaggle/input/<your-dataset>/source_log.csv", dtype=str).fillna("")
```
""")

md("""
## 3. Convert the log to CSL-JSON

Plagx Cite works with [CSL-JSON](https://citeproc-js.readthedocs.io/en/latest/csl-json/markup.html), the format Zotero, Mendeley and Crossref export. This function maps each log row to one CSL-JSON reference.
""")

code('''
def parse_authors(value):
    people = []
    for name in filter(None, (part.strip() for part in value.split(";"))):
        family, _, given = name.partition(",")
        people.append({"family": family.strip(), "given": given.strip()} if given else {"literal": family.strip()})
    return people


def row_to_csl(row):
    ref = {"id": row["id"], "type": row["type"] or "article-journal", "title": row["title"]}
    if row["authors"]:
        ref["author"] = parse_authors(row["authors"])
    if row["year"]:
        ref["issued"] = {"date-parts": [[int(row["year"])]]}
    if row["accessed"]:
        ref["accessed"] = {"date-parts": [[int(p) for p in row["accessed"].split("-")]]}
    fields = {"container": "container-title", "volume": "volume", "issue": "issue", "pages": "page",
              "publisher": "publisher", "doi": "DOI", "url": "URL"}
    ref.update({csl: row[col] for col, csl in fields.items() if row[col]})
    return ref


refs = [row_to_csl(row) for row in log.to_dict("records")]
refs[0]
''')

md("""
## 4. Check the log before you write

`check_references` reports **duplicates** (same DOI, or same title and first author) and **missing details** such as a missing year. DOI lookups are off here, so nothing is sent over the network.
""")

code("""
report = check_references(refs)
print(f"{report['errors']} error(s), {report['warnings']} warning(s)")
pd.DataFrame(report["issues"])[["level", "code", "ref", "message"]]
""")

md("""
The checker found that `smith2020b` is the same paper as `smith2020` (different capitalisation and DOI format), and that `chen2021` has no year. Fix the log, then continue:
""")

code("""
log = log[log["id"] != "smith2020b"].reset_index(drop=True)
log.loc[log["id"] == "chen2021", ["year", "notes"]] = ["2021", "Peer review works best with a rubric."]
refs = [row_to_csl(row) for row in log.to_dict("records")]
print(check_references(refs)["issues"] or "No problems found.")
""")

md("""
## 5. Format the reference list and in-text citations
""")

code("""
for style in ("apa", "mla"):
    print(style.upper())
    for entry in format_bibliography(refs, style=style):
        print("  ", entry)
    print()
""")

code("""
by_id = {ref["id"]: ref for ref in refs}
row = log.set_index("id").loc["smith2020"]

print("Parenthetical:", cite_in_text(by_id["smith2020"], page=row["quote_page"]))
print("Narrative:    ", cite_in_text(by_id["smith2020"], narrative=True))
print("MLA:          ", cite_in_text(by_id["smith2020"], style="mla", page=row["quote_page"]))
print()
print(f'Quote ready to paste: "{row["quote"]}" {cite_in_text(by_id["smith2020"], page=row["quote_page"])}')
""")

md("""
## 6. Match a draft against the log

A common mistake is citing a source in the text that never made it into the reference list, or the other way round. This cell finds APA-style citations such as `(Smith & Lee, 2020, p. 52)` or `Garcia (2018)` in a draft and compares them with the log.

It is a simple pattern match for this tutorial and will not catch every citation format.
""")

code('''
draft = """
Early feedback changes how students revise (Smith & Lee, 2020, p. 52). Garcia (2018) recommends
paraphrasing from notes rather than from the source. Several studies support peer review
(Chen, 2021; Patel, 2019).
"""

CITATION = re.compile(r"([A-Z][\\w'-]+)(?: (?:&|and) [A-Z][\\w'-]+| et al\\.)?,? \\(?(\\d{4})")


def cited_keys(text):
    return {(name.lower(), year) for name, year in CITATION.findall(text)}


def logged_keys(refs):
    keys = {}
    for ref in refs:
        family = (ref.get("author") or [{}])[0].get("family", "").lower()
        year = str(ref.get("issued", {}).get("date-parts", [[""]])[0][0])
        keys[(family, year)] = ref["id"]
    return keys


cited, logged = cited_keys(draft), logged_keys(refs)
print("Cited but not in the log:  ", sorted(f"{n.title()} {y}" for n, y in cited - logged.keys()) or "none")
print("In the log but never cited:", sorted(logged[k] for k in logged.keys() - cited) or "none")
''')

md("""
`Patel 2019` is cited but was never logged, so it needs a log entry (or should be removed). `okafor2022` is logged but not cited, which is fine for a working log. Leave it out of the final reference list for APA.
""")

md("""
## 7. Templates you can download

The next cells write the templates to the notebook's **Output** folder (`/kaggle/working`). Download them from the *Output* tab, or click **Copy & Edit** to use this notebook with your own sources.
""")

code("""
# 1. Source log: blank template plus the cleaned example
pd.DataFrame(columns=SOURCE_LOG_COLUMNS).to_csv(OUT / "source_log_template.csv", index=False)
log.to_csv(OUT / "source_log_example.csv", index=False)

# 2. Literature matrix: one row per source, columns for comparing them
matrix_columns = ["id", "citation", "research_question", "method", "sample_or_data",
                  "key_findings", "limitations", "relevance_to_my_question", "themes"]
matrix = pd.DataFrame({"id": log["id"], "citation": [cite_in_text(by_id[i]) for i in log["id"]]},
                      columns=matrix_columns).fillna("")
matrix.to_csv(OUT / "literature_matrix.csv", index=False)

# 3. Citation library in standard formats, for Zotero, Mendeley or LaTeX
import json
(OUT / "references.json").write_text(json.dumps(refs, indent=2), encoding="utf-8")
(OUT / "references.bib").write_text(to_bibtex(refs), encoding="utf-8")
matrix
""")

code('''
def annotated_bibliography(log, refs, style="apa"):
    by_id = {ref["id"]: ref for ref in refs}
    lines = [f"# Annotated bibliography ({style.upper()})", ""]
    for ref in sorted(refs, key=lambda r: format_reference(r, style=style)):
        row = log.set_index("id").loc[ref["id"]]
        lines.append(format_reference(by_id[ref["id"]], style=style, format="markdown"))
        lines.append("")
        lines.append(f"> {row['notes'] or 'Summary: what the source argues, its method, and how you will use it.'}")
        lines.append("")
    return "\\n".join(lines)


(OUT / "annotated_bibliography.md").write_text(annotated_bibliography(log, refs), encoding="utf-8")
print(annotated_bibliography(log, refs))
''')

code('''
research_plan = """# Research plan

## Working title

## Research question
- Main question:
- Sub-questions:

## Scope
- Included (years, regions, populations, source types):
- Excluded:

## Search strategy
| Database or source | Search string | Date searched | Results | Kept |
|---|---|---|---|---|
| | | | | |

## Key terms and synonyms
| Concept | Synonyms and related terms |
|---|---|
| | |

## Timeline
| Milestone | Due date | Done |
|---|---|---|
| Sources collected and logged | | |
| Literature matrix complete | | |
| Outline | | |
| First draft | | |
| Citations checked against source log | | |
| Final draft | | |

## Citation style
APA 7 / MLA 9 (delete one)
"""
(OUT / "research_plan.md").write_text(research_plan, encoding="utf-8")
sorted(p.name for p in OUT.iterdir())
''')

md(f"""
## What this notebook does not do

This notebook formats citations, checks a source log for duplicates and missing details, and provides research templates. It does **not** check for plagiarism or detect AI-generated text.

A free academic writing utility by Plagiarism Checker X. Check complete documents for plagiarism and AI-generated text at [Plagiarism Checker X]({PCX}).

---

**Licence:** code in this notebook is MIT-licensed. Plagx Cite: [PyPI](https://pypi.org/project/plagx-cite/) · [GitHub](https://github.com/plagiarismcheckerx/plagx-cite) · [live demo](https://plagiarismcheckerx.github.io/plagx-cite/)
""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
for i, cell in enumerate(cells):
    cell["id"] = f"cell-{i:02d}"

path = Path(__file__).with_name("plagx-research-kit.ipynb")
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {path} ({len(cells)} cells)")
