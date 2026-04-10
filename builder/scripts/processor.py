import os
import subprocess
import sys
import zipfile
from pathlib import Path

from .command_helpers import check_if_command_exists
from .helpers import log_info, log_error, log_tuple, OS, Arch, log_debug, log_success, log_warning
from .helpers_git import verify_git
from .helpers_cmake import verify_and_install_cmake
from .helpers_ninja import verify_and_install_ninja
from .helpers_llvm import download_llvm_repo, configure_and_build_llvm_project
from .termcolor import cprint

def build_archive(flags: dict) -> int:
    log_info("Initializing...")
    print()

    if OS.get_current() == OS.Windows:
        _verify_windows_env()
    elif OS.get_current() == OS.MacOS:
        _verify_macos_env()

    log_tuple("Python version: ", sys.version)
    log_tuple("Operating system: ", OS.get_current().value)
    log_tuple("Architecture: ", Arch.get_current().value)
    for key, value in flags.items():
        log_tuple(f"{key}: ", str(value))
    print()
    
    try:
        _internal_build_archive(flags)
        return 0
    except Exception as exc:
        if flags["verbose"]:
            raise
        log_error("Caught unhandled exception [", with_newline=False)
        cprint(type(exc).__name__, "light_cyan", end="")
        print("]: ", end="")
        cprint(str(exc), "light_yellow")
        return 1

def _internal_build_archive(flags: dict):
    verify_git()
    verify_and_install_cmake(flags)
    verify_and_install_ninja(flags)
    download_llvm_repo(flags)
    out_path = configure_and_build_llvm_project(flags)
    _pack_llvm_output(out_path, flags)
    log_success("Build completed! Bye bye!")

def _pack_llvm_output(out_path, flags: dict):
    llvm_version = flags["llvm_version"]
    archives_dir = flags["archives_dir"]
    force = flags["force"]
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    archive_name = f"llvm-{llvm_version}-{os_name}-{arch_name}.zip"
    archive_path = os.path.join(archives_dir, archive_name)

    if os.path.exists(archive_path):
        if not force:
            log_info(f"Llvm output already packed to {archive_path}. Use -force to pack again.")
            return
        log_warning(f"Llvm output already packed to {archive_path}. Repacking...")
        os.remove(archive_path)
    else:
        log_info(f"Packing llvm output to {archive_path}...")

    base_dir = os.path.dirname(out_path)
    file_name = os.path.basename(out_path)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_LZMA) as zipf:
        _add_to_archive(zipf, base_dir, file_name)

    log_success(f"Llvm output packed successfully to {archive_path}")

def _add_to_archive(zipf: zipfile.ZipFile, base_dir: str, file_name: str):
    file_path = os.path.join(base_dir, file_name)
    log_debug(f"Adding {file_path} to archive...")
    zipf.write(file_path, file_name)
    if os.path.isdir(file_path):
        for file in os.listdir(file_path):
            new_path = os.path.join(file_name, file)
            _add_to_archive(zipf, base_dir, new_path)

def _verify_windows_env():
    log_info("Verifying Windows env...")
    expected_env_vars = ["INCLUDE", "LIB", "PATH"]
    env_enabled = True
    for var in expected_env_vars:
        if var not in os.environ:
            env_enabled = False
            break

    if env_enabled:
        env_enabled = check_if_command_exists("cl")

    if not env_enabled:
        raise Exception("MSVC environment not initialized. Please initialize MSVC environment by running VS shell, e.g. vcvars64.bat file.")

    log_success("Windows env looks ok!")

def _verify_macos_env():
    log_info("Verifying MacOS env...")
    if not check_if_command_exists("xcode-select"):
        raise Exception("xcode-select is needed on MacOS.")
    cmd = ["xcode-select", "--version"  ]
    subprocess.run(cmd, check=True, capture_output=True)
    log_success("MacOS env looks ok!")
