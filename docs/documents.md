# The documents in an archive, and the files SEC serves

A submission in a daily archive holds every document of the filing: the form
itself, its exhibits, its images, its XBRL. Each stands between `<DOCUMENT>`
and `</DOCUMENT>`, with a few lines about it and then its text:

```
<DOCUMENT>
<TYPE>EX-99.1
<SEQUENCE>2
<FILENAME>ex99-1.htm
<DESCRIPTION>PRESS RELEASE
<TEXT>
...
</TEXT>
</DOCUMENT>
```

What stands between `<TEXT>` and `</TEXT>` is not the file SEC serves at
`https://www.sec.gov/Archives/edgar/data/{CIK}/{accession without hyphens}/{FILENAME}`.
Five things were done to the file on its way into the archive.
`tools/documents.py` undoes them, and `tools/compare.py` checks the result
against SEC's site.

## What was done to it

**1. A full stop at the start of a line is doubled.** The feed sends every line
that begins with a full stop with one more in front, as mail does. So a
stylesheet's `.note { color: red }` arrives as `..note { color: red }`, and
a browser shown the file as it stands applies none of that rule. It reaches
encoded files too: a line that holds 14 bytes begins with a full stop (the
character for the length 14), and is sent with two. SEC's site serves the
line as filed. The doubling is undone only where a submission has no line that
begins with a single full stop, which is the sign that it was sent this way.

**2. Lines end with a bare carriage return.** In the archive of 2026 every
line after a submission's first ends with a carriage return alone; in those of
1996 to 2019 with a line feed. SEC's site ends lines with a line feed. A text
document is given line feeds; an encoded file is decoded and has no lines.

**3. PDF, XBRL and XML documents are wrapped in a tag of that name.** The text
of a PDF is `<PDF>`, the encoded file, `</PDF>`; of an XBRL file `<XBRL>` ...
`</XBRL>`; of a form filed as XML `<XML>` ... `</XML>`. The wrapper is not
part of the file. Some years put a blank line before it.

**4. A binary file is uuencoded.** An image, a PDF, a spreadsheet or a zip is
text in the archive: a line `begin 644 name`, lines of up to 45 bytes each, and
`end`.

**5. Python's decoder refuses an encoded file's last line.** The last group of
characters of a file's last line is filled out with characters that
`binascii.a2b_uu` reports as "Trailing garbage", so Python's own decoders
stop at that line. Cutting each line to the
number of characters its first character calls for, before decoding it, reads
them all.

Two more things to know:

- **A document's own text can hold the tags.** A filing that quotes another
  has `<DOCUMENT>` in the middle of a line. Only a tag at the start of a line
  begins or ends a document.
- **Filings before about 2001 name no files.** Their documents have no
  `<FILENAME>`, and SEC's site names them itself (`0001.txt`, ...). The
  documents are read all the same, with an empty name; the command leaves them
  out, having nothing to call them.

## How it was checked

`tools/compare.py` takes a few documents of each kind of file from an archive,
fetches the same files from SEC's site, and says how they compare.

On the archive of 24 November 2026, three of each kind:

| Kind | Byte for byte | But for blanks at line ends | But for what SEC's site adds | But for white space | Different |
|---|---|---|---|---|---|
| `.gif` `.jpg` `.pdf` `.zip` `.json` `.xsd` | 18 | | | | |
| `.htm` | | 2 | 1 | | |
| `.txt` `.css` | | 6 | | | |
| `.xml` | 1 | 1 | | 1 | |
| `.js` `.paper` | | | 6 | | |
| All 36 | 19 | 9 | 7 | 1 | 0 |

"What SEC's site adds" is not the filing's: SEC serves some documents inside
the submission's own wrapping (`<DOCUMENT>` ... `<TEXT>`), and adds a script of
its own to some HTML. "Blanks at line ends" are spaces before a line's end,
which SEC's site drops.

The same reading, as part of [s6y.io](https://s6y.io), was compared before on
five days between 2001 and 2026: 198 of 202 documents were the same (117 byte
for byte, 72 but for what SEC's site adds, 9 but for blanks). The other four
were copies of SEC's own script for its XBRL viewer, which differ from the
copy SEC's site serves.

**Years not looked at.** 1996 to 2000 and most years between those five days
have not been compared. Before relying on a year, run the comparison on a day
of it:

```sh
python tools/compare.py --user-agent "Your Name you@example.com" 20040315.nc.tar.gz
```

It makes one request a second unless told otherwise (`--pause`), a few dozen
in all for an archive, and takes about a quarter of an hour for an archive of
2.7 GB, nearly all of it reading the archive. SEC allows a user ten requests a
second in all and asks every program to name itself:
<https://www.sec.gov/os/accessing-edgar-data>.

## Using it

```sh
python tools/documents.py out/ 20261120.nc.tar.gz                 # every filing's documents
python tools/documents.py out/ 20261120.nc.tar.gz --only 0000064803-26-000300
python tools/documents.py out/ 20261120.nc.tar.gz --list          # one line a document, nothing written
```

Documents are written to `out/{accession number}/{file name}`. A correction to
an earlier filing (`.corr01`) goes to a folder of its own, named with that
ending, since it carries the number of the filing it corrects. A day's
documents unpacked are several gigabytes.

As a module (`tools/` on the path):

```python
import documents
from headers import members

for name, data in members("20261120.nc.tar.gz"):
    accession, found = documents.read(data)
    for document in found:
        document.type, document.name, document.description, document.body
```

It reads a submission into memory, which for the largest is hundreds of
megabytes, and works by searching for bytes, not by regular expressions over
the whole of it: the first version, which used them, took seven times as long.
