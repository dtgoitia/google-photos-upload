import datetime
from gpy.cli import compare_dates, \
                    get_paths_recursive, \
                    input_to_datetime, \
                    is_supported, \
                    scan_date, \
                    scan_gps, \
                    try_to_parse_date
import os
import pytest


# -----------------------------------------------------------------------------
# Fixtures


@pytest.fixture
def mock_dir(tmpdir) -> str:
    tmpdir.join('file_1.jpg').write('file content 1\n')
    tmpdir.join('file_2.png').write('file content 2\n')
    tmpdir.join('file_3.3gp').write('file content 3\n')
    tmpdir.join('file_4.mp3').write('file content 4\n')
    d1 = tmpdir.mkdir('directory_1')
    d1.join('file_5.wav').write('file content 5\n')
    d1.join('file_6.mp4').write('file content 6\n')

    return os.path.join(tmpdir.dirname, tmpdir.basename)


@pytest.fixture
def parse_mocked(mocker):
    return mocker.patch('gpy.cli.parse')


@pytest.fixture
def read_datetime_mocked(mocker):
    return mocker.patch('gpy.cli.exiftool.read_datetime')


@pytest.fixture
def read_gps_mocked(mocker):
    return mocker.patch('gpy.cli.exiftool.read_gps')


# -----------------------------------------------------------------------------
# Unit tests


@pytest.mark.parametrize(('file_path', 'output'), [
    ('file/absolute/path.jpg', True),
    ('file/absolute/path.png', True),
    ('file/absolute/path.mp4', True),
    ('file/absolute/path.3gp', True),
    ('file/absolute/path.gif', False),
])
def test_is_supported(file_path, output):
    assert is_supported(file_path) == output


def test_get_paths_recursive_directory(mock_dir):
    expected_paths = [
        os.path.join(mock_dir, 'file_3.3gp'),
        os.path.join(mock_dir, 'file_2.png'),
        os.path.join(mock_dir, 'file_1.jpg'),
        os.path.join(mock_dir, 'directory_1', 'file_6.mp4'),
    ]

    actual_paths = list(get_paths_recursive(root_path=mock_dir))

    for path in actual_paths:
        assert path in expected_paths


def test_get_paths_recursive_file(mock_dir):
    file_path = os.path.join(mock_dir, 'file_1.jpg')
    expected_paths = [file_path]

    actual_paths = list(get_paths_recursive(root_path=file_path))

    assert actual_paths == expected_paths


@pytest.mark.parametrize(
    ('path', 'read_datetime_return', 'parse_return', 'expected_result'), [
        # Filename has no date, no metadata or broken
        ('blah/foo.mp4', None, None, {
            'filename_date': None,
            'match_date': False,
            'metadata_date': None,
            'path': 'blah/foo.mp4',
        }),
        # Filename has no date, metadata OK found
        ('blah/foo.mp4', '2010-01-01 16:01:01', None, {
            'filename_date': None,
            'match_date': False,
            'metadata_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'path': 'blah/foo.mp4',
        }),
        # Filename parsed OK, but no metadata or broken
        ('blah/VID_20100101_160101_123.mp4', None, datetime.datetime(2010, 1, 1, 16, 1, 1), {
            'filename_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'match_date': False,
            'metadata_date': None,
            'path': 'blah/VID_20100101_160101_123.mp4',
        }),
        # Filename parsed OK, metadata OK found, but no match
        ('blah/VID_20100101_160101_123.mp4', '2012-02-02 17:02:02', datetime.datetime(2010, 1, 1, 16, 1, 1), {
            'filename_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'match_date': False,
            'metadata_date': datetime.datetime(2012, 2, 2, 17, 2, 2),
            'path': 'blah/VID_20100101_160101_123.mp4',
        }),
        # Filename parsed OK, metadata OK found, and both match
        ('blah/VID_20100101_160101_123.mp4', '2010-01-01 16:01:01', datetime.datetime(2010, 1, 1, 16, 1, 1), {
            'filename_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'match_date': True,
            'metadata_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'path': 'blah/VID_20100101_160101_123.mp4',
        }),
        # Filename parsed OK, metadata OK found with timezone +0h, and both match
        ('blah/VID_20100101_160101_123.mp4', '2010-01-01 16:01:01.00+00.00', datetime.datetime(2010, 1, 1, 16, 1, 1), {
            'filename_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'match_date': True,
            'metadata_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'path': 'blah/VID_20100101_160101_123.mp4',
        }),
        # Filename parsed OK, metadata OK found with timezone +5h, and both match
        ('blah/VID_20100101_160101_123.mp4', '2010-01-01 16:01:01.00+05.00', datetime.datetime(2010, 1, 1, 16, 1, 1), {
            'filename_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'match_date': True,
            'metadata_date': datetime.datetime(2010, 1, 1, 16, 1, 1),
            'path': 'blah/VID_20100101_160101_123.mp4',
        }),
    ])
def test_scan_date(read_datetime_mocked, parse_mocked, path, read_datetime_return, parse_return, expected_result):
    read_datetime_mocked.return_value = read_datetime_return
    parse_mocked.return_value = parse_return

    actual_result = scan_date(file_path=path)

    assert actual_result == expected_result


@pytest.mark.parametrize(('text', 'expected_result'), [
    (None, None),
    ('blah', None),
    ('2010-01-01 16:01:01', datetime.datetime(2010, 1, 1, 16, 1, 1)),
    ('2010-01-01 16:01:01.00+00.00', datetime.datetime(2010, 1, 1, 16, 1, 1)),
])
def test_try_to_parse_date(text, expected_result):
    actual_result = try_to_parse_date(text)

    assert actual_result == expected_result


@pytest.mark.parametrize(('return_value', 'expected_result'), [
    ('random_coords', {'path': 'random_path', 'gps': 'random_coords'}),
    (None, {'path': 'random_path'}),
])
def test_scan_gps(read_gps_mocked, return_value, expected_result):
    read_gps_mocked.return_value = return_value

    actual_result = scan_gps(file_path='random_path')

    assert actual_result == expected_result


@pytest.mark.parametrize(('date_a', 'date_b', 'expected_result'), [
    (
        datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
        datetime.datetime(2018, 12, 12, 1, 1, 1, 2),
        False
    ),
    (
        datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
        datetime.datetime(2018, 12, 12, 1, 1, 1, 1),
        True
    ),
    (None, datetime.datetime(2018, 12, 12, 1, 1, 1, 1), False),
    (None, None, False),
])
def test_compare_dates(date_a, date_b, expected_result):
    actual_result = compare_dates(date_a, date_b)

    assert actual_result == expected_result


@pytest.mark.parametrize(('input', 'expected_result'), [
    ('blah', None),
    ('2010-01-01 16:01:01', None),
    ('2010-01-01_16:01:01', datetime.datetime(2010, 1, 1, 16, 1, 1)),
    ('2010-01-01_16:01:01.02', datetime.datetime(2010, 1, 1, 16, 1, 1, 20000)),
])
def test_input_to_datetime(input, expected_result):
    actual_result = input_to_datetime(input)

    assert actual_result == expected_result
