"""Write docs/tags.md: every tag of a header, what it holds and where it stands.

    python tools/tags_table.py

It joins three things, so the page is never written by hand:

    dtd/edgar-submission.dtd   which tags there are and what each may hold
    sec/tags.json              SEC's own description of a tag, where it has one
    docs/census.json           how often real headers have it, and an example
                               (made by tools/census.py --json)

Tags SEC's specification does not describe get the note in NOTES below, which
says only what the headers themselves show.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from census import allowed  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# For tags SEC's specification does not define. Each note was written from the
# headers that hold the tag; "seen" figures come from the census.
NOTES = {
    "SEC-HEADER": "The first tag of a `.hdr.sgml` file on www.sec.gov.",
    "IMS-HEADER": "The first tag of a `.hdr.sgml` file for a filing of EDGAR's first years.",
    "HEADER-FILE": (
        "Not SEC's tag: this DTD's name for the text that follows `<SEC-HEADER>` on its line, "
        "the file's own name and a date. Its tags are never written."
    ),
    "ACCEPTANCE-DATETIME": (
        "When EDGAR accepted the filing, as YYYYMMDDHHMMSS. In `.hdr.sgml` files only."
    ),
    "SROS": (
        "A self-regulatory organization (an exchange) the filing names, one tag each: NYSE, "
        "NASD, AMEX, PSE, ...; NONE where there is none."
    ),
    "FLAWED": "A flag on a document. SEC's specification does not say what it marks.",
    "TRANSFER-ADD": (
        "A flag in a correction that moves a filing from one company to another: it marks the "
        "party the filing now belongs to, and that party's filing values."
    ),
    "TRANSFER-DELETE": (
        "The other half of `<TRANSFER-ADD>`: it marks the party the filing is taken from."
    ),
    "ORGANIZATION-NAME": (
        "The SEC office the company is assigned to, as a number and a name (`02 Finance`, "
        "`07 Trade & Services`). Present and empty for a filer that has none."
    ),
    "LEGAL-ENTITY-IDENTIFIER": "The company's Legal Entity Identifier (LEI), 20 characters.",
    "ADDRESS-IS-A-NON-US-LOCATION": "`YES` on an address outside the United States.",
    "NON-US-STATE-TERRITORY": (
        "For an address outside the United States, a code from EDGAR's table of states and "
        "countries. It stands where `<STATE>` would."
    ),
    "PROVINCE-COUNTRY": (
        "For an address outside the United States, the code of its province or country in "
        "EDGAR's table of states and countries."
    ),
    "PUBLIC-REL-DATE": (
        "The day a filing that was first kept from the public was released, as YYYYMMDD. "
        "Seen beside `<PRIVATE-TO-PUBLIC>`."
    ),
    "SECURITIZER-FILE-NUMBER": "Declared in SEC's DTD and not described in its specification.",
    "RULE": (
        "On a specialized disclosure report (Form SD): the rule it is filed under, with the "
        "items of the form it answers."
    ),
    "RULE-NAME": "The rule a Form SD is filed under, such as `13p-1` or `13q-1`.",
    "ITEM": "One item of Form SD that the report answers, with the period it covers.",
    "ITEM-NUMBER": "The number of the item, such as `1.01` or `2.01`.",
    "ITEM-PERIOD": "The end of the period the item covers, as YYYYMMDD.",
    "RESOURCE-EXT-ISSUER": (
        "On a Form SD; `N` in the header seen. By its name, whether the filer is a resource "
        "extraction issuer."
    ),
    "ABS-SUB-ASSET-CLASS": (
        "A narrower class of the assets behind an asset-backed security. It follows "
        "`<ABS-ASSET-CLASS>`."
    ),
    "CALENDAR-YEAR-ENDING": (
        "A year (`2025`), on a credit rating agency's annual certification (Form NRSRO-CE)."
    ),
    "FILENAME": None,  # SEC describes it (and its DTD forgets to declare it)
}

# Tags whose commonest value names a person: the table shows their form instead.
NO_EXAMPLE = {"MA-I_INDIVIDUAL": "LAST,FIRST,MIDDLE,SUFFIX"}

# Where one tag has several definitions in SEC's specification (the same tag
# in a company's address and in its mailing address), the first is given.


def kinds(dtd: Path) -> dict[str, str]:
    """What each declared element holds: 'tags', 'text' or 'nothing'."""
    text = re.sub(r"<!--.*?-->", "", dtd.read_text(encoding="utf-8"), flags=re.DOTALL)
    entities = dict(re.findall(r'<!ENTITY\s+%\s+([\w.-]+)\s+"([^"]*)"', text))

    def expand(value: str) -> str:
        for _ in range(8):
            value, changed = re.subn(r"%([\w.-]+);", lambda m: entities.get(m.group(1), ""), value)
            if not changed:
                break
        return value

    found = {}
    for names, model in re.findall(
        r"<!ELEMENT\s+(\([^)]*\)|[\w.-]+)\s+[-oO]\s+[-oO]\s+([^>]*)>", text
    ):
        model = expand(model).strip()
        kind = "nothing" if model == "EMPTY" else "text" if model == "(#PCDATA)" else "tags"
        for name in re.findall(r"[A-Za-z][\w.-]*", expand(names)):
            found.setdefault(name.upper(), kind)
    return found


ROOTS = ["SUBMISSION", "SEC-HEADER", "IMS-HEADER"]
HEADER_FILE_ONLY = {"SEC-HEADER", "IMS-HEADER", "HEADER-FILE", "ACCEPTANCE-DATETIME"}
NEVER = {"SECURITIZER-FILE-NUMBER"}  # declared by SEC's DTD, seen nowhere


def order(dtd: Path) -> list[str]:
    """The header's elements in the order the DTD first names them, after the
    three a header can begin with and what only a header file has."""
    text = re.sub(r"<!--.*?-->", "", dtd.read_text(encoding="utf-8"), flags=re.DOTALL)
    text = text.split("<!ENTITY % footnotes")[0]
    seen: list[str] = [*ROOTS, "HEADER-FILE", "ACCEPTANCE-DATETIME"]
    for name in re.findall(r"(?<![%\w.-])([a-z][a-z0-9_.-]*)(?![\w.-]*;)", text):
        upper = name.upper()
        if upper not in seen and upper not in ("O", "EMPTY"):
            seen.append(upper)
    return seen


def where_it_stands(name: str, parents: list[str], inside: dict[str, set[str]]) -> str:
    """The elements a tag may stand in, said briefly: what stands in SUBMISSION
    stands in the two header files' first tags too, and the parties are alike."""
    if name in ROOTS:
        return "(first tag)"
    found = set(parents)
    if "SUBMISSION" in found:
        found -= {"SEC-HEADER", "IMS-HEADER"}
    parties = {child for child in inside["SUBMISSION"] if "COMPANY-DATA" in inside.get(child, ())}
    said = []
    if parties and parties <= found:
        found -= parties
        said.append("each party")
    return ", ".join([*(f"`{parent}`" for parent in sorted(found)), *said])


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render() -> str:
    """The page, from the DTD, SEC's definitions and the count."""
    dtd = ROOT / "dtd" / "edgar-submission.dtd"
    holds = kinds(dtd)
    inside = allowed(dtd)
    parents: dict[str, list[str]] = {}
    for parent, children in inside.items():
        for child in children:
            parents.setdefault(child, []).append(parent)
    census = json.loads((ROOT / "docs" / "census.json").read_text(encoding="utf-8"))
    total = census["headers"]
    described: dict[str, dict] = {}
    for record in json.loads((ROOT / "sec" / "tags.json").read_text(encoding="utf-8")):
        tag = re.sub(r"\s+", "", record["tag"]).strip("<>").split(">")[0].upper()
        described.setdefault(tag, record)

    names = [name for name in order(dtd) if name in holds]
    lines = [
        "# The tags of a header",
        "",
        "Every tag the DTD knows, in the order a header has them. Made by",
        "`tools/tags_table.py`; do not edit it by hand.",
        "",
        "- **Holds**: other tags (it has an end tag), text (it runs to the end of the line and",
        "  has no end tag), or nothing (it is a flag).",
        "- **Inside**: the tags it may stand in. What may stand in `SUBMISSION` may stand in",
        '  `SEC-HEADER` and `IMS-HEADER` too. "Each party" is `FILER`, `FILED-BY`,',
        "  `SUBJECT-COMPANY` and the others that hold a company's data.",
        "- **What it is**: SEC's words from section 3.3 of its specification where it has any.",
        "  A note in *italics* is this repository's, written from the headers that hold the tag.",
        f"- **Seen**: in how many of the {total:,} headers read from six days of SEC's archives",
        "  ("
        + ", ".join(census["by_year"])
        + "), in which of those years, and its commonest value.",
        "",
        "| Tag | Holds | Inside | What it is | Seen |",
        "|---|---|---|---|---|",
    ]
    for name in names:
        record = described.get(name)
        if record:
            what = record["description"]
            extra = [
                f"{label} {record[key]}"
                for key, label in (("format", "Format:"), ("length", "Length:"))
                if record.get(key) and record[key] not in ("NA", "Tag only", "Tag Only")
            ]
            if extra:
                what += " " + "; ".join(extra) + "."
        elif NOTES.get(name):
            what = f"*{NOTES[name]}*"
        else:
            what = "*SEC's specification does not describe it.*"
        seen = census["tags"].get(name)
        if seen:
            years = seen["years"]
            span = years[0] if len(years) == 1 else f"{years[0]} to {years[-1]}"
            example = NO_EXAMPLE.get(name, seen["example"])
            where = f"{seen['headers']:,} ({span})"
            if example and holds[name] == "text":
                where += f"; `{cell(example)}`"
        elif name in HEADER_FILE_ONLY:
            where = "in header files, which the count leaves out"
        elif name in NEVER:
            where = "in no header read"
        else:
            where = "in none of the six days; in header files fetched from SEC"
        within = where_it_stands(name, parents.get(name, []), inside)
        lines.append(f"| `{name}` | {holds[name]} | {within} | {cell(what)} | {where} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    page = render()
    (ROOT / "docs" / "tags.md").write_text(page, encoding="utf-8")
    print(f"{page.count(chr(10)) - 18} tags written to docs/tags.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
