import datetime
from gpy.cli import compare_dates, \
                    get_paths_recursive, \
                    is_supported, \
                    scan_date, \
                    scan_gps
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


@pytest.mark.parametrize(('return_value', 'expected_result'), [
    ('random_date', {
        'filename_date': None,
        'match_date': False,
        'metadata_date': None,
        'path': 'random_path',
    }),
    (None, {
        'filename_date': None,
        'match_date': False,
        'metadata_date': None,
        'path': 'random_path',
    }),
])
def test_scan_date(read_datetime_mocked, return_value, expected_result):
    read_datetime_mocked.return_value = return_value

    actual_result = scan_date(file_path='random_path')

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
