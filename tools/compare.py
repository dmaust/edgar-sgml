"""Compare the documents read out of a daily archive with SEC's own copies.

    python tools/compare.py --user-agent "Your Name you@example.com" 20120515.nc.tar.gz

takes a few documents of each kind of file (.htm, .txt, .xml, .jpg, .pdf, ...)
from the archive, fetches the same files from the filings' folders on
www.sec.gov, and counts how they compare:

    identical                                  the same bytes
    identical but for what SEC's site adds     SEC serves some documents in the
                                               submission's wrapping, and adds a
                                               script of its own to some HTML
    identical but for blanks at line ends
    identical but for white space
    DIFFERENT                                  printed, with the filing and file
    not at SEC                                 SEC's site has no such file

It is how tools/documents.py was checked, and how to check it on a year not
looked at before. It asks SEC for one file a comparison, one a second unless
told otherwise: SEC allows a user ten requests a second in all and asks every
program to name itself, so --user-agent is required and should be your own
name and address.
"""

import argparse
import collections
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from pathlib import Path

from documents import read, safe_name, unix_lines
from headers import members

_CIK = re.compile(rb"<CIK>(\d+)")
_SECS_SCRIPT = re.compile(rb'<script type="text/javascript"\s+src="/[^"]*">\s*</script>')
_BLANKS = re.compile(rb"[ \t]+(?=\n)")
_ENVELOPE = re.compile(rb"\A<DOCUMENT>\n.*?<TEXT>\n(.*)</TEXT>\n</DOCUMENT>\s*\Z", re.S)

DIFFERENT, MISSING = "DIFFERENT", "not at SEC"


def url(cik: int, accession: str, name: str) -> str:
    """Where SEC's site serves a filing's document."""
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{name}"


def compared(ours: bytes, theirs: bytes) -> str:
    """How a document read from an archive stands to SEC's copy of it, in
    words. What SEC's site adds or drops is not the filing's: the submission's
    own wrapping around some text, a script of SEC's in some HTML, the blanks at
    the ends of lines."""
    if ours == theirs:
        return "identical"
    theirs = unix_lines(theirs)
    enveloped = _ENVELOPE.match(theirs)
    theirs = _SECS_SCRIPT.sub(b"", enveloped.group(1) if enveloped else theirs)
    if ours.strip() == theirs.strip():
        return "identical but for what SEC's site adds"
    if _BLANKS.sub(b"", ours).strip() == _BLANKS.sub(b"", theirs).strip():
        return "identical but for blanks at line ends"
    if b"".join(ours.split()) == b"".join(theirs.split()):
        return "identical but for white space"
    return DIFFERENT


def compare(
    archives: Iterable[str | Path],
    fetch: Callable[[str], bytes | None],
    each: int = 3,
    say: Callable[[str], None] = print,
) -> collections.Counter:
    """Count how `each` documents of every kind of file in each archive compare
    with SEC's. `fetch` gives the bytes at an address, or None if there is no
    such file. Returns {(kind of file, how it compares): documents}."""
    counts: collections.Counter = collections.Counter()
    for archive in archives:
        taken: collections.Counter = collections.Counter()
        for member, data in members(archive):
            # A correction is not the filing SEC's folder holds.
            if not member.endswith(".nc"):
                continue
            cik = _CIK.search(data[:20000])
            # Most submissions hold nothing still wanted: don't decode those.
            if cik is None or all(taken[kind] >= each for kind in _kinds(data)):
                continue
            number = int(cik.group(1))
            accession, documents = read(data)
            for made in documents:
                kind = Path(made.name).suffix.lower() or "(none)"
                if not accession or not safe_name(made.name) or taken[kind] >= each:
                    continue
                taken[kind] += 1
                theirs = fetch(url(number, accession, made.name))
                how = MISSING if theirs is None else compared(made.body, theirs)
                if how == DIFFERENT:
                    say(f"{Path(archive).name} {accession} {made.name}: {how}")
                counts[kind, how] += 1
    return counts


_NAME = re.compile(rb"(?:(?<=[\r\n])|\A)<FILENAME>([^\r\n]*)")


def _kinds(data: bytes) -> set[str]:
    """The kinds of file a submission names, from its documents' own lines."""
    return {
        Path(name.strip().decode("latin-1")).suffix.lower() or "(none)"
        for name in _NAME.findall(data)
    }


def fetcher(user_agent: str, pause: float) -> Callable[[str], bytes | None]:
    """A `fetch` for `compare` that asks SEC, waiting `pause` seconds first."""

    def fetch(address: str) -> bytes | None:
        time.sleep(pause)
        request = urllib.request.Request(address, headers={"User-Agent": user_agent})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise

    return fetch


def report(counts: collections.Counter) -> list[str]:
    """The counts as lines, a kind of file at a time."""
    width = max((len(kind) for kind, _ in counts), default=0)
    return [
        f"{kind:<{width}}  {count:>4}  {how}"
        for (kind, how), count in sorted(counts.items(), key=lambda item: (item[0][0], -item[1]))
    ]


def main(arguments: list[str] | None = None) -> int:
    options = argparse.ArgumentParser(
        description="Compare documents read from EDGAR daily archives with SEC's own copies."
    )
    options.add_argument("archives", nargs="+", help="daily archives (YYYYMMDD.nc.tar.gz)")
    options.add_argument("--user-agent", required=True, help="your name and address, for SEC")
    options.add_argument("--each", type=int, default=3, help="documents of each kind, an archive")
    options.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    args = options.parse_args(arguments)

    counts = compare(args.archives, fetcher(args.user_agent, args.pause), args.each)
    for line in report(counts):
        print(line)
    different = sum(count for (_, how), count in counts.items() if how == DIFFERENT)
    print(f"{sum(counts.values()):,} documents compared, {different:,} different", file=sys.stderr)
    return 1 if different else 0


if __name__ == "__main__":
    sys.exit(main())
