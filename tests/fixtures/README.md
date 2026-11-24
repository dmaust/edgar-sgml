# Real headers

Every file here is a header as SEC published it, byte for byte. They are public
records of EDGAR. A file's name is the filing's accession number.

| Folder | What it holds |
|---|---|
| `archive/{day}/` | 34 submissions from six of SEC's daily archives (`{day}.nc.tar.gz`), each with its documents' text taken out by `tools/headers.py` and nothing else changed. `.nc` is a new filing, `.corr01` a correction to an earlier one. Those of 2026 end their lines with a bare carriage return |
| `sec/` | 12 header files (`{accession}.hdr.sgml`) from filings' folders on www.sec.gov, as fetched |
| `invalid/` | The one header of the six days that is not valid: a filing of 1996 that SEC marked `<FLAWED>` |

They were chosen by program, not by hand: the smallest set of filings that
between them shows every tag in every place where the 14,876 headers of the six
days, and the 245 header files fetched from SEC, have it. A test checks that
they cover every element the DTD declares.

`.gitattributes` keeps git from changing their line ends.

Where there was a choice, a filing by a company or a fund was taken over one by
a person. Three of the headers still name a person, each with an office
address: that is what the filing is.
