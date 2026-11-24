"""The DTD against real headers, and against headers made wrong on purpose."""

import re

import pytest
from conftest import CATALOG, FIXTURES, ROOT, archive_fixtures, sec_fixtures
from headers import header

# The least a submission may hold.
MINIMAL = """<SUBMISSION>
<ACCESSION-NUMBER>0000000000-26-000001
<TYPE>8-K
<PUBLIC-DOCUMENT-COUNT>1
<FILING-DATE>20260102
<FILER>
<COMPANY-DATA>
<CONFORMED-NAME>EXAMPLE CORP
<CIK>0000000000
</COMPANY-DATA>
<FILING-VALUES>
<FORM-TYPE>8-K
<ACT>34
<FILE-NUMBER>001-00000
<FILM-NUMBER>26000001
</FILING-VALUES>
<BUSINESS-ADDRESS>
<STREET1>1 MAIN ST
<CITY>ANYTOWN
<STATE>NY
<ZIP>10001
<PHONE>2125550100
</BUSINESS-ADDRESS>
<MAIL-ADDRESS>
<STREET1>1 MAIN ST
<CITY>ANYTOWN
<STATE>NY
<ZIP>10001
</MAIL-ADDRESS>
</FILER>
<DOCUMENT>
<TYPE>8-K
<SEQUENCE>1
<FILENAME>example.htm
<DESCRIPTION>FORM 8-K
<TEXT>
</TEXT>
</DOCUMENT>
</SUBMISSION>
"""


def names(paths):
    return [str(path.relative_to(FIXTURES)) for path in paths]


def test_the_minimal_submission_is_valid(parse):
    parsed = parse(MINIMAL)
    assert parsed.errors == []
    assert parsed.elements()[:3] == ["SUBMISSION", "ACCESSION-NUMBER", "TYPE"]


def test_the_dtd_gives_no_warning_of_any_kind(onsgmls):
    import subprocess

    run = subprocess.run(
        [onsgmls, "-s", "-wall", "-c", str(CATALOG)], input=MINIMAL.encode(), capture_output=True
    )
    assert run.stderr == b""
    assert run.returncode == 0


@pytest.mark.parametrize("path", archive_fixtures(), ids=names(archive_fixtures()))
def test_a_header_from_sec_daily_archives_is_valid(parse, path):
    parsed = parse(path.read_bytes())
    assert parsed.errors == []
    assert parsed.elements()[0] == "SUBMISSION"


@pytest.mark.parametrize("path", sec_fixtures(), ids=names(sec_fixtures()))
def test_a_header_file_from_sec_site_is_valid(parse, path):
    parsed = parse(path.read_bytes())
    assert parsed.errors == []
    assert parsed.elements()[0] in ("SEC-HEADER", "IMS-HEADER")
    # The text after the opening tag is the file's own name.
    assert parsed.text_of("HEADER-FILE")[0].startswith(path.name)


def test_the_fixtures_span_the_years_and_both_kinds_of_file():
    days = {path.parent.name[:4] for path in archive_fixtures()}
    assert days == {"1996", "2001", "2005", "2012", "2019", "2026"}
    assert any(".corr" in path.name for path in archive_fixtures())


def test_the_fixtures_have_every_way_of_ending_a_line():
    ends = set()
    for path in archive_fixtures():
        data = path.read_bytes()
        ends.add("crlf" if b"\r\n" in data else "cr" if b"\r" in data else "lf")
    assert {"cr", "lf"} <= ends


def declared_elements() -> set[str]:
    """Every element the DTD declares for headers (not for a document's text)."""
    dtd = (ROOT / "dtd" / "edgar-submission.dtd").read_text()
    dtd = re.sub(r"<!--.*?-->", "", dtd, flags=re.DOTALL)
    head = dtd.split("<!ENTITY % footnotes")[0]
    entities = dict(re.findall(r'<!ENTITY\s+%\s+([\w-]+)\s+"([^"]*)"', head))
    found = set()
    for group in re.findall(r"<!ELEMENT\s+(\([^)]*\)|[\w.-]+)", head):
        for name, text in entities.items():
            group = group.replace(f"%{name};", text)
        found.update(name.upper() for name in re.findall(r"[A-Za-z][\w.-]*", group))
    return found


# Elements the DTD declares because SEC's DTD does, though no header read so
# far holds one.
NOT_IN_THE_FIXTURES = {"SECURITIZER-FILE-NUMBER"}


def test_the_fixtures_show_every_element_the_dtd_declares(parse):
    seen = set()
    for path in [*archive_fixtures(), *sec_fixtures()]:
        seen.update(parse(path.read_bytes()).elements())
    declared = declared_elements()
    assert seen <= declared | {"TEXT"}
    assert declared - seen == NOT_IN_THE_FIXTURES


def test_a_header_reads_the_same_however_its_lines_end(parse):
    with_line_feeds = parse(MINIMAL)
    assert parse(MINIMAL.replace("\n", "\r")).events == with_line_feeds.events
    assert parse(MINIMAL.replace("\n", "\r\n")).events == with_line_feeds.events
    assert with_line_feeds.errors == []


