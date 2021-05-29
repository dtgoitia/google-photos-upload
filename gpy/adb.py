import logging
import subprocess

from gpy.log import get_log_format, get_logs_output_path

DeviceId = str

AQUARIS_PRO_X = "BL013003"


class AdbError(Exception):
    ...


# adb push "local/file.jpg" "remote/file.jpg"
# adb devices
def assert_is_device_connected(device_id: DeviceId = AQUARIS_PRO_X) -> None:
    cmd = "adb devices"
    completed_process = subprocess.run(cmd, capture_output=True, shell=True)

    if completed_process.returncode != 0:
        error_message = completed_process.stderr.decode("utf-8").strip()
        raise AdbError(error_message)

    output = completed_process.stdout.decode("utf-8").strip()
    assert output.startswith("List of devices attached")
    device_list = output.split("\n")[1:]
    device_ids = {device.split("\t")[0] for device in device_list}

    assert device_id in device_ids, f"Device {device_id} is not connected"


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


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    # logger.info("Running CLI command")

    assert_is_device_connected(device_id=AQUARIS_PRO_X)
    # logger.info("CLI command ran to completion")
