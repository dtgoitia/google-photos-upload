import logging

from gpy.cli.cli import gpy_cli
from gpy.log import get_log_format, get_logs_output_path

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Running CLI command")

    gpy_cli()
    logger.info("CLI command ran to completion")
