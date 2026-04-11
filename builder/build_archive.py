import argparse
import os
import sys

from scripts.command_helpers import check_if_command_exists
from scripts.helpers import OS
from scripts.helpers_windows import DRIVE
from scripts.processor import build_archive

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SUPPORTED_LLVM_VERSIONS = ("19", "20", "21", "22")

def main():
    flags = _initialize()
    exit_code = build_archive(flags)
    sys.exit(exit_code)

def _initialize() -> dict:
    major = sys.version_info[0]
    if major < 3:
        raise Exception("Python 3 is required")
    minor = sys.version_info[1]
    if minor < 9:
        raise Exception("Python 3.9 or higher is required")

    parser = argparse.ArgumentParser(
        prog='build_archive',
        description='Builds LLVM archives',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--llvm-version', type=str, required=True, choices=SUPPORTED_LLVM_VERSIONS)
    parser.add_argument('--temp-dir', type=str, required=False, help='Temporary directory to use for build artifacts. The default varies depending on the operating system.', default=_default_temp_dir())
    parser.add_argument('--out-dir', type=str, required=False, help='Output directory to use for final artifacts.', default=_default_out_dir())
    parser.add_argument('--force', action='store_true', help='Forces rebuild of everything')
    parser.add_argument('--verbose', action='store_true', help='Prints actual traceback on error, instead of short messages')
    args = parser.parse_args()

    llvm_version = int(args.llvm_version)
    assert llvm_version >= 10 and llvm_version <= 10000

    return {
        "llvm_version": llvm_version,
        "force": args.force,
        "verbose": args.verbose,
        "temp_dir": args.temp_dir,
        "archives_dir": args.out_dir,
    }

def _default_temp_dir() -> str:
    if OS.get_current() == OS.Windows:
        # On Windows we need short paths for some reason...
        temp_dir = os.path.join(DRIVE, "llvm-tmp")
    else:
        temp_dir = os.path.join(ROOT_DIR, "..", "temp")
    temp_dir = os.path.realpath(temp_dir)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

def _default_out_dir() -> str:
    out_dir = os.path.join(ROOT_DIR, "..", "archives")
    out_dir = os.path.realpath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    return out_dir

if __name__ == "__main__":
    main()
