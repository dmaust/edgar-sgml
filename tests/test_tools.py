"""The tools, run on the fixtures."""

import json

import census
import tags_table
import validate
from conftest import FIXTURES, ROOT


def test_validate_counts_the_valid_and_names_the_errors(onsgmls, capsys):
    assert validate.main([str(FIXTURES / "archive"), str(FIXTURES / "sec")]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "46 headers: 46 valid, 0 not"

    assert validate.main([str(FIXTURES / "invalid")]) == 1
    said = capsys.readouterr().out
    assert said.splitlines()[0] == "1 headers: 0 valid, 1 not"
    assert 'document type does not allow element "PAGE" here' in said
    assert "19960315-0000025885-96-000006.nc, line 95" in said


def test_validate_writes_the_names_of_the_headers_that_fail(onsgmls, tmp_path, capsys):
    failed = tmp_path / "failed.txt"
    validate.main([str(FIXTURES / "invalid"), "--failed", str(failed), "--quiet"])
    assert failed.read_text().strip().endswith("19960315-0000025885-96-000006.nc")
    assert len(capsys.readouterr().out.splitlines()) == 1


def test_validate_reads_a_daily_archive(onsgmls, tmp_path, capsys):
    import tarfile

    archive = tmp_path / "20261120.nc.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted((FIXTURES / "archive" / "20261120").iterdir()):
            tar.add(path, arcname=path.name)
    assert validate.main([str(archive)]) == 0
    assert "10 headers: 10 valid, 0 not" in capsys.readouterr().out


def test_the_census_finds_nothing_the_dtd_lacks(capsys):
    dtd = ROOT / "dtd" / "edgar-submission.dtd"
    assert census.main([str(FIXTURES / "archive"), "--against", str(dtd)]) == 0
    assert "0 places the DTD does not have" in capsys.readouterr().out


def test_the_census_shows_what_secs_dtd_lacks(capsys):
    sec = ROOT / "sec" / "repaired" / "sec.dtd"
    assert census.main([str(FIXTURES / "archive"), "--against", str(sec)]) == 1
    said = capsys.readouterr().out
    assert "FILENAME in DOCUMENT" in said and "not declared" in said
    assert "OWNER-CIK in SERIES" in said and "not allowed there" in said


def test_the_census_counts_tags_places_and_years(tmp_path):
    count = census.Census()
    for path in sorted((FIXTURES / "archive" / "20261120").iterdir()):
        count.add(f"20261120.nc.tar.gz:{path.name}", path.read_bytes())
    record = count.record()
    assert record["headers"] == 10
    assert record["by_year"] == {"2026": 10}
    assert record["roots"] == {"SUBMISSION": 10}
    assert record["tags"]["ACCESSION-NUMBER"]["headers"] == 10
    assert "ORGANIZATION-NAME" in record["containers"]["COMPANY-DATA"]["children"]


def test_what_a_dtd_allows():
    model = census.allowed(ROOT / "dtd" / "edgar-submission.dtd")
    assert model["FORMER-COMPANY"] == {"FORMER-CONFORMED-NAME", "DATE-CHANGED"}
    assert "PHONE" in model["BUSINESS-ADDRESS"] and "PHONE" not in model["MAIL-ADDRESS"]
    assert model["FILER"] == model["ISSUING_ENTITY"]
    assert model["ACCESSION-NUMBER"] == set()


def test_the_page_of_tags_is_what_the_tool_would_write():
    # docs/tags.md is made by tools/tags_table.py; run it after changing the
    # DTD, the count or the notes.
    assert (ROOT / "docs" / "tags.md").read_text(encoding="utf-8") == tags_table.render()


def test_the_count_kept_with_the_docs_is_of_the_six_days():
    count = json.loads((ROOT / "docs" / "census.json").read_text(encoding="utf-8"))
    assert count["headers"] == 14876
    assert count["by_year"] == {
        "1996": 652,
        "2001": 715,
        "2005": 3074,
        "2012": 5849,
        "2019": 1763,
        "2026": 2823,
    }
