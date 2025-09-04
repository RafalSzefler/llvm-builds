from .command_helpers import check_if_command_exists
from .helpers import log_info, log_success

def verify_git():
    log_info("Verifying git... ")
    if check_if_command_exists("git"):
        log_success("Git found!")
        return

    raise Exception("git not found. Please install git.")
