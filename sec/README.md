# SEC's own text

| File | What it is |
|---|---|
| `pds_dissemination_spec.pdf` | The EDGAR Public Dissemination Service (PDS) Technical Specification, as fetched from <https://www.sec.gov/files/info/edgar/specifications/pds_dissemination_spec.pdf> on 23 November 2026. The PDF is dated December 2020 |
| `dtd-as-printed.txt` | The SGML declaration and DTD of its section 3.4, as printed. Only the page numbers are taken out. No parser accepts it |
| `tags.json` | The 117 tag definitions of its section 3.3, as data: each tag's name, description, length, format and limits, in the specification's words |
| `repaired/` | The declaration and DTD with only what a parser refuses put right, to measure how far SEC's DTD describes what SEC sends. [docs/differences.md](../docs/differences.md) lists the repairs and the result |

The first is SEC's file. The second and third are made from it by
`tools/from_spec.py` and are not edited by hand, so that a newer edition of the
specification can be put in its place and compared. `repaired/` was written by
hand from `dtd-as-printed.txt`.

The specification is written for subscribers to SEC's dissemination feed. The
daily archives that anyone may download hold the same submissions in the same
form.

These are works of the United States government and are not under this
repository's license.
