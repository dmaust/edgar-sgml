"""Documents read out of a submission, as SEC's site serves them. The
submissions here are made for the tests, in the form the archives of 2026 have:
lines ended by a bare carriage return, a full stop at the start of a line
doubled, binary files encoded as SEC encodes them."""

import binascii
import io
import tarfile

import compare
import documents
import pytest

FILING = "0000064803-26-000300"
JPEG = bytes(range(256)) * 3 + b"\xff\xd9" * 7  # 782 bytes: its last line holds 17
PDF = b"%PDF-1.7\n" + bytes(range(200, 256)) * 5 + b"\n%%EOF\n"
HTML = b"<html>\n<style>\n.note { color: red }\n..two { }\n</style>\n<p>Text</p>\n</html>\n"
XML = b'<?xml version="1.0"?>\n<ownershipDocument>\n<x>1</x>\n</ownershipDocument>\n'


def uuencoded(name: str, body: bytes, padding: bytes = b"!") -> bytes:
    """A file as an archive holds a binary one. The last group of the last line
    is filled out with `padding`, as SEC's is, not with what Python writes."""
    lines = [f"begin 644 {name}".encode()]
    for at in range(0, len(body), 45):
        line = binascii.b2a_uu(body[at : at + 45]).rstrip(b"\n")
        used = 1 + (len(body[at : at + 45]) * 4 + 2) // 3
        lines.append(line[:used] + padding * (len(line) - used))
    return b"\n".join([*lines, b"`", b"end"])


def document(kind: str, sequence: int, name: str | None, text: bytes, described: str = "") -> bytes:
    lines = [b"<DOCUMENT>", f"<TYPE>{kind}".encode(), f"<SEQUENCE>{sequence}".encode()]
    if name:
        lines.append(f"<FILENAME>{name}".encode())
    if described:
        lines.append(f"<DESCRIPTION>{described}".encode())
    return b"\n".join([*lines, b"<TEXT>", text.rstrip(b"\n"), b"</TEXT>", b"</DOCUMENT>"])


def submission(accession: str = FILING, parts: list[bytes] | None = None, cr: bool = True) -> bytes:
    header = [
        "<SUBMISSION>",
        f"<ACCESSION-NUMBER>{accession}",
        "<TYPE>8-K",
        "<FILING-DATE>20261120",
        "<FILER>",
        "<COMPANY-DATA>",
        "<CONFORMED-NAME>SOME COMPANY",
        "<CIK>0000064803",
        "</COMPANY-DATA>",
        "</FILER>",
    ]
    if parts is None:
        parts = [
            document("8-K", 1, "main.htm", HTML, "Current report"),
            document("EX-99", 2, "ex99.pdf", b"<PDF>\n" + uuencoded("ex99.pdf", PDF) + b"\n</PDF>"),
            document("GRAPHIC", 3, "logo.jpg", uuencoded("logo.jpg", JPEG)),
            document("4", 4, "form4.xml", b"<XML>\n" + XML + b"</XML>"),
            document("EX-101.SCH", 5, "x.xsd", b"<XBRL>\n<schema/>\n</XBRL>"),
        ]
    body = b"\n".join(["\n".join(header).encode(), *parts, b"</SUBMISSION>", b""])
    stuffed = b"\n".join(b"." + line if line[:1] == b"." else line for line in body.split(b"\n"))
    return stuffed.replace(b"\n", b"\r") if cr else stuffed


def archive_of(path, members: dict[str, bytes]):
    with tarfile.open(path, "w:gz") as tar:
        for name, body in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            tar.addfile(info, io.BytesIO(body))
    return path


def test_a_doubled_full_stop_is_undone_only_where_the_sender_doubled_them():
    assert documents.unstuffed(b"a\r..b { }\r...\rc. d\r") == b"a\r.b { }\r..\rc. d\r"
    assert documents.unstuffed(b"..first\n..x\n") == b".first\n.x\n"
    # A line that begins with one full stop: this was not sent with them doubled.
    assert documents.unstuffed(b"..a\n.b\n") == b"..a\n.b\n"
    assert documents.unstuffed(b"no such lines\n") == b"no such lines\n"


def test_an_encoded_file_is_decoded_though_pythons_decoder_refuses_its_last_line():
    assert documents.decoded(uuencoded("logo.jpg", JPEG)) == JPEG
    with pytest.raises(binascii.Error):
        binascii.a2b_uu(uuencoded("logo.jpg", JPEG).split(b"\n")[-3])
    # A blank line before it, as in 2001, and lines ended either way.
    assert documents.decoded(b"\n" + uuencoded("a.pdf", PDF).replace(b"\n", b"\r\n")) == PDF
    assert documents.decoded(b"<html>begin 644 is not at the start</html>") is None
    assert documents.decoded(b"begin 644 x\n\x01\x02 not encoded\nend") is None


@pytest.mark.parametrize("cr", [True, False])
def test_a_submissions_documents_are_read_as_secs_site_serves_them(cr):
    accession, found = documents.read(submission(cr=cr))
    assert accession == FILING
    files = {made.name: made.body for made in found}
    assert list(files) == ["main.htm", "ex99.pdf", "logo.jpg", "form4.xml", "x.xsd"]
    # Text as filed: line feeds, and the full stops as the filer wrote them.
    assert files["main.htm"] == HTML
    # Binary files decoded, and out of the tag that wrapped one.
    assert files["logo.jpg"] == JPEG and files["ex99.pdf"] == PDF
    # XML and XBRL out of theirs.
    assert files["form4.xml"] == XML and files["x.xsd"] == b"<schema/>\n"
    first = found[0]
    assert (first.type, first.sequence, first.description) == ("8-K", "1", "Current report")


