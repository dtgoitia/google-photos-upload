import logging
from typing import List

from gpy.google_sheet import Worksheet
from gpy.log import get_log_format, get_logs_output_path
from gpy.types import Action, AppliedAction


def read_latest_local_gsheet() -> Worksheet:
    # TODO: dump state of GSheet just before pushing changes on 'make refresh'
    # and then just read it here
    ...


def read_latest_remote_gsheet() -> Worksheet:
    ...


def determine_actions(local, remote) -> List[Action]:  # List or Dict?
    # local: local copy of the GSheet state, which has been pushed in the past to the cloud
    # remote: most up to date GSheet state
    # changes to do = remote state - local state

    # find the differences between remote and local, and create a declarative list of
    # changes to be done, and return them, they will be applied elsewhere
    # pro: you can dump the list of changes to be done, like Terraform does
    ...


def apply_actions(actions: List[Action]) -> List[AppliedAction]:
    # Here you will need to actually edit files
    # ensure edited files are copied to /tmp/var or so before uploading, and log
    # the tmp paths for debugging

    # probably the editing logic needs a bit of love
    ...


def reconcile() -> None:
    local = read_latest_local_gsheet()
    remote = read_latest_remote_gsheet()
    actions = determine_actions(local, remote)
    # TODO: worth persisting actions before executing?
    # if dry_run:
    applied_actions = apply_actions(actions)
    # update gsheet? probably worth letting the 'refresh' bit to be done manually
    # in git when you push, your local state updates, no need to refetch :/
    # hmm... maybe do it automatically
    assert applied_actions


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logs_path = get_logs_output_path()
    log_format = get_log_format()
    logging.basicConfig(filename=logs_path, format=log_format, level=logging.DEBUG)

    logger.info("Refreshing Google Spreadsheet to show latest state")
    reconcile()
    logger.info("Finished refreshing Google Spreadsheet to show latest state")
