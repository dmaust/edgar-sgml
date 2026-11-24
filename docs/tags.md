# The tags of a header

Every tag the DTD knows, in the order a header has them. Made by
`tools/tags_table.py`; do not edit it by hand.

- **Holds**: other tags (it has an end tag), text (it runs to the end of the line and
  has no end tag), or nothing (it is a flag).
- **Inside**: the tags it may stand in. What may stand in `SUBMISSION` may stand in
  `SEC-HEADER` and `IMS-HEADER` too. "Each party" is `FILER`, `FILED-BY`,
  `SUBJECT-COMPANY` and the others that hold a company's data.
- **What it is**: SEC's words from section 3.3 of its specification where it has any.
  A note in *italics* is this repository's, written from the headers that hold the tag.
- **Seen**: in how many of the 14,876 headers read from six days of SEC's archives
  (1996, 2001, 2005, 2012, 2019, 2026), in which of those years, and its commonest value.

| Tag | Holds | Inside | What it is | Seen |
|---|---|---|---|---|
| `SUBMISSION` | tags | (first tag) | Initial dissemination tag. Required. | 14,876 (1996 to 2026) |
| `SEC-HEADER` | tags | (first tag) | *The first tag of a `.hdr.sgml` file on www.sec.gov.* | in header files, which the count leaves out |
| `IMS-HEADER` | tags | (first tag) | *The first tag of a `.hdr.sgml` file for a filing of EDGAR's first years.* | in header files, which the count leaves out |
| `HEADER-FILE` | text | `IMS-HEADER`, `SEC-HEADER` | *Not SEC's tag: this DTD's name for the text that follows `<SEC-HEADER>` on its line, the file's own name and a date. Its tags are never written.* | in header files, which the count leaves out |
| `ACCEPTANCE-DATETIME` | text | `IMS-HEADER`, `SEC-HEADER` | *When EDGAR accepted the filing, as YYYYMMDDHHMMSS. In `.hdr.sgml` files only.* | in header files, which the count leaves out |
| `CORRECTION` | nothing | `SUBMISSION` | Identifies post acceptance correction transaction. This tag is only present for a correction to a filing. Optional. | 163 (1996 to 2005) |
| `TIMESTAMP` | text | `SUBMISSION` | Edgar Dissemination date-time, used for Post Acceptance Corrections only. Defines the time which the correction is disseminated by EDGAR, supplied by the R/A Subsystem. Optional. Format: YYYYMMDD:HHMMSS; Length: 15. | 332 (1996 to 2026); `19960315:100555` |
| `PAPER` | nothing | `SUBMISSION` | Identifies the submission as a Paper submission. Optional. | 504 (2005 to 2019) |
| `PRIVATE-TO-PUBLIC` | nothing | `SUBMISSION` | Identifies an SEC-approved private-to-public document dissemination. This tag is only present in a *.pr dissemination (a private-to-public dissemination). Optional. | 169 (2012 to 2026) |
| `ACCESSION-NUMBER` | text | `SUBMISSION` | EDGAR assigned identifier unique to each submission. Required. Format: (10-Char CIK)+"-"+YY+"-"+(6-Char sequence #); Length: 20. | 14,876 (1996 to 2026); `0000000000-96-001264` |
| `DELETION` | nothing | `FILING-VALUES`, `SUBMISSION`, each party | Identifies post acceptance correction filing deletion. This tag is present after accession number only when the filing is being deleted. Optional. | 27 (2005) |
| `TYPE` | text | `DOCUMENT`, `SUBMISSION` | Conformed type of submission being disseminated. Required. Length: 20. | 14,876 (1996 to 2026); `10-Q` |
| `CATEGORY` | text | `SUBMISSION` | Category of submission being disseminated. Optional. Length: 20. | 1 (2019); `STAFF LETTER` |
| `CONFIRMING-COPY` | nothing | `SUBMISSION` | This tag defines this submission as being a confirming copy to a paper submission. | 7 (1996 to 2012) |
| `PUBLIC-DOCUMENT-COUNT` | text | `SUBMISSION` | Number of PUBLIC documents in the submission, including rendered XBRL documents; if any. Length: 3. | 14,876 (1996 to 2026); `1` |
| `PREVIOUS-ACCESSION-NUMBER` | text | `SUBMISSION` | Tag to hold the accession number being amended for the form types ATS-N/MA, ATS-N/UA, ATS-N/CA, and ATS-N/OFA. Format: (10-Char CIK)+"-"+YY+"-"+(6-Char sequence #); Length: 20. | in none of the six days; in header files fetched from SEC |
| `CALENDAR-YEAR-ENDING` | text | `SUBMISSION` | *A year (`2025`), on a credit rating agency's annual certification (Form NRSRO-CE).* | in none of the six days; in header files fetched from SEC |
| `RULE` | tags | `SUBMISSION` | *On a specialized disclosure report (Form SD): the rule it is filed under, with the items of the form it answers.* | in none of the six days; in header files fetched from SEC |
| `RESOURCE-EXT-ISSUER` | text | `SUBMISSION` | *On a Form SD; `N` in the header seen. By its name, whether the filer is a resource extraction issuer.* | in none of the six days; in header files fetched from SEC |
| `REFERENCES-429` | text | `SUBMISSION` | Refers to a prospectus relating to two or more registration statements updated pursuant to Rule 429. The value represents the file numbers of the prior registration statements. Optional & Repeatable. Format: ###-#####[#][-XX[X][X]] where # is a number, [] is optional, and X is alphanumeric.; Length: 15. | 11 (1996 to 2012); `033-60572` |
| `PERIOD` | text | `SUBMISSION` | End date of reporting period of filing. Optional. Format: YYYYMMDD; Length: 8. | 11,078 (1996 to 2026); `19951231` |
| `DEPOSITOR-CIK` | text | `SUBMISSION` | The Central Index Key of the Depositor of an asset-backed securities offering. Optional Length: 10. | 47 (2019 to 2026); `0001182534` |
| `SPONSOR-CIK` | text | `SUBMISSION` | The Central Index Key of the Sponsor of an asset-backed securities offering. Optional Length: 10. | 46 (2019 to 2026); `0000833733` |
| `ITEMS` | text | `SUBMISSION` | Identifies 1 or more items declared in the filings. Optional & Repeatable. Applies to forms: 1-U, 1-U/A, 8-K, 8-K/A, 8-K12B, 8-K12B/A, 8-K12G3, 8- K12G3/A, 8-K15D5, 8-K15D5/A, ABS-15G, ABS-15G/A, D, D/A, REGDEX, REGDEX/A, SD, SD/A Format: #.##; Length: 4. | 2,277 (1996 to 2026); `9.01` |
| `MA-I_INDIVIDUAL` | text | `SUBMISSION` | This element specifies the filer supplied name of the individual for whom an MA-I or MA-I/A submission was submitted. Optional. Format: YYYYMMDD; Length: 8. | 2 (2019); `LAST,FIRST,MIDDLE,SUFFIX` |
| `FILING-DATE` | text | `SUBMISSION` | EDGAR assigned official filing date, or post acceptance new filing date (Post Acceptance Correction). Required. Format: YYYYMMDD; Length: 8. | 14,876 (1996 to 2026); `20010613` |
| `PUBLIC-REL-DATE` | text | `SUBMISSION` | *The day a filing that was first kept from the public was released, as YYYYMMDD. Seen beside `<PRIVATE-TO-PUBLIC>`.* | 6 (2026); `20261120` |
| `DATE-OF-FILING-DATE-CHANGE` | text | `SUBMISSION` | Date when the last Post Acceptance occurred. Optional. Format: YYYYMMDD; Length: 8. | 13,286 (1996 to 2026); `20120515` |
| `EFFECTIVENESS-DATE` | text | `SUBMISSION` | The effective date of the submission. Optional. Format: YYYYMMDD; Length: 8. | 4,368 (1996 to 2026); `20120515` |
| `ACTION-DATE` | text | `SUBMISSION` | The grant or issue date for Orders or Notices. Optional. Format: YYYYMMDD; Length: 8. | 28 (2012 to 2019); `20120515` |
| `RECEIVED-DATE` | text | `SUBMISSION` | The received date for Orders or Notices. Optional. Format: YYYYMMDD; Length: 8. | 28 (2012 to 2019); `20120515` |
| `SROS` | text | `SUBMISSION` | *A self-regulatory organization (an exchange) the filing names, one tag each: NYSE, NASD, AMEX, PSE, ...; NONE where there is none.* | 652 (1996); `NONE` |
| `GROUP-MEMBERS` | text | `SUBMISSION` | This identifies group members in this submission. Optional and repeatable. Length: 60. | 50 (1996 to 2026); `MACANDREWS & FORBES GROUP, INCORPORATED` |
| `ABS-RULE` | text | `SUBMISSION` | This element identifies the ABS rule selected for the submission. Optional. Length: 10. | 86 (2012 to 2026); `RULE-15GA1` |
| `PERIOD-START` | text | `SUBMISSION` | This identifies start date of reporting for the submission. Optional. Format: YYYYMMDD; Length: 8. | 329 (2012 to 2026); `20261231` |
| `NO-INITIAL-PERIOD-ACTIVITY` | text | `SUBMISSION` | Identifies if the Securitizer has any activity to report for the initial period pursuant to Rule 15Ga-1(c)(1). Optional. Length: 1. | 3 (2012); `N` |
| `NO-QUARTERLY-ACTIVITY` | text | `SUBMISSION` | Identifies if the Securitizer has any activity to report for the quarterly period pursuant to Rule 15Ga-1(c)(2)(i). Optional. Length: 1. | 76 (2012); `Y` |
| `NO-ANNUAL-ACTIVITY` | text | `SUBMISSION` | Identifies if the Securitizer has any activity to report for the annual period pursuant to Rule 15Ga-1(c)(2)(ii). Optional. Length: 1. | 76 (2012); `N` |
| `SECURITIZER-FILE-NUMBER` | text | `SUBMISSION` | *Declared in SEC's DTD and not described in its specification.* | in no header read |
| `REGISTERED-ENTITY` | text | `SUBMISSION` | This element identifies if the ABS-15Ga-2 submission is for a registered or unregistered entity. Optional. Length: 1. | 6 (2019 to 2026); `N` |
| `ABS-ASSET-CLASS` | text | `SUBMISSION` | This element specifies the ABS Asset Class for the submission. Optional. Length: 50. | 132 (2012 to 2026); `Commercial mortgages` |
| `ABS-SUB-ASSET-CLASS` | text | `SUBMISSION` | *A narrower class of the assets behind an asset-backed security. It follows `<ABS-ASSET-CLASS>`.* | in none of the six days; in header files fetched from SEC |
| `ISSUING-ENTITY-NAME` | text | `SUBMISSION` | This element specifies the filer supplied name of the Issuing Entity associated with the submission. Optional. Length: 150. | 4 (2019); `Residential Mortgage Loan Trust 2019-2` |
| `FILER` | tags | `SUBMISSION` | Initial tag for nested Filer information. Related data will be grouped together depending on submission type. The relevant tag will be reported for each grouping of company data. The tag is required and repeatable as a filing is being made on behalf of more than one Filer (person or entity). | 10,537 (1996 to 2026) |
| `FILED-BY` | tags | `SUBMISSION` | Initial tag for nested company information that filed the submission. The relevant tag is required as a filing is being made on behalf of more than one Filer (person or entity). | 717 (1996 to 2026) |
| `SERIAL-COMPANY` | tags | `SUBMISSION` | Initial tag for nested company information. Related data will be grouped together depending on submission type. The relevant tag will be reported for each grouping of company data. The relevant tag is optional and repeatable as a filing is being made on behalf of more than one Filer (person or entity). | 4 (2005) |
| `SUBJECT-COMPANY` | tags | `SUBMISSION` | Initial tag for nested company information. Related data will be grouped together depending on submission type. The relevant tag is optional and repeatable as a filing is being made on behalf of more than one Filer (person or entity). | 880 (1996 to 2026) |
| `REPORTING-OWNER` | tags | `SUBMISSION` | Initial tag for nested owner information. Related data will be grouped together depending on submission type. The relevant tag will be reported for each grouping of company data. The relevant tag is optional and repeatable as a filing is being made on behalf of more than one Filer (person or entity). | 3,574 (2001 to 2026) |
| `ISSUER` | tags | `SUBMISSION` | Initial tag for nested company information. Related data will be grouped together depending on submission type. The relevant tag is required as a filing is being made on behalf of more than one Filer (person or entity). | 3,413 (2005 to 2026) |
| `FILED-FOR` | tags | `SUBMISSION` | Initial tag for nested company information. Related data will be grouped together depending on submission type. The relevant tag will be reported for each grouping of company data. The relevant tag is optional and repeatable as a filing is being made on behalf of more than one Filer (person or entity). This tag nest is used only in dissem headers for SEC Uploads (<CONFORMED- SUBMISSION-TYPE>UPLOAD). | 46 (2012 to 2019) |
| `DEPOSITOR` | tags | `SUBMISSION` | Initial tag for nested Depositor information. Related data will be grouped together depending on submission type. The tag is optional. | 6 (2019 to 2026) |
| `SECURITIZER` | tags | `SUBMISSION` | Initial tag for nested Securitizer information. Related data will be grouped together depending on submission type. The tag is optional. | 6 (2019 to 2026) |
| `ISSUING_ENTITY` | tags | `SUBMISSION` | Initial tag for nested Issuing Entity information. Related data will be grouped together depending on submission type. The tag is optional. | in none of the six days; in header files fetched from SEC |
| `UNDERWRITER` | tags | `SUBMISSION` | Initial tag for nested Underwriter information. Related data will be grouped together depending on submission type. The tag is optional. | in none of the six days; in header files fetched from SEC |
| `PUBLIC-REFERENCE-ACC` | text | `SUBMISSION` | Present only in SEC UPLOADS. Reference to a specific submission (via Accession number). Optional. Format: (10-Char CIK)+"-"+YY+"-"+(6-Char sequence #); Length: 20. | 41 (2012 to 2019); `0001493152-18-010319` |
| `SERIES-AND-CLASSES-CONTRACTS-DATA` | tags | `SUBMISSION` | Initial tag for nested series and classes (contracts) information. Related data will be grouped together. The tag is required per relevant form type and investment company type. | 642 (2012 to 2026) |
| `IS-FILER-A-NEW-REGISTRANT` | text | `SUBMISSION` | Identifies if the primary registrant has been registered or regulated under the Investment Company Act for less than 12 calendar months preceding the filing. Optional. Length: 1. | 2 (2026); `Y` |
| `IS-FILER-A-WELL-KNOWN-SEASONED-ISSUER` | text | `SUBMISSION` | Identifies if the primary registrant meets the well-known seasoned issuer criteria noted in Rule 405 of Regulation C under the Securities Act of 1933 [17 CFR 230.405]. Optional. Length: 1. | 2 (2026); `N` |
| `FILED-PURSUANT-TO-GENERAL-INSTRUCTION-A2` | text | `SUBMISSION` | Identifies if the filing is pursuant to General Instruction A.2. Optional. Length: 1. | 2 (2026); `N` |
| `IS-FUND-24F2-ELIGIBLE` | text | `SUBMISSION` | Identifies if the fund is 24F-2 eligible. Optional. Length: 1. | 1 (2026); `N` |
| `DOCUMENT` | tags | `SUBMISSION` | Initial tag for nested document information. Required and repeatable. | 14,876 (1996 to 2026) |
| `TRANSFER-ADD` | nothing | `FILING-VALUES`, each party | *A flag in a correction that moves a filing from one company to another: it marks the party the filing now belongs to, and that party's filing values.* | 12 (2001) |
| `TRANSFER-DELETE` | nothing | `FILING-VALUES`, each party | *The other half of `<TRANSFER-ADD>`: it marks the party the filing is taken from.* | 12 (2001) |
| `RULE-NAME` | text | `RULE` | *The rule a Form SD is filed under, such as `13p-1` or `13q-1`.* | in none of the six days; in header files fetched from SEC |
| `ITEM` | tags | `RULE` | *One item of Form SD that the report answers, with the period it covers.* | in none of the six days; in header files fetched from SEC |
| `ITEM-NUMBER` | text | `ITEM` | *The number of the item, such as `1.01` or `2.01`.* | in none of the six days; in header files fetched from SEC |
| `ITEM-PERIOD` | text | `ITEM` | *The end of the period the item covers, as YYYYMMDD.* | in none of the six days; in header files fetched from SEC |
| `COMPANY-DATA` | tags | each party | Initial tag for nested company information, related data will be grouped together. The information enclosed in this grouping represent the latest company conformed data submitted to the SEC. Required in each Filer nest. | 14,876 (1996 to 2026) |
| `OWNER-DATA` | tags | each party | Initial tag for nested owner information, related data will be grouped together. The information enclosed in this grouping represents the latest owner conformed data submitted to the SEC. Required in each reporting- owner nest. | 3,413 (2005 to 2026) |
| `FILING-VALUES` | tags | each party | Initial tag for nested filing values. A form may be filed under more than 1 act. Required and Repeatable within each filer nest, except filed by | 14,876 (1996 to 2026) |
| `BUSINESS-ADDRESS` | tags | each party | Company Business Address. Optional. | 14,745 (1996 to 2026) |
| `MAIL-ADDRESS` | tags | each party | Company Mail Address. Optional. | 14,338 (1996 to 2026) |
| `FORMER-COMPANY` | tags | each party | Former company name. Optional and repeatable up to three times. | 6,932 (1996 to 2026) |
| `FORMER-NAME` | tags | each party | Former reporting owner name. Optional and repeatable up to three times. | 119 (2005 to 2026) |
| `CONFORMED-NAME` | text | `COMPANY-DATA`, `OWNER-DATA` | Filer/Registrant/Owner conformed name as it appears in the SEC's database. Required in each company data nest. Length: 150. | 14,876 (1996 to 2026); `FMR CORP` |
| `CIK` | text | `ACQUIRING-DATA`, `COMPANY-DATA`, `OWNER-DATA`, `TARGET-DATA` | Filer/Registrant Central Index Key, which was supplied by the SEC following receipt of the Form ID. Required in each company data nest and Merger series and classes (contracts) information. Length: 10. | 14,876 (1996 to 2026); `0000315066` |
| `ASSIGNED-SIC` | text | `COMPANY-DATA`, `OWNER-DATA` | Company's Standard Industrial Classification code. Required in each company data nest. Length: 4. | 10,834 (1996 to 2026); `6021` |
| `ORGANIZATION-NAME` | text | `COMPANY-DATA`, `OWNER-DATA` | *The SEC office the company is assigned to, as a number and a name (`02 Finance`, `07 Trade & Services`). Present and empty for a filer that has none.* | 2,822 (2026); `02 Finance` |
| `RELATIONSHIP` | text | `COMPANY-DATA`, `OWNER-DATA` | Identifies the filer’s relationship with the company, e.g., Director, Officer etc. Length: 10. | 46 (2001 to 2012); `DIRECTOR` |
| `IRS-NUMBER` | text | `COMPANY-DATA`, `OWNER-DATA` | Filer/Registrant/Subject Company/Issuer IRS number. Required in each subject company tag nest. Serial Company IRS Number is not disseminated. Format: 99-9999999; Length: 10. | 14,583 (1996 to 2026); `161144965` |
| `STATE-OF-INCORPORATION` | text | `COMPANY-DATA`, `OWNER-DATA` | Company State of Incorporation. Optional. Length: 2. | 13,213 (1996 to 2026); `DE` |
| `FISCAL-YEAR-END` | text | `COMPANY-DATA`, `OWNER-DATA` | Company Fiscal Year End. Optional. Format: MMDD; Length: 4. | 13,598 (1996 to 2026); `1231` |
| `LEGAL-ENTITY-IDENTIFIER` | text | `COMPANY-DATA`, `OWNER-DATA` | *The company's Legal Entity Identifier (LEI), 20 characters.* | 11 (2026); `213800ZNSR7AIJZ2J557` |
| `FORM-TYPE` | text | `FILING-VALUES` | Used to identify the form type filed for each filer. Required by Filer. Length: 10. | 14,876 (1996 to 2026); `8-K` |
| `ACT` | text | `FILING-VALUES` | Identification of the act(s) under which certain IM filings are made. The form type may be filed under more than one act. Required in each filing values tag nest. Length: 2. | 14,736 (1996 to 2026); `34` |
| `FILE-NUMBER` | text | `FILING-VALUES` | SEC Conformed File Number. Required in each filing values tag nest. Format: ###-#####[#][-XX[X][X]] where # is a number, [] is optional, and X is alphanumeric.; Length: 15. | 14,736 (1996 to 2026); `001-04105` |
| `FILM-NUMBER` | text | `FILING-VALUES` | Also known as the Document Control Number (DCN) Microfilm number assigned to submission. Required for each Subject Company or Registrant, or Owner, not for Filed By or Issuer. Format: YY######; Length: 10. | 14,731 (1996 to 2026); `96535430` |
| `ADDRESS-IS-A-NON-US-LOCATION` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | *`YES` on an address outside the United States.* | 171 (2026); `YES` |
| `STREET1` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | Company Business Street 1. Optional. Length: 40. | 14,868 (1996 to 2026); `82 DEVONSHIRE ST` |
| `STREET2` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | Company Business Street 2. Optional. Length: 40. | 8,505 (1996 to 2026); `SUITE 400` |
| `CITY` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | Company Business City. Optional. Length: 30. | 14,865 (1996 to 2026); `NEW YORK` |
| `STATE` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | Company Business State. Optional. Length: 2. | 14,739 (1996 to 2026); `NY` |
| `NON-US-STATE-TERRITORY` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | *For an address outside the United States, a code from EDGAR's table of states and countries. It stands where `<STATE>` would.* | 33 (2026); `N4` |
| `PROVINCE-COUNTRY` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | *For an address outside the United States, the code of its province or country in EDGAR's table of states and countries.* | 171 (2026); `A6` |
| `ZIP` | text | `BUSINESS-ADDRESS`, `MAIL-ADDRESS` | Company Business Zip. Optional. Length: 10. | 14,790 (1996 to 2026); `10017` |
| `PHONE` | text | `BUSINESS-ADDRESS` | Company Business Phone. Optional. Length: 12. | 14,548 (1996 to 2026); `6175706339` |
| `FORMER-CONFORMED-NAME` | text | `FORMER-COMPANY`, `FORMER-NAME` | Former Company name. Required in each former company tag nest. Length: 150. | 6,985 (1996 to 2026); `NCNB CORP` |
| `DATE-CHANGED` | text | `FORMER-COMPANY`, `FORMER-NAME` | Date when company name was changed. Required in each former company tag nest. Format: YYYYMMDD; Length: 8. | 6,985 (1996 to 2026); `19920703` |
| `NEW-SERIES-AND-CLASSES-CONTRACTS` | tags | `SERIES-AND-CLASSES-CONTRACTS-DATA` | Initial tag for identifying new series and classes (contracts) information. Related data will be grouped together. The tag is optional per relevant form type. | 22 (2012 to 2026) |
| `EXISTING-SERIES-AND-CLASSES-CONTRACTS` | tags | `SERIES-AND-CLASSES-CONTRACTS-DATA` | Initial tag for identifying existing series and classes (contracts) information. Related data will be grouped together. The tag is optional per relevant form type. | 615 (2012 to 2026) |
| `MERGER-SERIES-AND-CLASSES-CONTRACTS` | tags | `SERIES-AND-CLASSES-CONTRACTS-DATA` | Initial tag for identifying merger series and classes (contracts) information. Related data will be grouped together. The tag is optional per relevant form type. | 5 (2026) |
| `OWNER-CIK` | text | `EXISTING-SERIES-AND-CLASSES-CONTRACTS`, `NEW-SERIES-AND-CLASSES-CONTRACTS`, `SERIES` | Series and Classes (Contracts) Owner Central Index Key, which was supplied by the SEC following receipt of the Form ID. Required for identifying new and existing series and classes (contracts). Length: 10. | 637 (2012 to 2026); `0000088525` |
| `NEW-SERIES` | tags | `NEW-SERIES-AND-CLASSES-CONTRACTS` | Initial tag for identifying new series information. Required and repeatable for New Series and Classes Contracts. | 19 (2019 to 2026) |
| `NEW-CLASSES-CONTRACTS` | tags | `NEW-SERIES-AND-CLASSES-CONTRACTS` | Initial tag for identifying new classes (contracts) information. Required and repeatable for New Series and Classes Contracts. | 3 (2012 to 2026) |
| `SERIES` | tags | `ACQUIRING-DATA`, `EXISTING-SERIES-AND-CLASSES-CONTRACTS`, `TARGET-DATA` | Initial tag for identifying existing and merger series information. Required and repeatable for Existing and Merger Series and Classes Contracts. | 620 (2012 to 2026) |
| `MERGER` | tags | `MERGER-SERIES-AND-CLASSES-CONTRACTS` | Initial tag for identifying merger series and classes (contracts) information. Required and repeatable for Merger Series and Classes Contracts. | 5 (2026) |
| `SERIES-ID` | text | `NEW-CLASSES-CONTRACTS`, `NEW-SERIES`, `SERIES` | Series ID number, which was supplied by the SEC following receipt of new series information. Required for all scenarios (new, existing, merger) for series and classes (contracts). Format: S#########; Length: 10. | 642 (2012 to 2026); `S000009770` |
| `SERIES-NAME` | text | `NEW-CLASSES-CONTRACTS`, `NEW-SERIES`, `SERIES` | Series name, which was supplied by the filer during receipt new series information. Required for all scenarios (new, existing, merger) for series and classes (contracts). Length: 150. | 642 (2012 to 2026); `U.S. INTERMEDIATE BOND` |
| `CLASS-CONTRACT` | tags | `NEW-CLASSES-CONTRACTS`, `NEW-SERIES`, `SERIES` | Initial tag for identifying new, existing, or merger class (contract) information. Required and repeatable. | 642 (2012 to 2026) |
| `CLASS-CONTRACT-ID` | text | `CLASS-CONTRACT` | Class (contract) ID number, which was supplied by the SEC following receipt of new class (contract) information. Required for all scenarios (new, existing, merger) for series and classes (contracts). Format: C#########; Length: 10. | 642 (2012 to 2026); `C000026841` |
| `CLASS-CONTRACT-NAME` | text | `CLASS-CONTRACT` | Class (contract) name, which was supplied by the filer during receipt of new class (contract) information. Required for all scenarios (new, existing, merger) for series and classes (contracts). Length: 150. | 642 (2012 to 2026); `Class A` |
| `CLASS-CONTRACT-TICKER-SYMBOL` | text | `CLASS-CONTRACT` | Class (contract) ticker symbol, which was supplied by the filer during receipt of existing class (contract) information. Optional for all existing and merger scenarios for series and classes (contracts). Length: 10. | 355 (2012 to 2026); `SIUSX` |
| `ACQUIRING-DATA` | tags | `MERGER` | Initial tag for identifying the acquiring series and class (contract) information as part of reporting merger information. Required for Merger Series and Classes Contracts. | 5 (2026) |
| `TARGET-DATA` | tags | `MERGER` | Initial tag for identifying the target series and class (contract) information as part of reporting merger information. Required and repeatable for Merger Series and Classes Contracts. | 5 (2026) |
| `SEQUENCE` | text | `DOCUMENT` | Document sequence number. Required in each document tag nest. Length: 3. | 14,876 (1996 to 2026); `1` |
| `FILENAME` | text | `DOCUMENT` | Document File name. Required in each document tag nest. Length: 32. | 14,224 (2001 to 2026); `ps2866.htm` |
| `DESCRIPTION` | text | `DOCUMENT` | Describes what is contained in the document. Optional. Length: 255. | 11,561 (1996 to 2026); `8-K` |
| `FLAWED` | nothing | `DOCUMENT` | *A flag on a document. SEC's specification does not say what it marks.* | 10 (1996) |
| `TEXT` | tags | `DOCUMENT` | Identifies beginning of document text. Required in each document tag nest. | 14,713 (1996 to 2026) |
