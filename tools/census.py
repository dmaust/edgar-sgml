"""Count the tags in EDGAR submission headers: what stands inside what, how
often, and in which years.

    python tools/census.py PATH ... [--json FILE]

A PATH is a daily archive from SEC (YYYYMMDD.nc.tar.gz), a file holding one
submission or one header, or a folder of such files. No parser and no DTD is
used: a header is read as lines, so the count shows what SEC sends whether or
not the DTD allows it. It is how the DTD was written, and how to find out what
a newer archive holds that the DTD lacks:

    python tools/census.py 20270104.nc.tar.gz --against dtd/edgar-submission.dtd

lists every tag, and every place of a tag, that the DTD does not have.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from headers import header  # noqa: E402
from validate import submissions  # noqa: E402

_LINE = re.compile(rb"\r\n|\r|\n")
_TAG = re.compile(r"^\s*<(/?)([^<>\s]+)>(.*)$")
_FILED = re.compile(rb"<FILING-DATE>(\d{4})")
_ARCHIVE = re.compile(r"(?:^|[/:])((?:19|20)\d\d)\d{4}\.nc\.tar")
_VALUES = 40  # different values remembered for a tag, to give its commonest as an example


class Census:
    def __init__(self) -> None:
        self.headers = 0
        self.roots: collections.Counter[str] = collections.Counter()
        # (parent, child) -> [parents that have it, times it occurs, most in one parent]
        self.places: dict[tuple[str, str], list[int]] = collections.defaultdict(lambda: [0, 0, 0])
        self.parents: collections.Counter[str] = collections.Counter()
        self.years: dict[str, set[str]] = collections.defaultdict(set)
        self.by_year: collections.Counter[str] = collections.Counter()
        self.example: dict[tuple[str, str], str] = {}
        self.holding: collections.Counter[str] = collections.Counter()  # headers with the tag
        self.values: dict[str, collections.Counter[str]] = collections.defaultdict(
            collections.Counter
        )

    def add(self, name: str, data: bytes) -> None:
        """Count one header (a submission's text is taken out first)."""
        data = header(data)
        # The year SEC sent it: the archive's, or else the year it was filed.
        found = _ARCHIVE.search(name)
        filed = _FILED.search(data)
        year = found.group(1) if found else filed.group(1).decode() if filed else "?"
        seen: set[str] = set()
        self.headers += 1
        self.by_year[year] += 1
        closed = {tag.decode("latin-1") for tag in re.findall(rb"</([^<>\s]+)>", data)}
        stack: list[tuple[str, collections.Counter[str]]] = [("", collections.Counter())]

        def close() -> None:
            parent, children = stack.pop()
            self.parents[parent] += 1
            for child, count in children.items():
                place = self.places[(parent, child)]
                place[0] += 1
                place[1] += count
                place[2] = max(place[2], count)
                self.example.setdefault((parent, child), name)

        for raw in _LINE.split(data):
            line = _TAG.match(raw.decode("latin-1"))
            if line is None:
                continue
            end, tag, rest = line.groups()
            if end:
                while len(stack) > 1:
                    top = stack[-1][0]
                    close()
                    if top == tag:
                        break
                continue
            if len(stack) == 1:
                self.roots[tag] += 1
            else:
                stack[-1][1][tag] += 1
            self.years[tag].add(year)
            seen.add(tag)
            value = rest.strip()
            if tag in closed and not value:
                stack.append((tag, collections.Counter()))
            elif value and (value in self.values[tag] or len(self.values[tag]) < _VALUES):
                self.values[tag][value] += 1
        while len(stack) > 1:
            close()
        self.holding.update(seen)

    def record(self) -> dict:
        """The count as plain data."""
        return {
            "headers": self.headers,
            "by_year": dict(sorted(self.by_year.items())),
            "roots": dict(self.roots),
            "tags": {
                tag: {
                    "headers": self.holding[tag],
                    "years": sorted(self.years[tag]),
                    "example": self.values[tag].most_common(1)[0][0] if self.values[tag] else "",
                }
                for tag in sorted(self.holding)
            },
            "containers": {
                parent: {
                    "count": self.parents[parent],
                    "children": {
                        child: {
                            "in": place[0],
                            "times": place[1],
                            "most": place[2],
                            "years": sorted(self.years[child]),
                            "example": self.example[(p, child)],
                        }
                        for (p, child), place in sorted(self.places.items())
                        if p == parent
                    },
                }
                for parent in sorted(self.parents)
                if parent
            },
        }


def allowed(dtd: Path) -> dict[str, set[str]]:
    """For each element the DTD declares, the elements its content may hold."""
    text = re.sub(r"<!--.*?-->", "", dtd.read_text(encoding="utf-8"), flags=re.DOTALL)
    entities: dict[str, str] = {}
    for name, value in re.findall(r'<!ENTITY\s+%\s+([\w.-]+)\s+"([^"]*)"', text):
        entities[name] = value

    def expand(value: str) -> str:
        for _ in range(8):
            value, changed = re.subn(r"%([\w.-]+);", lambda m: entities.get(m.group(1), ""), value)
            if not changed:
                break
        return value

    found: dict[str, set[str]] = {}
    declarations = re.findall(r"<!ELEMENT\s+(\([^)]*\)|[\w.-]+)\s+[-oO]\s+[-oO]\s+([^>]*)>", text)
    for names, model in declarations:
        model = re.sub(r"-\([^)]*\)\s*$", "", expand(model))  # an exclusion names no child
        children = {
            name.upper()
            for name in re.findall(r"[A-Za-z][\w.-]*", model)
            if name.upper() not in ("EMPTY", "PCDATA", "CDATA", "RCDATA", "ANY")
        }
        for name in re.findall(r"[A-Za-z][\w.-]*", expand(names)):
            found[name.upper()] = children
    return found


def main(arguments: list[str] | None = None) -> int:
    options = argparse.ArgumentParser(description="Count the tags in EDGAR submission headers.")
    options.add_argument("paths", nargs="+")
    options.add_argument("--json", type=Path, help="write the count to this file")
    options.add_argument("--against", type=Path, help="a DTD to hold the count against")
    args = options.parse_args(arguments)

    census = Census()
    for name, data in submissions(args.paths):
        census.add(name, data)
    record = census.record()
    if args.json:
        args.json.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")

    print(f"{census.headers:,} headers; first tags: {dict(census.roots)}")
    if args.against:
        model = allowed(args.against)
        unknown = 0
        for parent, entry in record["containers"].items():
            for child, place in entry["children"].items():
                if parent not in model:
                    reason = f"{parent} is not declared"
                elif child not in model:
                    reason = "not declared"
                elif child not in model[parent]:
                    reason = "not allowed there"
                else:
                    continue
                unknown += 1
                where = f"{child} in {parent}"
                print(f"  {where:58} {reason:28} {place['in']:>7,}  {place['example']}")
        print(f"{unknown} places the DTD does not have")
        return 1 if unknown else 0
    for parent, entry in record["containers"].items():
        print(f"\n{parent}  ({entry['count']:,})")
        for child, place in sorted(entry["children"].items(), key=lambda item: -item[1]["in"]):
            share = place["in"] / entry["count"]
            most = f", up to {place['most']}" if place["most"] > 1 else ""
            years = place["years"]
            print(f"    {child:44} {share:7.2%}{most}   {years[0]}-{years[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
