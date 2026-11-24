"""Cut the header out of an EDGAR submission.

A submission, as SEC's daily archives and its dissemination feed carry it, is a
header followed by the filing's documents. Each document's content stands
between a line that begins <TEXT> and the next </TEXT>, and it is most of the
submission: HTML, XML, or a PDF or image encoded as text. None of it is SGML
that the header's DTD can read, so it has to come out before a parser sees the
rest.

    python tools/headers.py OUT_DIR 20261120.nc.tar.gz ...

writes one file a submission, named as in the archive. As a module:

    header(data)        the submission without its documents' content
    members(archive)    (name, bytes) for each submission in a daily archive
"""

import re
import sys
import tarfile
from collections.abc import Iterator
from pathlib import Path

# A line that begins <TEXT>. Lines end with a line feed, a carriage return and
# a line feed, or (in the archives of recent years) a carriage return alone,
# which "^" does not take for the start of a line.
_TEXT_START = re.compile(rb"(?:^|(?<=\r))<TEXT>[^\r\n]*(?:\r\n|\r|\n|\Z)", re.MULTILINE)


def header(data: bytes) -> bytes:
    """`data` without what stands between each <TEXT> line and its </TEXT>.

    Everything else is returned byte for byte, line ends included. A document
    whose text is never closed loses the rest of the submission, as it would
    for any reader.
    """
    kept = []
    at = 0
    while True:
        start = _TEXT_START.search(data, at)
        if start is None:
            kept.append(data[at:])
            break
        kept.append(data[at : start.end()])
        end = data.find(b"</TEXT>", start.end())
        if end == -1:
            break
        at = end
    return b"".join(kept)


def members(archive: str | Path) -> Iterator[tuple[str, bytes]]:
    """Each submission of a daily archive (YYYYMMDD.nc.tar.gz): its name in the
    archive and its bytes. Besides new filings (.nc) an archive holds
    corrections to earlier ones (.corr01, ...), which have the same form."""
    with tarfile.open(archive, mode="r|*") as tar:
        for member in tar:
            file = tar.extractfile(member) if member.isfile() else None
            if file is not None:
                yield Path(member.name).name, file.read()


def main(arguments: list[str]) -> int:
    if len(arguments) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    out = Path(arguments[0])
    for archive in arguments[1:]:
        folder = out / Path(archive).name.split(".")[0]
        folder.mkdir(parents=True, exist_ok=True)
        count = 0
        for name, data in members(archive):
            (folder / name).write_bytes(header(data))
            count += 1
        print(f"{archive}: {count:,} headers in {folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
