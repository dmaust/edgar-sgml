# Where the headers are, and what to do before parsing one

Every filing in EDGAR has a header in SGML: who filed, on what form, when, and
which documents the filing holds. SEC publishes it in two places, and the DTD
in `dtd/` reads both.

For everything else SEC publishes (the APIs, the indexes, the bulk files) and
the rules for fetching it, see
[SEC's EDGAR data: where it is and how to read it](https://s6y.io/guide/data).

## The daily archives

`https://www.sec.gov/Archives/edgar/Feed/{YYYY}/QTR{n}/{YYYYMMDD}.nc.tar.gz`

One archive a business day, holding everything SEC made public that day. Each
member is one submission:

| Member | What it is |
|---|---|
| `{accession}.nc` | A filing: the header, then every document of the filing, one after another |
| `{accession}.corr01`, `.corr02`, ... | A correction SEC made to a filing of an earlier day. It has the same form, begins with `<CORRECTION>` or `<TIMESTAMP>` or both, and may list a document without its text |

A submission's first tag is `<SUBMISSION>`.

The header is a small part of it. In the six days measured here it was 0.1% to
1.3% of an archive's bytes, about 1 KB for a typical filing; the rest is the
documents.

| Day | Submissions | Unpacked | Lines end with |
|---|---|---|---|
| 1996-03-15 | 652 | 69 MB | line feed |
| 2001-06-13 | 715 | 89 MB | line feed |
| 2005-03-11 | 3,074 | 887 MB | line feed |
| 2012-05-15 | 5,849 | 4,868 MB | line feed |
| 2019-06-12 | 1,763 | 1,267 MB | line feed |
| 2026-11-20 | 2,823 | 5,131 MB | a carriage return alone, after a first line that ends with a line feed |

## The header file in a filing's folder

`https://www.sec.gov/Archives/edgar/data/{CIK}/{accession without hyphens}/{accession}.hdr.sgml`

The header alone, without the documents' text and without the list of
documents. Its first tag is `<SEC-HEADER>` (`<IMS-HEADER>` for a filing of
1994), and the rest of its first line is the file's own name and a date:

```
<SEC-HEADER>0000064803-26-000010.hdr.sgml : 20260210
<ACCEPTANCE-DATETIME>20260210063659
<ACCESSION-NUMBER>0000064803-26-000010
<TYPE>10-K
...
```

`<ACCEPTANCE-DATETIME>` is in these files only (the archives do not carry
it): in every file looked at for filings of 2005 and later, and in none of
those of 1996 and 2001. The files of all six years end their lines with a line
feed.

This file needs nothing done to it before parsing:

```sh
onsgmls -s -c dtd/catalog 0000064803-26-000010.hdr.sgml
```

SEC asks that programs fetching from www.sec.gov say who they are in the
`User-Agent` header and make no more than ten requests a second:
<https://www.sec.gov/os/accessing-edgar-data>.

## What this DTD does not read

`{accession}.txt`, the "complete submission text file" in the same folder,
begins `<SEC-DOCUMENT>` and has the header as lines of text with labels
(`ACCESSION NUMBER:`, `CONFORMED SUBMISSION TYPE:`), not as tags. It holds the
same facts and is a different format.

## Before parsing a submission from an archive

**Take the documents' text out.** What stands between a line beginning `<TEXT>`
and the next `</TEXT>` is the document itself: HTML, XML, or a PDF, image or
spreadsheet encoded as text. An SGML parser given that would report thousands
of errors, since every `<p>` is a tag the DTD does not know. `tools/headers.py`
removes it and leaves everything else byte for byte:

```sh
python tools/headers.py out/ 20261120.nc.tar.gz    # one header a file in out/20261120/
```

**Nothing else.** In particular:

- *Ampersands need no escaping.* Headers hold them plainly (`AT&T INC`, `MD&A`,
  and once `C&#298;ON`). Of the 14,876 headers read, 1,621 hold an ampersand,
  and in 160 it is followed by a letter or `#`, which an SGML parser would
  otherwise take for the start of a reference. The declaration in
  `dtd/edgar.dcl` makes an ampersand ordinary text.
- *Line ends need no changing.* The declaration gives SGML's two record
  characters their usual codes, and the parser reads all three conventions
  alike (a test holds this).
- *No document type declaration is needed.* The declaration lets a document go
  without one, and the catalog names the DTD for each of the three first tags.
  A parser that cannot do that can be given
  `<!DOCTYPE SUBMISSION PUBLIC "-//edgar-sgml//DTD EDGAR Submission Header//EN">`
  on a line before the header.

No header read so far has a `<` inside a value or a byte outside ASCII.
Nothing in SEC's specification promises either.

**A character outside ASCII comes as a number**: `C&#298;ON Investment Corp`
for CĪON, `&#147;Group Policies&#148;` for a name in quotation marks. The
parser leaves it as that text. The numbers are not all Unicode: 147, 148, 150
and 153 are positions in the Windows code page (the two quotation marks, a
dash and the trade mark sign), as HTML reads them. Python's `html.unescape`
decodes both kinds.

## Reading the result

`onsgmls` prints the document as the parser understood it, one event a line;
`osx` (also part of OpenSP) prints it as XML, which any language can read:

```sh
osx -c dtd/catalog 0000064803-26-000010.hdr.sgml > header.xml
```

Every tag SEC leaves open is closed, and `&` is written `&amp;`:

```xml
<COMPANY-DATA
><CONFORMED-NAME
>CVS HEALTH Corp</CONFORMED-NAME><CIK
>0000064803</CIK><ASSIGNED-SIC
>5912</ASSIGNED-SIC><ORGANIZATION-NAME
>07 Trade &amp; Services</ORGANIZATION-NAME>...
```
