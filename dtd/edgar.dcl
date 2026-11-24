<!SGML "ISO 8879:1986 (WWW)"
--
  SGML declaration for the headers of EDGAR submissions.

  It follows the declaration SEC prints in section 3.4 of the EDGAR Public
  Dissemination Service (PDS) Technical Specification, with the changes that
  real headers need. Each change is marked "CHANGED" below and explained in
  docs/differences.md.
--
CHARSET
         BASESET  "ISO 646-1983//CHARSET
                   International Reference Version (IRV)//ESC 2/5 4/0"
         DESCSET    0   9   UNUSED
                    9   2   9
                   11   2   UNUSED
                   13   1   13
                   14  18   UNUSED
                   32  95   32
                  127   1   UNUSED

CAPACITY PUBLIC   "ISO 8879:1986//CAPACITY Reference//EN"

SCOPE    DOCUMENT

SYNTAX
         SHUNCHAR CONTROLS 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
                           20 21 22 23 24 25 26 27 28 29 30 31 127 255
         BASESET  "ISO 646-1983//CHARSET
                   International Reference Version (IRV)//ESC 2/5 4/0"
         DESCSET  0 128 0

         FUNCTION RE          13
                  RS          10
                  SPACE       32
                  TAB SEPCHAR  9

         -- CHANGED: "_" is a name character (the tag MA-I_INDIVIDUAL), and
            "&" is not (SEC's print lists it). --
         NAMING   LCNMSTRT ""
                  UCNMSTRT ""
                  LCNMCHAR "-._"
                  UCNMCHAR "-._"
                  NAMECASE GENERAL YES
                           ENTITY  NO

         -- CHANGED: an ampersand in a header is only ever an ampersand
            ("AT&T INC", "MD&A"), so the two delimiters that would make a
            reference of it are spelled in a way no header uses. --
         DELIM    GENERAL  SGMLREF
                           ERO  "&&&"
                           CRO  "&&&#"
                  SHORTREF SGMLREF

         NAMES    SGMLREF

         -- CHANGED: NAMELEN 64 where SEC prints 40, which the longest tag
            of 2026 (FILED-PURSUANT-TO-GENERAL-INSTRUCTION-A2) just fits. --
         QUANTITY SGMLREF
                  NAMELEN    64
                  LITLEN   9000
                  ATTCNT     40
                  GRPCNT    350
                  GRPGTCNT  350

FEATURES
         MINIMIZE DATATAG NO  OMITTAG  YES  RANK     NO
                  SHORTTAG
                           STARTTAG EMPTY NO  UNCLOSED NO  NETENABL NO
                           ENDTAG   EMPTY NO  UNCLOSED NO
                           ATTRIB   DEFAULT NO  OMITNAME NO  VALUE NO
                  EMPTYNRM NO
                  IMPLYDEF ATTLIST NO  DOCTYPE YES  ELEMENT NO
                           ENTITY  NO  NOTATION NO
         LINK     SIMPLE  NO  IMPLICIT NO   EXPLICIT NO
         OTHER    CONCUR  NO  SUBDOC   NO   FORMAL   NO
                  URN     NO  KEEPRSRE NO   VALIDITY TYPE
                  ENTITIES REF ANY  INTEGRAL NO

APPINFO  NONE
>
