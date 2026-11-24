# What differs from SEC's DTD, and why

SEC's DTD is section 3.4 of the EDGAR Public Dissemination Service (PDS)
Technical Specification (the edition dated December 2020, in `sec/`). The DTD
in `dtd/` starts from it. This page lists every change, each with what was
seen in real headers.

The headers come from three places:

- **Six days of SEC's daily archives**, every submission in them: 15 March
  1996, 13 June 2001, 11 March 2005, 15 May 2012, 12 June 2019 and 20 November
  2026. 14,876 headers. Each was read as SEC sent it, with only the documents'
  text taken out.
- **Header files from www.sec.gov** (`.hdr.sgml`), fetched one at a time: 72
  for filings of those six days, and 245 chosen by the survey below. All 317
  are valid.
- **A survey of 400,000 headers** of 2021 to 2026, already parsed, that
  [s6y.io](https://s6y.io) keeps. It was used only to find what the six days
  lack. It showed 286 different arrangements of tags; a filing with each was
  then fetched from SEC and read as SEC sent it (245 files, which is where the
  figures marked "in the survey" come from).

## 1. Faults that stop a parser

Before any question of what real headers hold, SEC's text cannot be read as
SGML. `sec/dtd-as-printed.txt` is the text as printed; `sec/repaired/` has it
with these put right and nothing else changed.

| In the print | Repaired as |
|---|---|
| `<!SGML "ISO 8879-1986"` | `"ISO 8879:1986"`, the only spelling a parser takes |
| `SUBDOCNO` | `SUBDOC NO` |
| Marks of the print inside the text (`C-1` to `C-6`) and words broken across lines (`filing-` / `date`) | Removed and joined |
| `<!ENTITY % address "street1?, ... zip?", phone? >`: the quotation mark closes too soon | `"street1?, street2?, city?, state?, zip?"`; `business-address` adds `phone?` itself |
| `company-data \| owner-data` inside a sequence, without parentheses | `(company-data \| owner-data)` |
| `<!ELEMENT company-data \| owner-data ...>` and `<!ELEMENT former-company \| former-name ...>`: two names without parentheses | `(company-data \| owner-data)`, `(former-company \| former-name)` |
| `new-series*;`, `acquiring-data;` and others: a semicolon after a name in a content model | Removed |
| `merger-series-and classes-contracts`: a space in a name | `merger-series-and-classes-contracts` |
| `<!—Series ...`: a dash of the wrong kind opens a comment | `<!--` |

A test puts each fault back, one at a time, and checks that the parser then
refuses the DTD. Two more misprints are left as printed, since the parser lets
them pass: `2425` for `24 25` in a list of characters, and the ampersand among
the characters a name may have (`LCNMCHAR "-.&"`).

With those repaired the parser accepts the DTD and rejects every one of the
14,876 headers: the DTD requires a `<FILENAME>` in each document and has no
declaration for it. With that one declaration added it accepts 10,345 (70%):

| Day | Accepted |
|---|---|
| 1996-03-15 | 0 of 652 |
| 2001-06-13 | 549 of 715 (77%) |
| 2005-03-11 | 2,895 of 3,074 (94%) |
| 2012-05-15 | 5,433 of 5,849 (93%) |
| 2019-06-12 | 1,467 of 1,763 (83%) |
| 2026-11-20 | 1 of 2,823 |

## 2. The SGML declaration

| Change | Why |
|---|---|
| An ampersand does not begin a reference. The two delimiters that would make one (`ERO`, `CRO`) are spelled `&&&` and `&&&#` | Headers hold ampersands as text: `AT&T INC`, `MD&A`. 1,621 of the 14,876 headers have one, and 160 have one followed by a letter or `#`, each of which SEC's declaration makes an error. No header uses a reference to a named entity. A character outside ASCII is written as a number (`C&#298;ON`, `&#147;Group Policies&#148;`), which SGML cannot resolve either: the numbers are not positions in the document's character set, and some are Windows code page numbers. So the text is left as it is, for whoever reads the value to decode |
| `_` is a character of names | The tags `<MA-I_INDIVIDUAL>` and `<ISSUING_ENTITY>` |
| `NAMELEN 64` in place of 40 | `<FILED-PURSUANT-TO-GENERAL-INSTRUCTION-A2>` is exactly 40 characters long. The next long name would otherwise break every parser |
| A document may go without a `<!DOCTYPE>` declaration (`IMPLYDEF DOCTYPE YES`, which needs the declaration to begin `"ISO 8879:1986 (WWW)"`) | SEC's files have none. The catalog names the DTD for each first tag, so a file is parsed as it comes |

Left as SEC has them: the character set (ASCII), the two record characters,
tags that may be left open (`OMITTAG YES`) and none of SGML's other shortcuts.

## 3. Tags added

Real headers have these and SEC's DTD has no declaration for them. "In the
spec" says whether section 3.3 of SEC's specification, which is newer than its
DTD, describes the tag.

| Tag | Where | Seen | In the spec |
|---|---|---|---|
| `FILENAME` | `DOCUMENT` | 86,725 of 88,435 documents; every day but 1996 | yes (and SEC's DTD requires it without declaring it) |
| `ORGANIZATION-NAME` | `COMPANY-DATA`, `OWNER-DATA` | 2,822 of the 2,823 headers of the 2026 day | no |
| `SROS` | `SUBMISSION` | every header of the 1996 day | no |
| `PERIOD-START` | `SUBMISSION` | 329 headers, 2012 to 2026 | yes |
| `ADDRESS-IS-A-NON-US-LOCATION`, `NON-US-STATE-TERRITORY`, `PROVINCE-COUNTRY` | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | 171 headers of 2026 | no |
| `NO-QUARTERLY-ACTIVITY`, `NO-ANNUAL-ACTIVITY`, `NO-INITIAL-PERIOD-ACTIVITY` | `SUBMISSION` | 76, 76 and 3 headers of 2012 | yes |
| `DEPOSITOR-CIK`, `SPONSOR-CIK` | `SUBMISSION` | 47 and 46 headers, 2019 and 2026 | yes |
| `TRANSFER-ADD`, `TRANSFER-DELETE` | a party, and its `FILING-VALUES` | corrections of 2001 | no |
| `LEGAL-ENTITY-IDENTIFIER` | `COMPANY-DATA` | 11 headers of 2026 | no |
| `FLAWED` | `DOCUMENT` | 10 documents of 1996 | no |
| `PUBLIC-REL-DATE` | `SUBMISSION` | 6 corrections of 2026 | no |
| `DEPOSITOR`, `SECURITIZER` | `SUBMISSION`, as parties | 6 headers each, 2019 and 2026 | yes |
| `ISSUING-ENTITY-NAME` | `SUBMISSION` | 4 headers of 2019 | yes |
| `MA-I_INDIVIDUAL` | `SUBMISSION` | 2 headers of 2019; 745 in the survey | yes |
| `CATEGORY` | `SUBMISSION` | 1 header of 2019 | yes |
| `RULE`, `RULE-NAME`, `ITEM`, `ITEM-NUMBER`, `ITEM-PERIOD` | `SUBMISSION` | 525 in the survey (Form SD) | no |
| `PREVIOUS-ACCESSION-NUMBER` | `SUBMISSION` | 60 in the survey | yes |
| `RESOURCE-EXT-ISSUER` | `SUBMISSION` | 49 in the survey (Form SD) | no |
| `ISSUING_ENTITY` | `SUBMISSION`, as a party | 41 in the survey (ABS-15G) | yes |
| `ABS-SUB-ASSET-CLASS` | `SUBMISSION` | 7 in the survey | no |
| `CALENDAR-YEAR-ENDING` | `SUBMISSION` | 7 in the survey (NRSRO-CE) | no |
| `UNDERWRITER` | `SUBMISSION`, as a party | 1 in the survey (ABS-15G) | yes |
| `ACCEPTANCE-DATETIME` | `SEC-HEADER` | header files for filings of 2005 and later | no |

`SEC-HEADER`, `IMS-HEADER` and `HEADER-FILE` are added so that the header
files on SEC's site can be read: see [files.md](files.md). `HEADER-FILE` is not
SEC's tag.

## 4. Rules changed

| SEC's DTD | Here | Why |
|---|---|---|
| The parties in any order, but all of one kind together (`filer* & filed-by* & ...`) | Any order, mixed freely | 15 headers (13 of 2012, 2 of 2005) have a reporting owner, the issuer, then more reporting owners |
| `(correction, timestamp)?`: both or neither | Each optional | All 169 corrections of 2012, 2019 and 2026 have `<TIMESTAMP>` without `<CORRECTION>` |
| `filing-values?` | `filing-values*` | A fund that files under both the 1933 and the 1940 act has one for each (20 filers of 1996 and 2001) |
| `act` required; `file-number` and `film-number` both or neither | Each optional | 1,026 `FILING-VALUES` hold a form type alone; 11 have a file number and no film number |
| `owner-cik` in `existing-series-and-classes-contracts`, not in `series` | Optional in both | Each of 1,680 `SERIES` has its own `<OWNER-CIK>`; none stands before them |
| `series-and-classes-contracts-data` and `public-reference-acc` are declared and allowed nowhere | Allowed after the parties | 642 and 41 headers |
| A document must have `filename` and `text` | Both optional | The 1996 day has no file names. A correction may list a document without its text (274 documents, all in corrections of 1996, 2001 and 2005) |
| `text` must hold something | May be empty | It is empty once the document is taken out |

## 5. Order where it could not be seen

A DTD fixes the order of tags. Where two optional tags never stood in the same
header, the order between them could not be read from any header, and one had
to be chosen:

- `ORGANIZATION-NAME` (2026 only) and `RELATIONSHIP` (2001 to 2012 only): the
  first is put right after `ASSIGNED-SIC`, which it always follows.
- `ABS-SUB-ASSET-CLASS` and `ISSUING-ENTITY-NAME`, both after
  `ABS-ASSET-CLASS`: the sub-class is put first.
- `PREVIOUS-ACCESSION-NUMBER`, `CALENDAR-YEAR-ENDING`, `RULE` and
  `MA-I_INDIVIDUAL`, each seen between `PUBLIC-DOCUMENT-COUNT` and
  `FILING-DATE` and never with another, nor with `PERIOD` or `ITEMS`:
  `MA-I_INDIVIDUAL` stands after `ITEMS`, where SEC's specification lists it;
  the others stand first.
- `NEW-SERIES` before `NEW-CLASSES-CONTRACTS`, as SEC's DTD has them.
- `PUBLIC-REFERENCE-ACC`, `SERIES-AND-CLASSES-CONTRACTS-DATA` and the four
  `IS-...` tags after the parties, in that order.

A header that has them the other way round would be refused. If you meet one,
it is a fault of this DTD and worth an issue.

## 6. Left out

- **SEC's specification describes, and no header read has:**
  `<MULTI-ACCESSION-NUMBERS>` and `<WITHDRAWN-ACCESSION-NUMBER>`.
- **SEC's DTD declares, and no header read has:** `<SECURITIZER-FILE-NUMBER>`.
  It is kept, since SEC declares it.
- **Tags an older DTD of ours had**, patched in years ago when a day's filings
  failed, that nothing read here shows: `DESCRIPTION-OF-UPDATE`,
  `SERIAL-NUMBER`, `SECURITIZER-CIK`, `ISSUING-ENTITY-CIK`,
  `UNDER-WRITER-CIK`, `DEPOSITOR-FILE-NUMBER`, `ISSUING-ENTITY-FILE-NUMBER`
  and `IMG`. They may be in years not sampled. They are left out until a real
  header shows where they stand.

## 7. The one header that is not valid

`0000025885-96-000006`, filed 15 March 1996. Its tenth document carries SEC's
`<FLAWED>`, and after that document's text ends there is a `<PAGE>` tag and a
page number before `</DOCUMENT>`. Nothing may stand there. The DTD is left
strict, and the header is kept in `tests/fixtures/invalid/` with a test that
says so.
