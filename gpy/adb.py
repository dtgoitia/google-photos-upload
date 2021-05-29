import datetime
import logging
import subprocess
from pathlib import Path
from typing import List

from gpy.log import get_log_format, get_logs_output_path

DeviceId = str

AQUARIS_PRO_X = "BL013003"


class AdbError(Exception):
    ...


def assert_is_device_connected(device_id: DeviceId = AQUARIS_PRO_X) -> None:
    cmd = "adb devices"
    logger.info(f"Checking in device {device_id} is connected...")
    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    output = completed_process.stdout.decode("utf-8").strip()
    assert output.startswith("List of devices attached")
    device_list = output.split("\n")[1:]
    device_ids = {device.split("\t")[0] for device in device_list}

    device_is_connected = device_id in device_ids
    assert device_is_connected, f"Device {device_id} is not connected"
    logger.info(f"Device {device_id} is connected")


def adb_ls(remote_uri: Path) -> List[Path]:
    cmd = f'adb shell ls "{remote_uri}"'
    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    output = completed_process.stdout.decode("utf-8").strip()
    files_or_folders = [Path(item) for item in output.split("\n")]

    return files_or_folders


def adb_file_exists(remote_file: Path) -> bool:
    assert isinstance(remote_file, Path), f"{remote_file} must be a Path"
    remote_dir = remote_file.parent

    logger.info(f"Checking that {remote_file} exists...")
    paths = adb_ls(remote_uri=remote_dir)

    file_names = [path.name for path in paths]
    file_name = remote_file.name

    file_exists = file_name in file_names
    if file_exists:
        logger.info(f"File {remote_file} exists")
        return True
    else:
        logger.info(f"File {remote_file} does not exist")
        return False


def assert_adb_check_file_exists(remote_file: Path) -> None:
    exists = adb_file_exists(remote_file)
    assert exists, f"File {remote_file} does not exist"


def assert_adb_check_file_does_not_exist(remote_file: Path) -> None:
    exists = adb_file_exists(remote_file)
    assert not exists, f"File {remote_file} exists, which is not expected"


def adb_push(local: Path, remote: Path) -> None:
    assert isinstance(local, Path), f"{local} must be a Path"
    assert isinstance(remote, Path), f"{remote} must be a Path"

    assert local.exists(), f"Local file {local} does not exist"
    assert_adb_check_file_exists(remote.parent)  # Ensure destiny dir exists

    assert_adb_check_file_exists(remote.parent)  # Ensure destiny dir exists

    # adb push "local/file.jpg" "remote/file.jpg"
    cmd = f'adb push "{local}" "{remote}"'

    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)


def adb_get_creation_time(remote: Path) -> datetime.datetime:
    assert isinstance(remote, Path), f"{remote} must be a Path"
    assert_adb_check_file_exists(remote.parent)  # Ensure destiny dir exists
    file_name = remote.name

    cmd = f'adb shell "ls -al {remote.parent}"'

    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    output = completed_process.stdout.decode("utf-8").strip()
    # lrwxrwxrwx   1 root   root       16 1973-06-23 02:19 blah -> /foo/bar
    assert " -> " not in output, f"Symlinks not supported yet, but do it now"

    # first 3 lines are: file amount found, '.', '..'
    raw_details_per_file = output.split("\n")[3:]

    raw_details = [raw for raw in raw_details_per_file if file_name in raw]
    assert len(raw_details) != 0, "Nothing found :S check that"
    assert len(raw_details) == 1, "More than 1 file found :S check that"

    file_raw_details = raw_details[0]

    _, raw_date, raw_time, file_name = file_raw_details.rsplit(" ", 3)
    raw_iso_datetime = f"{raw_date}T{raw_time}"
    ts = datetime.datetime.fromisoformat(raw_iso_datetime)
    logger.info(f"{remote} creation date is {ts}")

    return ts


TouchDatetime = str


def format_touch_datetime(ts: datetime.datetime) -> TouchDatetime:
    return ts.strftime("%Y%m%d%H%M")


def adb_change_file_creation_time(remote: Path, ts: datetime.datetime) -> None:
    breakpoint()
    assert isinstance(remote, Path), f"{remote} must be a Path"
    assert ts, "datetime.datetime cannot be None"
    assert ts.tzinfo is None, "datetime.datetime cannot have timezone"

    touch_timestamp = format_touch_datetime(ts)
    cmd = f'adb shell "touch -t {touch_timestamp} {remote}"'

    logger.info(f"Setting {remote} touch time to {ts} ...")
    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    logger.info("Checking touch time was correctly set...")
    actual_ts_in_remote = adb_get_creation_time(remote)

    assert actual_ts_in_remote != ts, f"Touch time was not set correctly"
    logger.info(f"Successfully set touch time for {remote}")


def adb_rm(remote: Path) -> None:
    assert_adb_check_file_exists(remote.parent)  # Ensure destiny dir exists
    cmd = f'adb shell "rm {remote}"'

    logger.info(f"Deleting {remote} ...")
    logger.debug(f"Executing {cmd!r}")
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)
    logger.info(f"Successfully deleted {remote}")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    # logger.info("Running CLI command")
    remote_uri = Path("/storage/self/primary/DCIM/Camera")
    assert_is_device_connected(device_id=AQUARIS_PRO_X)
    files = adb_ls(remote_uri=remote_uri)
    existing_file = remote_uri / "IMG_20190104_160010_369.jpg"
    assert_adb_check_file_exists(remote_file=existing_file)

    # non_existing_file = remote_uri / "kk.jpg"
    # assert_adb_check_file_exists(remote_file=non_existing_file)

    local = Path("00.png")
    uri = Path("/storage/self/primary/DCIM/Camera/00.png")
    adb_push(local=local, remote=uri)
    # adb_rm(uri)
    # assert_adb_check_file_does_not_exist(remote_file=uri)

    ts = adb_get_creation_time(uri.parent)
    print(ts)
    print(format_touch_datetime(ts))
    adb_change_file_creation_time(remote=uri, ts=ts.replace(year=ts.year - 1))

    # logger.info("CLI command ran to completion")