def test_an_encoded_line_that_begins_with_a_full_stop_is_read():
    """A file whose last line holds 14 bytes begins that line with a full stop,
    which the sender doubles like any other."""
    odd = bytes(range(59))
    sent = submission(parts=[document("GRAPHIC", 1, "odd.gif", uuencoded("odd.gif", odd))])
    assert b"\r.." in sent
    assert documents.read(sent)[1][0].body == odd


def test_what_is_not_a_document_to_write_is_told_apart():
    # Before about 2001 a filing names no files: the document is read, without a name.
    accession, found = documents.read(submission(parts=[document("10-K", 1, None, b"Old text")]))
    assert [(made.name, made.body) for made in found] == [("", b"Old text\n")]
    assert not documents.safe_name("") and not documents.safe_name("../x.htm")
    assert documents.safe_name("a-1_b.htm")
    # A correction can list a document without its text.
    listed = b"<SUBMISSION>\n<DOCUMENT>\n<TYPE>8-K\n<FILENAME>a.htm\n</DOCUMENT>\n"
    assert documents.read(listed) == ("", [])
    # A document that quotes the tag in its text is one document.
    quoting = document("8-K", 1, "q.htm", b"<p>It read: <DOCUMENT> and </DOCUMENT> so.</p>")
    assert len(documents.read(submission(parts=[quoting]))[1]) == 1


def test_documents_are_written_a_folder_a_filing(tmp_path, capsys):
    day = archive_of(
        tmp_path / "20261120.nc.tar.gz",
        {
            f"./{FILING}.nc": submission(),
            "./0000064803-26-000301.nc": submission(
                "0000064803-26-000301", [document("8-K", 1, None, b"No file is named")]
            ),
            f"./{FILING}.corr01": submission(parts=[document("8-K", 1, "main.htm", b"Corrected")]),
        },
    )
    out = tmp_path / "out"
    assert documents.main([str(out), str(day)]) == 0
    assert (out / FILING / "logo.jpg").read_bytes() == JPEG
    assert (out / FILING / "main.htm").read_bytes() == HTML
    assert (out / f"{FILING}.corr01" / "main.htm").read_bytes() == b"Corrected\n"
    assert not (out / "0000064803-26-000301").exists()
    assert (
        "3 filings, 6 documents written, 1 without a file name left out" in capsys.readouterr().err
    )

    assert documents.main([str(tmp_path / "none"), str(day), "--list", "--only", FILING]) == 0
    listed = capsys.readouterr().out.splitlines()
    assert f"{FILING}\tGRAPHIC\tlogo.jpg\t{len(JPEG)}" in listed and len(listed) == 6
    assert not (tmp_path / "none").exists()


def test_a_document_is_compared_with_secs_copy_for_what_is_the_filings():
    assert compare.compared(HTML, HTML) == "identical"
    script = b'<script type="text/javascript" src="/include/x.js"></script>'
    adds = "identical but for what SEC's site adds"
    assert compare.compared(HTML, HTML.replace(b"<p>", script + b"<p>")) == adds
    wrapped = b"<DOCUMENT>\n<TYPE>EX-99\n<TEXT>\n" + XML + b"</TEXT>\n</DOCUMENT>\n"
    assert compare.compared(XML, wrapped) == adds
    blanks = "identical but for blanks at line ends"
    assert compare.compared(b"a  \nb\n", b"a\nb\n") == blanks
    assert compare.compared(b"a b\n", b"a\nb\n") == "identical but for white space"
    assert compare.compared(b"a\n", b"b\n") == "DIFFERENT"


def test_a_few_documents_of_each_kind_are_compared(tmp_path):
    day = archive_of(
        tmp_path / "20261120.nc.tar.gz",
        {
            f"./{FILING}.nc": submission(),
            "./0000064803-26-000302.nc": submission("0000064803-26-000302"),
            f"./{FILING}.corr01": submission(),
        },
    )
    folder = "https://www.sec.gov/Archives/edgar/data/64803/000006480326000300/"
    theirs = {folder + "main.htm": HTML, folder + "logo.jpg": JPEG + b"!", folder + "x.xsd": None}
    asked, said = [], []

    def fetch(address):
        asked.append(address)
        return theirs.get(address, b"something else")

    counts = compare.compare([day], fetch, each=1, say=said.append)
    # One of each kind, from the first filing that has it, and never a correction.
    assert sorted(asked) == sorted(
        folder + name for name in ("main.htm", "ex99.pdf", "logo.jpg", "form4.xml", "x.xsd")
    )
    assert counts[".htm", "identical"] == 1 and counts[".xsd", "not at SEC"] == 1
    assert counts[".jpg", "DIFFERENT"] == 1 and sum(counts.values()) == 5
    assert f"20261120.nc.tar.gz {FILING} logo.jpg: DIFFERENT" in said
    assert any(line.startswith(".htm") and "identical" in line for line in compare.report(counts))