def test_an_ampersand_is_an_ampersand(parse):
    # SEC's own syntax would take "&T" for a reference to an entity named T.
    document = MINIMAL.replace("EXAMPLE CORP", "AT&T INC").replace(
        "FORM 8-K", "MD&A, R&D & C&#298;ON &amp; MORE"
    )
    parsed = parse(document)
    assert parsed.errors == []
    assert parsed.text_of("CONFORMED-NAME") == ["AT&T INC"]
    assert parsed.text_of("DESCRIPTION") == ["MD&A, R&D & C&#298;ON &amp; MORE"]


def test_a_character_outside_ascii_stays_as_sec_wrote_it(parse):
    # SEC writes such a character as a number. SGML could not resolve it (298
    # is no position in the document's character set), so it is left as text.
    document = (FIXTURES / "sec" / "0001140361-21-037265.hdr.sgml").read_bytes()
    parsed = parse(document)
    assert parsed.errors == []
    assert "C&#298;ON Investment Corp" in parsed.text_of("FORMER-CONFORMED-NAME")


def test_a_document_type_declaration_may_be_given(parse):
    declared = '<!DOCTYPE SUBMISSION PUBLIC "-//edgar-sgml//DTD EDGAR Submission Header//EN">\n'
    assert parse(declared + MINIMAL).errors == []


def test_a_description_may_run_over_lines(parse):
    document = MINIMAL.replace("<DESCRIPTION>FORM 8-K", "<DESCRIPTION>FORM 8-K\nOF EXAMPLE CORP")
    parsed = parse(document)
    assert parsed.errors == []
    assert parsed.text_of("DESCRIPTION") == ["FORM 8-K\\nOF EXAMPLE CORP"]


def test_a_whole_submission_is_valid_once_its_text_is_taken_out(parse):
    document = MINIMAL.replace(
        "<TEXT>\n", "<TEXT>\n<html><body><p>R&D costs rose.</p></body></html>\n"
    ).encode()
    assert parse(document).errors != []  # HTML is not what the DTD describes
    assert parse(header(document)).errors == []


# A header made wrong, and what the parser says of it.
WRONG = {
    "no accession number": (
        MINIMAL.replace("<ACCESSION-NUMBER>0000000000-26-000001\n", ""),
        'start tag for "ACCESSION-NUMBER" omitted, but its declaration does not permit this',
    ),
    "the filing date before the type": (
        MINIMAL.replace("<TYPE>8-K\n<PUBLIC-DOCUMENT-COUNT>1\n<FILING-DATE>20260102\n", "").replace(
            "<FILER>", "<FILING-DATE>20260102\n<TYPE>8-K\n<PUBLIC-DOCUMENT-COUNT>1\n<FILER>", 1
        ),
        'start tag for "TYPE" omitted, but its declaration does not permit this',
    ),
    "a tag SEC does not send": (
        MINIMAL.replace("<FILING-DATE>", "<TICKER>EX\n<FILING-DATE>"),
        'element "TICKER" undefined',
    ),
    "a company without a name": (
        MINIMAL.replace("<CONFORMED-NAME>EXAMPLE CORP\n", ""),
        'start tag for "CONFORMED-NAME" omitted, but its declaration does not permit this',
    ),
    "a party without its company": (
        MINIMAL.replace(
            "<COMPANY-DATA>\n<CONFORMED-NAME>EXAMPLE CORP\n<CIK>0000000000\n</COMPANY-DATA>\n", ""
        ),
        'document type does not allow element "FILING-VALUES" here',
    ),
    "a telephone number in the mailing address": (
        MINIMAL.replace("<ZIP>10001\n</MAIL-ADDRESS>", "<ZIP>10001\n<PHONE>1\n</MAIL-ADDRESS>"),
        'document type does not allow element "PHONE" here',
    ),
    "a filer that is never closed": (
        MINIMAL.replace("</FILER>\n", ""),
        'document type does not allow element "DOCUMENT" here',
    ),
    "a document without a sequence number": (
        MINIMAL.replace("<SEQUENCE>1\n", ""),
        'start tag for "SEQUENCE" omitted, but its declaration does not permit this',
    ),
    "no document": (
        MINIMAL.split("<DOCUMENT>")[0] + "</SUBMISSION>\n",
        'end tag for "SUBMISSION" which is not finished',
    ),
    "text where only tags may stand": (
        MINIMAL.replace("<FILER>\n", "<FILER>\nstray words\n"),
        "character data is not allowed here",
    ),
}


@pytest.mark.parametrize("case", WRONG)
def test_a_wrong_header_is_refused(parse, case):
    document, message = WRONG[case]
    assert message in parse(document).errors


def test_the_one_header_of_the_six_days_that_is_not_valid(parse):
    # A filing of 15 March 1996. SEC's own <FLAWED> stands on its tenth
    # document, which has a page break and a page number after its text ends.
    document = (FIXTURES / "invalid" / "19960315-0000025885-96-000006.nc").read_bytes()
    assert b"<FLAWED>\n<TEXT>\n</TEXT>\n<PAGE>\n\n          234\n" in document
    assert parse(document).errors == [
        'document type does not allow element "PAGE" here',
        "character data is not allowed here",
    ]
