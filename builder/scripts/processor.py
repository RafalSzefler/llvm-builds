import os
import sys
import zipfile
from pathlib import Path

from .helpers import log_info, log_error, log_tuple, OS, Arch, log_debug, log_success, log_warning
from .helpers_git import verify_git
from .helpers_cmake import verify_and_install_cmake
from .helpers_llvm import download_llvm_repo, configure_and_build_llvm_project
from .termcolor import cprint

def build_archive(*args, **kwargs) -> int:
    verbose = kwargs.pop("verbose", False)
    try:
        _internal_build_archive(*args, **kwargs)
        return 0
    except Exception as exc:
        if verbose:
            raise
        log_error("Caught unhandled exception [", with_newline=False)
        cprint(type(exc).__name__, "light_cyan", end="")
        print("]: ", end="")
        cprint(str(exc), "light_yellow")
        return 1


def _internal_build_archive(llvm_version: int, temp_dir: str, archives_dir: str, force: bool):
    log_info("Initializing...")
    print()
    log_tuple("Python version: ", sys.version)
    log_tuple("Operating system: ", OS.get_current().value)
    log_tuple("Architecture: ", Arch.get_current().value)
    log_tuple("Temp directory: ", temp_dir)
    log_tuple("Archives directory: ", archives_dir)
    log_tuple("Force: ", str(force))
    log_tuple("LLVM version: ", str(llvm_version))
    print()

    verify_git()
    verify_and_install_cmake(temp_dir, force)
    repo_path = download_llvm_repo(llvm_version, temp_dir, force)
    out_path = configure_and_build_llvm_project(llvm_version, temp_dir, repo_path, force)
    _pack_llvm_output(llvm_version, out_path, archives_dir, force)
    log_success("Build completed! Bye bye!")

def _pack_llvm_output(llvm_version: int, out_path: str, archives_dir: str, force: bool):
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
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
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
