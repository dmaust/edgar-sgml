import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
CATALOG = ROOT / "dtd" / "catalog"

sys.path.insert(0, str(ROOT / "tools"))


class Parsed:
    """What OpenSP made of a document: its errors, and the document as the
    parser read it (one line an event: "(TAG" opens an element, ")TAG" closes
    it, "-" is text)."""

    def __init__(self, run: subprocess.CompletedProcess):
        self.errors = [
            line.split(":E: ", 1)[1]
            for line in run.stderr.decode("latin-1").splitlines()
            if ":E: " in line
        ]
        self.events = run.stdout.decode("latin-1").splitlines()

    @property
    def valid(self) -> bool:
        return not self.errors

    def elements(self) -> list[str]:
        return [event[1:] for event in self.events if event.startswith("(")]

    def text_of(self, tag: str) -> list[str]:
        """The text of each element of that name that holds any."""
        found, inside = [], False
        for event in self.events:
            if event == f"({tag}":
                inside = True
            elif event.startswith("-") and inside:
                found.append(event[1:])
                inside = False
            elif event.startswith(("(", ")")):
                inside = False
        return found


@pytest.fixture(scope="session")
def onsgmls() -> str:
    parser = shutil.which("onsgmls")
    if parser is None:
        pytest.skip("OpenSP (the command `onsgmls`) is not installed")
    return parser


@pytest.fixture(scope="session")
def parse(onsgmls):
    def run(data: bytes | str, catalog: Path = CATALOG) -> Parsed:
        if isinstance(data, str):
            data = data.encode("latin-1")
        return Parsed(
            subprocess.run([onsgmls, "-c", str(catalog)], input=data, capture_output=True)
        )

    return run


def archive_fixtures() -> list[Path]:
    return sorted(p for p in (FIXTURES / "archive").rglob("*") if p.is_file())


def sec_fixtures() -> list[Path]:
    return sorted((FIXTURES / "sec").glob("*.hdr.sgml"))
