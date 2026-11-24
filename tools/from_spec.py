"""Take the machine-readable parts out of SEC's PDS Technical Specification.

    python tools/from_spec.py

reads sec/pds_dissemination_spec.pdf (with poppler's `pdftotext`) and writes

    sec/dtd-as-printed.txt   the SGML declaration and DTD of section 3.4, as
                             printed: only the page numbers are taken out
    sec/tags.json            the tag definitions of section 3.3, one record a
                             definition, in the spec's order

Neither is edited by hand, so that both can be made again from a newer edition
of the specification and compared.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SEC = Path(__file__).resolve().parent.parent / "sec"
FIELDS = {
    "DATA ELEMENT": "element",
    "TAG": "tag",
    "DESCRIPTION": "description",
    "LENGTH": "length",
    "END TAG": "end_tag",
    "CHARACTERISTIC": "characteristic",
    "LIMITS": "limits",
    "FORMAT": "format",
}
# A field's label. Most stand at the start of a line; a few follow another
# field's value on the same line ("Alpha-Numeric LIMITS: NA").
_LABEL = re.compile(
    r"(?<![A-Za-z<-])(DATA ELEMENT|END\s+TAG|TAG|DESCRIPTION|LENGTH|CHARACTERISTICS?|LIMITS|FORMAT)"
    r"\s*:\s*"
)
_PAGE_NUMBER = re.compile(r"^\s*\d{1,3}\s*$")
_HEADING = re.compile(r"^\s*\d\.\d(\.\d)?\s+\S")


def text_of(pdf: Path) -> list[str]:
    run = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, check=True)
    return run.stdout.decode("utf-8").replace("\f", "\n").split("\n")


def printed_dtd(lines: list[str]) -> str:
    """Section 3.4 from the SGML declaration's first line to the line that
    closes the document type declaration."""
    start = next(i for i, line in enumerate(lines) if line.strip().startswith("<!SGML"))
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == "]>")
    kept = [line.rstrip() for line in lines[start : end + 1] if not _PAGE_NUMBER.match(line)]
    return "\n".join(kept) + "\n"


def definitions(lines: list[str]) -> list[dict[str, str]]:
    """The tag definitions of section 3.3, each as the spec gives it."""
    start = next(
        i
        for i, line in enumerate(lines)
        if re.match(r"^\s*3\.3\.1\s+Submission Header Tags", line)
        and i > 500  # past the table of contents
    )
    end = next(i for i, line in enumerate(lines) if line.strip().startswith("<!SGML"))
    records: list[dict[str, str]] = []
    part = "submission header"
    field = None
    for line in lines[start:end]:
        if _PAGE_NUMBER.match(line) or not line.strip():
            continue
        if _HEADING.match(line):
            if "Document Header and Text Tags" in line:
                part = "document"
            field = None
            continue
        at = 0
        for label in _LABEL.finditer(line):
            before = line[at : label.start()].strip()
            if before and field and records:
                records[-1][field] = (records[-1][field] + " " + before).strip()
            said = re.sub(r"\s+", " ", label.group(1))
            name = FIELDS["CHARACTERISTIC" if said == "CHARACTERISTICS" else said]
            if name == "element":
                records.append({"part": part})
            field = name if records else None
            if field:
                records[-1][field] = ""
            at = label.end()
        rest = line[at:].strip()
        if rest and field and records:
            records[-1][field] = (records[-1][field] + " " + rest).strip()
    for record in records:
        for name, value in record.items():
            record[name] = re.sub(r"\s+", " ", value)
    return records


def main() -> int:
    lines = text_of(SEC / "pds_dissemination_spec.pdf")
    (SEC / "dtd-as-printed.txt").write_text(printed_dtd(lines), encoding="utf-8")
    records = definitions(lines)
    (SEC / "tags.json").write_text(json.dumps(records, indent=1) + "\n", encoding="utf-8")
    print(
        f"{len(records)} tag definitions; the printed DTD is "
        f"{len((SEC / 'dtd-as-printed.txt').read_text().splitlines())} lines"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
