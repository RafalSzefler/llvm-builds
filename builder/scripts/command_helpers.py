import shutil

def check_if_command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None
