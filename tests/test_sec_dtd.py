"""SEC's own DTD, as far as it goes.

sec/repaired/ holds the DTD of SEC's specification with only what a parser
refuses put right. These tests record what that DTD then makes of real
headers, which is the reason the DTD in dtd/ exists.
"""

import json

import pytest
from conftest import ROOT, archive_fixtures
from test_dtd import MINIMAL

SEC_CATALOG = ROOT / "sec" / "repaired" / "catalog"
DOCTYPE = "<!DOCTYPE SUBMISSION SYSTEM>"


def test_the_repaired_dtd_is_one_a_parser_accepts(parse):
    # No error is about the DTD itself: each is about the document.
    errors = parse(DOCTYPE + MINIMAL, SEC_CATALOG).errors
    assert errors == [
        'element "FILENAME" undefined',
        'end tag for "DOCUMENT" which is not finished',
    ]


def test_it_never_declares_the_file_name_every_document_has(parse):
    without = MINIMAL.replace("<FILENAME>example.htm\n", "")
    # ... and without a file name the document is not finished either, since
    # the DTD requires the element it does not declare.
    assert (
        'end tag for "DOCUMENT" which is not finished'
        in parse(DOCTYPE + without, SEC_CATALOG).errors
    )


def test_it_takes_an_ampersand_for_a_reference(parse):
    document = DOCTYPE + MINIMAL.replace("EXAMPLE CORP", "AT&T INC")
    assert (
        'general entity "T" not defined and no default entity'
        in parse(document, SEC_CATALOG).errors
    )


@pytest.mark.parametrize("path", archive_fixtures(), ids=[p.name for p in archive_fixtures()])
def test_it_accepts_none_of_the_real_headers(parse, path):
    assert parse(DOCTYPE.encode() + path.read_bytes(), SEC_CATALOG).errors != []


# Each fault of the print that sec/repaired/ puts right: how to put it back.
FAULTS = {
    "the standard's name": ("sec.dcl", '<!SGML "ISO 8879:1986"', '<!SGML "ISO 8879-1986"'),
    "two words run together": ("sec.dcl", "SUBDOC   NO", "SUBDOCNO"),
    "a mark of the print": ("sec.dcl", "SCOPE         DOCUMENT\n", "SCOPE         DOCUMENT\nC-1\n"),
    "a quotation mark that closes too soon": (
        "sec.dtd",
        'zip?" >',
        'zip?",\n                 phone? >',
    ),
    "a choice inside a sequence without parentheses": (
        "sec.dtd",
        "(company-data | owner-data),",
        "company-data | owner-data,",
    ),
    "two names declared without parentheses": (
        "sec.dtd",
        "<!ELEMENT (company-data | owner-data) ",
        "<!ELEMENT company-data | owner-data ",
    ),
    "a semicolon after a name": (
        "sec.dtd",
        "(owner-cik, new-series*,",
        "(owner-cik, new-series*;,",
    ),
    "a space in a name": (
        "sec.dtd",
        "<!ELEMENT merger-series-and-classes-contracts ",
        "<!ELEMENT merger-series-and classes-contracts ",
    ),
    "a comment opened with the wrong dash": (
        "sec.dtd",
        "<!-- Series and Classes",
        "<!\u2014Series and Classes",
    ),
    "a name broken across lines": (
        "sec.dtd",
        "                   filing-date,\n",
        "                   filing-\n                   date,\n",
    ),
}


@pytest.mark.parametrize("fault", FAULTS)
def test_each_repair_is_one_the_parser_needs(parse, tmp_path, fault):
    file, repaired, printed = FAULTS[fault]
    for name in ("sec.dcl", "sec.dtd", "catalog"):
        text = (ROOT / "sec" / "repaired" / name).read_text(encoding="utf-8")
        if name == file:
            assert repaired in text
            text = text.replace(repaired, printed, 1)
        (tmp_path / name).write_text(text, encoding="utf-8")
    before = parse(DOCTYPE + MINIMAL, SEC_CATALOG).errors
    after = parse(DOCTYPE + MINIMAL, tmp_path / "catalog").errors
    assert [error for error in after if error not in before] != []


def test_the_printed_dtd_is_kept_as_printed():
    printed = (ROOT / "sec" / "dtd-as-printed.txt").read_text(encoding="utf-8")
    assert printed.lstrip().startswith('<!SGML "ISO 8879-1986"')
    # Three of the faults that stop a parser, still there to be seen.
    assert "2425" in printed
    assert "<!ELEMENT company-data | owner-data" in printed
    assert "merger-series-and classes-contracts" in printed


def test_the_tag_definitions_taken_from_the_specification():
    records = json.loads((ROOT / "sec" / "tags.json").read_text(encoding="utf-8"))
    by_tag = {record["tag"]: record for record in records}
    assert len(records) == 117
    assert by_tag["<ACCESSION-NUMBER>"]["element"] == "ACCESSION NUMBER"
    assert by_tag["<TIMESTAMP>"]["format"] == "YYYYMMDD:HHMMSS"
    assert by_tag["<FILER>"]["end_tag"] == "</FILER>"
