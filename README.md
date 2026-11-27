# edgar-sgml

A document type definition (DTD) for the SGML headers of SEC EDGAR filings that
works: an SGML parser accepts it, and it describes the headers SEC actually
sends. It is tested against real headers from 1996 to 2026.

Every filing in EDGAR begins with a header: who filed, on what form, when, and
which documents the filing holds. The header is SGML, and SEC publishes a DTD
for it, but only printed in a PDF (section 3.4 of the
[EDGAR Public Dissemination Service Technical Specification](https://www.sec.gov/files/info/edgar/specifications/pds_dissemination_spec.pdf)).
As printed, no parser can read that DTD, and once it is repaired enough to be
read it accepts none of the headers SEC sends today. This repository has one
that does.

If you are new to EDGAR's files, two pages on [s6y.io](https://s6y.io), the
site this was made for, give the surroundings:
[SEC's EDGAR data: where it is and how to read it](https://s6y.io/guide/data)
(every address, the formats, the rules for fetching) and
[How EDGAR works](https://s6y.io/guide/edgar) (what a header's lines mean, and
how a filing gets its date).

## How the two DTDs fare

Each was given every header in six of SEC's daily archives, one day from each
of 1996, 2001, 2005, 2012, 2019 and 2026: 14,876 headers, read by
[OpenSP](https://openjade.sourceforge.net/doc/index.htm), the standard SGML
parser.

| DTD | Headers it accepts |
|---|---|
| SEC's, as printed | None: the parser stops at the DTD itself |
| SEC's, with only its faults of syntax put right (`sec/repaired/`) | 0 of 14,876. It requires every document to have a `<FILENAME>` and never declares that tag |
| The same with `<FILENAME>` declared | 10,345 of 14,876 (70%): none of 1996, none of 2026, 77% to 94% in the years between |
| This one (`dtd/`) | 14,875 of 14,876. The other is a 1996 filing that SEC itself marked `<FLAWED>` |

The header files SEC serves beside each filing (`.hdr.sgml`) were tried too.
All 317 fetched are valid as they come: 72 for filings of the six days, and
245 chosen to show every arrangement of tags found in a survey of 400,000
headers of 2021 to 2026.

[docs/differences.md](docs/differences.md) lists what was changed from SEC's
DTD and the evidence for each change.

## Try it

You need OpenSP: `apt install opensp`, `dnf install opensp` or
`brew install open-sp`.

A header file from SEC's site needs nothing done to it. (SEC asks programs to
name themselves; put your own name and address in the `User-Agent`.)

```sh
curl -A "Your Name you@example.com" -O \
  https://www.sec.gov/Archives/edgar/data/64803/000006480326000010/0000064803-26-000010.hdr.sgml

onsgmls -s -c dtd/catalog 0000064803-26-000010.hdr.sgml    # prints nothing: it is valid
osx -c dtd/catalog 0000064803-26-000010.hdr.sgml > header.xml    # the same header as XML
```

A whole day of filings, from one of SEC's
[daily archives](https://www.sec.gov/Archives/edgar/Feed/):

```sh
python tools/validate.py 20261120.nc.tar.gz
```

```
2,823 headers: 2,823 valid, 0 not
```

The tools need Python 3.10 or later and nothing else.

## What is here

| Path | What it is |
|---|---|
| `dtd/edgar-submission.dtd` | The DTD: a submission from an archive (`SUBMISSION`) and a header file from SEC's site (`SEC-HEADER`, `IMS-HEADER`) |
| `dtd/edgar.dcl` | The SGML declaration that goes with it: long tag names, and an ampersand that is only an ampersand |
| `dtd/catalog` | Lets a parser find both, so that a file needs no `<!DOCTYPE>` line |
| `docs/tags.md` | Every tag: what it holds, where it stands, SEC's description of it, how often real headers have it, an example |
| `docs/files.md` | Where headers are found and what to do before parsing one |
| `docs/differences.md` | Every difference from SEC's DTD, with the evidence |
| `sec/` | SEC's specification, its DTD exactly as printed, the DTD repaired only as far as a parser needs, and its tag definitions as data |
| `docs/documents.md` | What an archive does to a filing's documents, and how to get back the files SEC serves |
| `tools/headers.py` | Cuts the header out of a submission (takes the documents' text away) |
| `tools/documents.py` | Reads a submission's documents as SEC's site serves them: undoes the doubled full stops, the wrappers and the encoding |
| `tools/compare.py` | Compares documents read from an archive with SEC's own copies |
| `tools/validate.py` | Runs the parser over files, folders or daily archives and counts the errors by kind |
| `tools/census.py` | Counts the tags in real headers without any DTD, and lists what a DTD lacks |
| `tests/` | The tests, with 46 real headers that between them show every tag in every place it was found |

## The documents too

A daily archive holds every document of every filing, but not as SEC's site
serves them: a full stop at the start of a line is doubled, PDF and XML are
wrapped in a tag, binary files are encoded as text that Python's own decoder
refuses. `tools/documents.py` gives back the files as SEC serves them:

```sh
python tools/documents.py out/ 20261120.nc.tar.gz    # out/{accession number}/{file name}
```

Checked against SEC's site: of 36 documents of twelve kinds from the archive
of 24 November 2026, 19 were the same byte for byte and the other 17 but for
blanks at line ends or what SEC's site itself adds.
[docs/documents.md](docs/documents.md) has what is done and the evidence.

## Three things to know before parsing a header

1. **A submission is mostly not header.** The documents of a filing follow the
   header in the same file, each between `<TEXT>` and `</TEXT>`, and they are
   HTML, XML or encoded files. Take them out first (`tools/headers.py`); the
   header files on SEC's site have none.
2. **An ampersand is only an ampersand.** Headers say `AT&T INC` and `MD&A`.
   A parser following SEC's own declaration takes `&T` for a reference to
   something named T and reports an error. The declaration here makes `&`
   ordinary text.
3. **Lines end in more than one way.** Older archives use a line feed, the
   archive of 2026 a bare carriage return. The parser reads both alike.

A character outside ASCII comes as a number, `C&#298;ON` for CĪON. It is left
as that text; decoding it is up to whoever reads the value.

[docs/files.md](docs/files.md) has the detail.

## When SEC adds a tag

SEC adds tags without notice. The 2026 day has fourteen that none of the five
earlier days has, one of them (`<ORGANIZATION-NAME>`) in all but one of its
headers. A header with a tag the DTD does not know is not valid, which is the
point of a DTD, so this one needs keeping up. To see what a newer archive holds
that the DTD lacks:

```sh
python tools/census.py 20270104.nc.tar.gz --against dtd/edgar-submission.dtd
```

Reports of headers that fail, with the accession number, are welcome as issues.

## Running the tests

```sh
pip install pytest && pytest          # needs onsgmls on the PATH
```

or, with nothing installed but podman or docker:

```sh
podman build -t edgar-sgml . && podman run --rm -v "$PWD":/repo:ro,Z edgar-sgml
```

## Where this comes from

It was made while building [s6y.io](https://s6y.io), which serves EDGAR filings
as pages that are easy to read. The site first read headers with an SGML parser
and a DTD patched by hand; this is that work done again from the beginning and
checked. The site's own reader of headers and of whole submissions, in Python,
is to follow here.

The site is also a place to see what a header says, laid out for reading: the
header fetched above is that of
[CVS Health's annual report for 2025](https://s6y.io/c/cvs/10-K-20260210/list).
Its guide has more for people who work with the filings by program:

- [SEC's EDGAR data](https://s6y.io/guide/data): the folders, the APIs, the
  nightly archives, and what has to be undone to get a document out of one
- [How EDGAR works](https://s6y.io/guide/edgar): the path of a filing, the
  clock it is filed against, and what can happen to it afterwards
- [SEC forms explained](https://s6y.io/glossary): what each form is

## License

MIT for what was written here (see [LICENSE](LICENSE)). SEC's specification,
what is taken from it, and the headers of filings in the tests are works of the
United States government or public records, and are not covered by it
(see [NOTICE](NOTICE)).
