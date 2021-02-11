import hashlib
from pathlib import Path

from gpy.cli.meta import edit_metadata_datetime
from gpy.cli.scan import _scan_date
from gpy.exiftool import client as exiftool_client
from gpy.filenames import parse_datetime as datetime_parser


def get_file_hash(path: Path, root_dir: Path) -> str:
    unique_relative_path = path.relative_to(root_dir)
    as_bytes = bytes(unique_relative_path)
    hash = hashlib.sha256(as_bytes).hexdigest()
    return hash


def test_file_hash_is_constant_with_different_metadata(tmp_real_img: Path) -> None:
    root_dir = tmp_real_img.parent.parent

    report_before = _scan_date(exiftool_client, datetime_parser, tmp_real_img)
    assert not report_before.dates_match

    hash_before = get_file_hash(tmp_real_img, root_dir)

    edit_metadata_datetime(
        path=tmp_real_img,
        read_datetime_from_filename=True,
        input=None,
        backup=False,
    )

    report_after = _scan_date(exiftool_client, datetime_parser, tmp_real_img)
    assert report_after.dates_match

    hash_after = get_file_hash(tmp_real_img, root_dir)

    assert hash_before == hash_after
