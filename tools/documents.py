"""Read the documents out of an EDGAR submission, as SEC's site serves them.

A submission in SEC's daily archives is a header followed by the filing's
documents, each between <DOCUMENT> and </DOCUMENT>. The document you get by
cutting out what stands between <TEXT> and </TEXT> is not the file SEC serves
from the filing's folder. Five things were done to it on the way into the
archive, and this module undoes them (docs/documents.md has the evidence):

1. A full stop at the start of a line is doubled, as mail does.
2. Lines end with a bare carriage return in the archives of recent years.
3. PDF, XBRL and XML documents are wrapped in a tag of that name.
4. A binary file (an image, a PDF, a spreadsheet, a zip) is uuencoded.
5. The last line of an encoded file is filled out with characters Python's
   own decoder refuses.

    python tools/documents.py OUT_DIR 20261120.nc.tar.gz ...

writes each filing's documents to OUT_DIR/{accession number}/{file name}. With
--list it writes nothing and prints one line a document. As a module:

    read(data)          a submission's accession number and its documents
    unstuffed(data)     the submission with its doubled full stops undone
    decoded(text)       the file a uuencoded text holds

Everything is done with searches for bytes, not regular expressions over the
whole submission: one can be hundreds of megabytes.
"""

import argparse
import binascii
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from headers import members

_FIELD = re.compile(rb"(?:(?<=[\r\n])|\A)<(TYPE|SEQUENCE|FILENAME|DESCRIPTION)>([^\r\n]*)")
_WRAPPER = re.compile(rb"<(PDF|XBRL|XML)>[ \t]*(?:\r\n|\r|\n)")
_ACCESSION = re.compile(rb"<ACCESSION-NUMBER>(\d{10}-\d{2}-\d{6})")
# A name that is safe to use as a file's: SEC's own are letters, digits, full
# stops, hyphens and underscores.
_FILE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def unstuffed(data: bytes) -> bytes:
    """A submission without the full stops its sender doubled.

    The feed sends every line that begins with a full stop with one more in
    front, in every year looked at; SEC's site serves the line as filed. It
    matters for CSS (".note { }" arrives as "..note { }") and for an encoded
    file, where a line of 14 bytes begins with a full stop. A submission with a
    line that begins with a single full stop was not sent so, and is returned
    as it is.
    """
    for newline in (b"\n", b"\r"):
        if data.count(newline + b".") != data.count(newline + b".."):
            return data  # a line begins with one full stop only
    if data[:1] == b"." and data[:2] != b"..":
        return data
    data = data.replace(b"\n..", b"\n.").replace(b"\r..", b"\r.")
    return data[1:] if data[:2] == b".." else data


def unix_lines(text: bytes) -> bytes:
    """Text with its lines ended as SEC's site ends them, by a line feed."""
    return text.replace(b"\r\n", b"\n").replace(b"\r", b"\n") if b"\r" in text else text


