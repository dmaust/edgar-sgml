import io
import tarfile

from headers import header, members


def test_a_documents_text_is_taken_out_and_nothing_else():
    submission = (
        b"<SUBMISSION>\n<ACCESSION-NUMBER>0000000000-26-000001\n<DOCUMENT>\n<TYPE>8-K\n"
        b"<TEXT>\n<html>the document</html>\n</TEXT>\n</DOCUMENT>\n</SUBMISSION>\n"
    )
    assert header(submission) == (
        b"<SUBMISSION>\n<ACCESSION-NUMBER>0000000000-26-000001\n<DOCUMENT>\n<TYPE>8-K\n"
        b"<TEXT>\n</TEXT>\n</DOCUMENT>\n</SUBMISSION>\n"
    )


def test_every_document_loses_its_text():
    submission = (
        b"<DOCUMENT>\n<TEXT>\none\n</TEXT>\n</DOCUMENT>\n<DOCUMENT>\n<TEXT>\ntwo\n</TEXT>\n"
    )
    assert header(submission) == (
        b"<DOCUMENT>\n<TEXT>\n</TEXT>\n</DOCUMENT>\n<DOCUMENT>\n<TEXT>\n</TEXT>\n"
    )


def test_lines_ended_by_a_bare_carriage_return():
    # How the archives of recent years end their lines.
    submission = b"<DOCUMENT>\r<TYPE>4\r<TEXT>\r<XML>\rdata\r</XML>\r</TEXT>\r</DOCUMENT>\r"
    assert header(submission) == b"<DOCUMENT>\r<TYPE>4\r<TEXT>\r</TEXT>\r</DOCUMENT>\r"


def test_lines_ended_by_carriage_return_and_line_feed():
    assert header(b"<TEXT>\r\nbody\r\n</TEXT>\r\n") == b"<TEXT>\r\n</TEXT>\r\n"


def test_text_begins_only_at_the_start_of_a_line():
    submission = b"<DESCRIPTION>the <TEXT> tag\n<TEXT>\nbody\n</TEXT>\n"
    assert header(submission) == b"<DESCRIPTION>the <TEXT> tag\n<TEXT>\n</TEXT>\n"


def test_a_text_tag_inside_the_text_changes_nothing():
    assert header(b"<TEXT>\n<TEXT> again\n</TEXT>\n</DOCUMENT>\n") == (
        b"<TEXT>\n</TEXT>\n</DOCUMENT>\n"
    )


def test_text_that_is_never_closed_ends_the_header():
    assert header(b"<TYPE>4\n<TEXT>\nno end\n") == b"<TYPE>4\n<TEXT>\n"


def test_a_header_without_documents_is_returned_as_it_is():
    file = b"<SEC-HEADER>0000000000-26-000001.hdr.sgml : 20260101\n<TYPE>4\n</SEC-HEADER>\n"
    assert header(file) == file


def test_members_of_a_daily_archive(tmp_path):
    archive = tmp_path / "20260101.nc.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for name, data in (("0000000000-26-000001.nc", b"<SUBMISSION>\n"), ("x.corr01", b"<A>")):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    assert list(members(archive)) == [
        ("0000000000-26-000001.nc", b"<SUBMISSION>\n"),
        ("x.corr01", b"<A>"),
    ]
