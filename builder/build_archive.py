import argparse
import sys
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SUPPORTED_LLVM_VERSIONS = ("19", "20", "21")

def main():
    llvm_version, force, verbose = _initialize()

    temp_dir = os.path.join(ROOT_DIR, ".temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    archives_dir = os.path.realpath(os.path.join(ROOT_DIR, "..", "archives"))

    from scripts.processor import build_archive
    exit_code = build_archive(llvm_version=llvm_version, temp_dir=temp_dir, archives_dir=archives_dir, force=force, verbose=verbose)
    sys.exit(exit_code)


def _initialize():
    major = sys.version_info[0]
    if major < 3:
        raise Exception("Python 3 is required")
    minor = sys.version_info[1]
    if minor < 9:
        raise Exception("Python 3.9 or higher is required")

    parser = argparse.ArgumentParser(
        prog='build_archive',
        description='Builds LLVM archives')
    parser.add_argument('--llvm-version', type=str, required=True, choices=SUPPORTED_LLVM_VERSIONS)
    parser.add_argument('--force', action='store_true', help='Forces rebuild of everything')
    parser.add_argument('--verbose', action='store_true', help='Prints actual traceback on error, instead of short messages')
    args = parser.parse_args()

    llvm_version = int(args.llvm_version)
    assert llvm_version >= 10 and llvm_version <= 10000

    return llvm_version, args.force, args.verbose

if __name__ == "__main__":
    main()
