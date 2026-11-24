"""Check EDGAR submission headers against the DTD with an SGML parser.

    python tools/validate.py PATH ...

A PATH is a daily archive from SEC (YYYYMMDD.nc.tar.gz), a file holding one
submission or one header (.nc, .corr01, .hdr.sgml), or a folder of such files.
Each header is given to OpenSP's `onsgmls` with the catalog in dtd/, and the
result is a count of the headers that are valid and of each kind of error.
The exit status is 0 only if every header is valid.

    --catalog FILE    the catalog to use (default: dtd/catalog beside tools/)
    --doctype NAME    put <!DOCTYPE NAME SYSTEM> before each header, for a
                      declaration that does not let a document go without one
    --jobs N          parsers to run at once (default: the number of processors)
    --examples N      headers to name for each kind of error (default: 3)
    --failed FILE     write the names of the headers that are not valid to FILE
    --quiet           print only the totals

OpenSP is in most systems' packages: `opensp` on Debian, Ubuntu and Fedora,
`open-sp` in Homebrew.
"""

import argparse
import collections
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from headers import header, members  # noqa: E402

CATALOG = Path(__file__).resolve().parent.parent / "dtd" / "catalog"
# "onsgmls:<OSFD>0:12:3:E: document type does not allow element "X" here"
_MESSAGE = re.compile(r"^[^:]+:(?:<[^>]*>)?[^:]*:(\d+):(\d+):([A-Z]):\s*(.*)$")


def submissions(paths: list[str]) -> Iterator[tuple[str, bytes]]:
    """The name and bytes of every submission the paths hold."""
    for given in paths:
        path = Path(given)
        if path.is_dir():
            for file in sorted(p for p in path.rglob("*") if p.is_file()):
                yield str(file), file.read_bytes()
        elif path.name.endswith((".tar.gz", ".tgz", ".tar")):
            for name, data in members(path):
                yield f"{path.name}:{name}", data
        else:
            yield str(path), path.read_bytes()


def check(parser: str, catalog: Path, data: bytes, doctype: str = "") -> list[tuple[int, str]]:
    """The errors a parser reports for one header: (line, message) each."""
    if doctype:  # on the header's own first line, so that line numbers stay true
        data = f"<!DOCTYPE {doctype} SYSTEM>".encode() + data
    run = subprocess.run(
        [parser, "-s", "-c", str(catalog)], input=data, capture_output=True, check=False
    )
    errors = []
    lines = run.stderr.decode("latin-1").splitlines()
    for line in lines:
        # Errors only: a warning is not a failure, and a line without a letter
        # ("start tag was here") is a note on the error before it.
        found = _MESSAGE.match(line)
        if found and found.group(3) in "EX":
            errors.append((int(found.group(1)), found.group(4)))
    if run.returncode and not errors:
        errors.append((0, lines[0] if lines else f"the parser ended with status {run.returncode}"))
    return errors


def main(arguments: list[str] | None = None) -> int:
    options = argparse.ArgumentParser(description="Check EDGAR submission headers against the DTD.")
    options.add_argument("paths", nargs="+")
    options.add_argument("--catalog", type=Path, default=CATALOG)
    options.add_argument("--doctype", default="")
    options.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    options.add_argument("--examples", type=int, default=3)
    options.add_argument("--failed", type=Path)
    options.add_argument("--quiet", action="store_true")
    args = options.parse_args(arguments)

    parser = shutil.which("onsgmls") or shutil.which("nsgmls")
    if parser is None:
        print("No SGML parser found: install OpenSP (the command `onsgmls`).", file=sys.stderr)
        return 2

    total = 0
    failed: list[str] = []
    kinds: collections.Counter[str] = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)

    def record(name: str, errors: list[tuple[int, str]]) -> None:
        nonlocal total
        total += 1
        if not errors:
            return
        failed.append(name)
        for message in {message for _, message in errors}:
            kinds[message] += 1
            if len(examples[message]) < args.examples:
                line = next(line for line, m in errors if m == message)
                examples[message].append(f"{name}, line {line}")

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        waiting: dict[concurrent.futures.Future, str] = {}
        for name, data in submissions(args.paths):
            waiting[pool.submit(check, parser, args.catalog, header(data), args.doctype)] = name
            if len(waiting) >= args.jobs * 4:  # keep few submissions in memory
                done, _ = concurrent.futures.wait(
                    waiting, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for future in done:
                    record(waiting.pop(future), future.result())
        for future in concurrent.futures.as_completed(waiting):
            record(waiting[future], future.result())

    print(f"{total:,} headers: {total - len(failed):,} valid, {len(failed):,} not")
    if not args.quiet:
        for message, count in kinds.most_common():
            print(f"\n{count:>7,}  {message}")
            for example in examples[message]:
                print(f"         {example}")
    if args.failed:
        args.failed.write_text("".join(f"{name}\n" for name in sorted(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
