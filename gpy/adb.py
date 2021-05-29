import logging
import subprocess
from pathlib import Path
from typing import List

from gpy.log import get_log_format, get_logs_output_path

DeviceId = str

AQUARIS_PRO_X = "BL013003"


class AdbError(Exception):
    ...


# def foo(device: DeviceId = AQUARIS_PRO_X) -> bool:
#     cmd_1 = "adb devices"
#     cmd_2 = f'exiftool -a "-AllDates<XMP:CreateDate" {path}'

#     completed_process_1 = subprocess.run(cmd_1, capture_output=True, shell=True)

#     if completed_process_1.returncode != 0:
#         error_message = completed_process_1.stderr.decode("utf-8").strip()
#         raise AdbError(error_message)

#     completed_process_2 = subprocess.run(cmd_2, capture_output=True, shell=True)

#     if completed_process_2.returncode != 0:
#         error_message = completed_process_2.stderr.decode("utf-8").strip()
#         raise AdbError(error_message)


# adb push "local/file.jpg" "remote/file.jpg"
# adb devices
def assert_is_device_connected(device_id: DeviceId = AQUARIS_PRO_X) -> None:
    cmd = "adb devices"
    logger.info(f"Checking in device {device_id} is connected...")
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
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    output = completed_process.stdout.decode("utf-8").strip()
    files_or_folders = [Path(item) for item in output.split("\n")]

    return files_or_folders


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    # logger.info("Running CLI command")

    assert_is_device_connected(device_id=AQUARIS_PRO_X)
    files = adb_ls(remote_uri="/storage/self/primary/DCIM/Camera")
    breakpoint()
    # logger.info("CLI command ran to completion")