def decoded(text: bytes) -> bytes | None:
    """The file a uuencoded text holds, or None if the text is not one.

    The text is "begin 644 name", lines of up to 45 bytes each, and "end". A
    line is cut to the characters its length calls for before it is decoded:
    the last group of a file's last line is filled out with characters that
    binascii.a2b_uu takes for an error ("Trailing garbage").
    """
    if not text[:64].lstrip().startswith(b"begin "):
        return None
    parts = []
    for line in unix_lines(text.lstrip()).split(b"\n")[1:]:
        if line[:3] == b"end":
            break
        if not line:
            continue
        length = (line[0] - 32) & 63
        try:
            parts.append(binascii.a2b_uu(line[: 1 + (length * 4 + 2) // 3]))
        except binascii.Error:
            return None
    return b"".join(parts)


def blocks(data: bytes) -> Iterator[bytes]:
    """What stands between each <DOCUMENT> and </DOCUMENT> that begin a line.

    A document's own text can hold the words "<DOCUMENT>" (a filing that quotes
    another), so only a tag at the start of a line counts.
    """
    at = 0
    while True:
        start = data.find(b"<DOCUMENT>", at)
        if start == -1:
            return
        at = start + 10
        if start and data[start - 1] not in b"\r\n":
            continue
        end = data.find(b"</DOCUMENT>", at)
        while end != -1 and data[end - 1] not in b"\r\n":
            end = data.find(b"</DOCUMENT>", end + 11)
        if end == -1:
            return
        yield data[at:end]
        at = end + 11


@dataclass
class Document:
    type: str  # the header's <TYPE>: "8-K", "EX-99.1", "GRAPHIC", ...
    sequence: str
    name: str  # the file's name; "" where the filing names none (before about 2001)
    description: str
    body: bytes  # as SEC's site serves the file


def document(block: bytes) -> Document | None:
    """One document from what stands between <DOCUMENT> and </DOCUMENT> of a
    submission whose full stops are undone. None if it has no <TEXT>: a
    correction can list a document without its text."""
    opened = block.find(b"<TEXT>")
    if opened == -1:
        return None
    # A document's own lines come first and are few; its text is everything
    # between the first <TEXT> and the last </TEXT>.
    fields = {
        name.decode(): value.strip().decode("latin-1")
        for name, value in _FIELD.findall(block[:opened])
    }
    body = block[opened + 6 : max(block.rfind(b"</TEXT>"), opened + 6)].lstrip(b" \t")
    body = body[2:] if body[:2] == b"\r\n" else body[1:] if body[:1] in (b"\r", b"\n") else body
    # Some years put a blank line before the wrapper or the encoded file.
    wrapper = _WRAPPER.match(body[:64].lstrip())
    if wrapper is not None:
        body = body.lstrip()
        close = body.rfind(b"</" + wrapper.group(1) + b">")
        body = body[wrapper.end() : close if close != -1 else len(body)]
    binary = decoded(body)
    return Document(
        fields.get("TYPE", ""),
        fields.get("SEQUENCE", ""),
        fields.get("FILENAME", ""),
        fields.get("DESCRIPTION", ""),
        binary if binary is not None else unix_lines(body),
    )


def read(data: bytes) -> tuple[str, list[Document]]:
    """A submission's accession number ("" if it gives none) and its documents,
    in the filing's order."""
    data = unstuffed(data)
    found = _ACCESSION.search(data[:4096])
    documents = [made for block in blocks(data) if (made := document(block)) is not None]
    return (found.group(1).decode() if found else ""), documents


def safe_name(name: str) -> bool:
    """Whether a document's name can be used as a file's name as it stands."""
    return bool(_FILE_NAME.match(name))


def main(arguments: list[str] | None = None) -> int:
    options = argparse.ArgumentParser(
        description="Write the documents of EDGAR daily archives as SEC's site serves them."
    )
    options.add_argument("out", type=Path, help="the folder to write to")
    options.add_argument("archives", nargs="+", help="daily archives (YYYYMMDD.nc.tar.gz)")
    options.add_argument("--only", action="append", default=[], metavar="ACCESSION")
    options.add_argument("--list", action="store_true", help="print the documents, write none")
    args = options.parse_args(arguments)

    filings = written = unnamed = 0
    for archive in args.archives:
        for member, data in members(archive):
            # A filing not asked for is passed over before its documents are read.
            named = _ACCESSION.search(data[:4096])
            if args.only and (named is None or named.group(1).decode() not in args.only):
                continue
            accession, documents = read(data)
            # A correction has the number of the filing it corrects: keep the two apart.
            folder = accession if member.endswith(".nc") else f"{accession}{Path(member).suffix}"
            if not accession or (args.only and accession not in args.only):
                continue
            filings += 1
            for made in documents:
                if not safe_name(made.name):
                    unnamed += 1
                    continue
                if args.list:
                    print(f"{folder}\t{made.type}\t{made.name}\t{len(made.body)}")
                    continue
                target = args.out / folder / made.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(made.body)
                written += 1
    said = f"{filings:,} filings, {written:,} documents written"
    print(
        said + (f", {unnamed:,} without a file name left out" if unnamed else ""), file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
