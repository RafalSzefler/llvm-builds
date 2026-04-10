import os
import argparse
import subprocess

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
ARCHIVES_DIR = os.path.join(ROOT_DIR, "..", "archives")

from scripts.command_helpers import check_if_command_exists

def main(tag: str):
    if not check_if_command_exists("gh"):
        raise Exception("gh command not found")

    number_of_uploaded_archives = 0
    for file in os.listdir(ARCHIVES_DIR):
        if not file.endswith(".zip"):
            continue
        
        number_of_uploaded_archives += 1
        archive_path = os.path.join(ARCHIVES_DIR, file)
        cmd = ["gh", "release", "upload", tag, archive_path, "--clobber"]
        subprocess.run(cmd, check=True)

    print(f"Uploaded {number_of_uploaded_archives} archive(s) to GitHub")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='upload_to_github',
        description='Uploads LLVM archives to GitHub',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--tag', type=str, required=True, help='Release tag')
    args = parser.parse_args()
    main(args.tag)
