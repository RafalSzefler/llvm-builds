import os
import subprocess

from .command_helpers import check_if_command_exists
from .helpers import log_info, log_warning, log_success, rmdir
from .termcolor import cprint

CMD_COLOR = "light_yellow"

def _repo_path(flags: dict) -> str:
    temp_dir = flags["temp_dir"]
    return os.path.join(temp_dir, "ninja-repo")

def _ninja_dir(flags: dict) -> str:
    temp_dir = flags["temp_dir"]
    return os.path.join(temp_dir, "ninja")

def _ninja_bin_dir(flags: dict) -> str:
    return os.path.join(_ninja_dir(flags), "bin")

def _build_dir(flags: dict) -> str:
    temp_dir = flags["temp_dir"]
    return os.path.join(temp_dir, "ninja-build")

def verify_and_install_ninja(flags: dict):
    log_info("Verifying Ninja... ")
    if check_if_command_exists("ninja"):
        log_success("Ninja found!")
        return
    
    log_warning("No global Ninja. Checking locally...")
    ninja_dir = _ninja_dir(flags)
    if os.path.exists(ninja_dir):
        if not flags["force"]:
            log_info("Found local Ninja. Adding to PATH...")
            os.environ["PATH"] += os.pathsep + _ninja_bin_dir(flags)
            return
        log_warning("Local Ninja found, but force is true. Reinstalling...")
    else:
        log_info("No local Ninja found. Installing...")
    
    repo_path = _repo_path(flags)
    rmdir(repo_path)
    rmdir(ninja_dir)
    build_dir = _build_dir(flags)
    rmdir(build_dir)

    tag = "v1.13.1"
    cmd = [
        "git",
        "clone",
        "-b",
        tag,
        "--depth",
        "1",
        "https://github.com/ninja-build/ninja.git",
        repo_path
    ]
    cprint(_stringify_args(cmd), CMD_COLOR)
    subprocess.run(cmd, check=True)

    log_success("Ninja successfully downloaded, building...")

    try:
        log_info("Configuring Ninja...")
        cmd = [
            "cmake",
            f"-DCMAKE_INSTALL_PREFIX={ninja_dir}",
            "-B",
            build_dir,
            "-S",
            repo_path,
            "-DBUILD_TESTING=OFF",
            "-DCMAKE_BUILD_TYPE=Release",
        ]
        cprint(_stringify_args(cmd), CMD_COLOR)
        subprocess.run(cmd, check=True)

        log_info("Building Ninja...")
        cmd = [
            "cmake",
            "--build",
            build_dir,
            "--target",
            "install",
            "--config",
            "Release",
        ]
        cprint(_stringify_args(cmd), CMD_COLOR)

        subprocess.run(cmd, check=True)
    finally:
        rmdir(build_dir)
        rmdir(repo_path)

    os.environ["PATH"] += os.pathsep + _ninja_bin_dir(flags)

    log_info("Verifying Ninja installation by calling [ninja --version]...")
    cmd = ["ninja", "--version"]
    subprocess.run(cmd, check=True, capture_output=True)
    log_success("Ninja built successfully")

def _stringify_args(args: list[str]) -> str:
    return ' '.join(_escape_arg(arg) for arg in args)

def _escape_arg(arg: str) -> str:
    arg = arg.replace('"', '\\"')
    if " " in arg:
        arg = f'"{arg}"'
    return arg
