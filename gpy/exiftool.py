# TODO:
# Create an enum to hold the types.
# Create funciton to detect the filename format
# Create 1 function per filename format type, to extract the date
# Create a wrapper function which detects via filename and writes the metadata

import click
import datetime
import re
import subprocess


# def exiftool() -> None:
#     write_geolocation('test.jpg', north=43.0, west=-79.0)
#     write_datetime('test.jpg', year=2018, month=12, day=31, h=20, m=55, s=42, ms=2, timezone=-5)
#     parse_date_from_filename('IMG_20190101_085024_277.jpg')

def clean_metadata(file_path: str, no_backup=False) -> bool:
    """Erase all metadata in the file.

    :param file_path: path of the file
    :param no_backup: if true, don't do backup copy of the file
    :type file_path: str
    :type no_backup: bool
    :returns: true if successful, otherwise false
    :rtype: bool
    """
    shell_instruction = f'exiftool -all= {file_path}'
    if no_backup:
        shell_instruction += ' -overwrite_original'
    completed_process = subprocess.run(shell_instruction, capture_output=True, shell=True)

    if completed_process.returncode is not 0:
        error_message = f"Writting date and time to '{file_path}' >>> "
        error_message += completed_process.stderr.decode('utf-8').rstrip('\n')
        click.echo(error_message)
        return False
    return True


def format_tz(tz: int) -> str:
    """Return timezone formatted.

    Example:
      tz = -5  -->  '-05:00'
      tz = 3   -->  '+03:00'

    :param tz: timezone
    :type tz: int
    :returns: timezone correctly formatted
    :rtype: str
    """
    if tz < -12:
        raise Exception('Timezone cannot be smaller than -12:00')
    if tz > 14:
        raise Exception('Timezone cannot be higher than +14:00')
    result = '+' if tz >= 0 else '-'
    absolute_tz = str(abs(tz))
    if len(absolute_tz) < 2:
        absolute_tz = f'0{absolute_tz}'
    result += absolute_tz
    result += ':00'
    return result


def parse_date_from_filename(file_path: str) -> datetime.datetime:
    """Return datetime as per file name.

    :param file_path: path of the file
    :type file_path: str
    :returns: date and time as per file name
    :rtype: datetime.datetime
    """
    search_results = re.findall(r'IMG_([0-9]{8}_[0-9]{6})_([0-9]{3})', file_path)
    if len(search_results) == 0:
        raise Exception(f"File name pattern not recognized while parsing date from '{file_path}' file...")
    search_results = re.findall(r'IMG_([0-9]{8}_[0-9]{6})_([0-9]{3})', file_path)[0]
    file_datetime = search_results[0]
    file_datetime_miliseconds = search_results[1]
    result = datetime.datetime.strptime(file_datetime, '%Y%m%d_%H%M%S')
    result = result.replace(microsecond=1000 * int(file_datetime_miliseconds))
    return result


def read_datetime(file_path: str):
    """Return Date/Time from file, if any."""
    shell_instruction = f'exiftool -AllDates {file_path}'
    completed_process = subprocess.run(shell_instruction, capture_output=True, shell=True)

    if completed_process.returncode is not 0:
        error_message = f"Writting date and time to '{file_path}' >>> "
        error_message += completed_process.stderr.decode('utf-8').rstrip('\n')
        click.echo(error_message)
        return False

    result = completed_process.stdout.decode('utf-8')
    result = result.split('\n')[0]
    result = result.split(':')[1:]
    result = ':'.join(result)
    result = result.strip()
    return result


def read_gps(file_path: str):
    """Return GPS coordinates from file, if any."""
    raise NotImplementedError('TODO > find out how pull GPS data with exiftool')


def write_datetime(file_path: str, *, ts: datetime.datetime, timezone=0, no_backup=False) -> bool:
    """Write Date/Time to file.

    The Date/Time tag refers to the moment when the image/video was captured.

    :param file_path: path of the file
    :param ts: date and time when the file was captured
    :param timezone: timezone of the capture
    :param no_backup: if true, don't do backup copy of the file
    :type file_path: str
    :type ts: datetime.datetime
    :type timezone: int
    :type no_backup: bool
    :returns: true if successful, otherwise false
    :rtype: bool
    """
    date_time = ts.strftime('%Y:%m:%d %H:%M:%S')
    ms = ts.microsecond
    tz = format_tz(timezone)
    formatted_date_time = f"{date_time}.{ms:02}{tz}"

    shell_instruction = f'exiftool'
    shell_instruction += f' -AllDates="{formatted_date_time}"'
    shell_instruction += f' {file_path}'
    if no_backup:
        shell_instruction += ' -overwrite_original'
    completed_process = subprocess.run(shell_instruction, capture_output=True, shell=True)

    if completed_process.returncode is not 0:
        error_message = f"Writting date and time to '{file_path}' >>> "
        error_message += completed_process.stderr.decode('utf-8').rstrip('\n')
        click.echo(error_message)
        return False
    return True


def write_geolocation(file_path: str, *, north: float, west: float, no_backup: bool) -> bool:
    """Write GPS coordinates to file.

    :param file_path: path of the file
    :param north: latitude, North based
    :param west: longitude, West based
    :param no_backup: if true, don't do backup copy of the file
    :type file_path: str
    :type north: float
    :type west: float
    :type no_backup: bool
    :returns: true if successful, otherwise false
    :rtype: bool
    """
    shell_instruction = f'exiftool -XMP:GPSLatitude="{north}" -XMP:GPSLongitude="{west}" -GPSLatitudeRef="North" -GPSLongitudeRef="West" {file_path}'
    if no_backup:
        shell_instruction += ' -overwrite_original'
    completed_process = subprocess.run(shell_instruction, capture_output=True, shell=True)

    if completed_process.returncode is not 0:
        error_message = f"Writting GPS coordinates to '{file_path}' >>> "
        error_message += completed_process.stderr.decode('utf-8').rstrip('\n')
        click.echo(error_message)
        return False
    return True
