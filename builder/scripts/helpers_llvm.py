import os
import shutil
import subprocess

from .helpers import log_info, log_warning, OS, Arch, rmdir, log_success
from .termcolor import cprint

CMD_COLOR = "light_yellow"

def download_llvm_repo(llvm_version: int, temp_dir: str, force: bool) -> str:
    repo_path = os.path.join(temp_dir, f"llvm-project-{llvm_version}")
    if os.path.exists(repo_path):
        if not force:
            log_info(f"Llvm project already downloaded to {repo_path}. Use -force to download again.")
            return repo_path
        log_warning(f"Llvm project already downloaded to {repo_path}. Reinstalling...")
        rmdir(repo_path)
    else:
        log_info(f"Downloading llvm project to {repo_path}...")

    branch = f"release/{llvm_version}.x"
    cmd = [
        "git",
        "clone",
        "-b",
        branch,
        "--depth",
        "1",
        "https://github.com/llvm/llvm-project.git",
        repo_path
    ]
    cprint(_stringify_args(cmd), CMD_COLOR)
    subprocess.run(cmd, check=True)

    log_success(f"Llvm project downloaded successfully to {repo_path}")

    return repo_path

def configure_and_build_llvm_project(llvm_version: int, temp_dir: str, repo_path: str, force: bool) -> str:
    _configure_llvm_project(llvm_version, temp_dir, repo_path, force)
    _build_llvm_project(llvm_version, temp_dir, repo_path, force)
    _validate_llvm_project(llvm_version, temp_dir, repo_path, force)

    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    llvm_out_dir = os.path.join(temp_dir, f"llvm-{llvm_version}-{os_name}-{arch_name}")
    return llvm_out_dir

def _configure_llvm_project(llvm_version: int, temp_dir: str, repo_path: str, force: bool):
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    llvm_cmake_dir = os.path.join(temp_dir, f"llvm-cmake-{llvm_version}-{os_name}-{arch_name}")
    llvm_out_dir = os.path.join(temp_dir, f"llvm-{llvm_version}-{os_name}-{arch_name}")

    if os.path.exists(llvm_cmake_dir):
        if not force:
            log_info(f"Llvm already configured in {llvm_cmake_dir}. Use -force to reconfigure.")
            return
        log_warning(f"Llvm already configured in {llvm_cmake_dir}. Reconfiguring...")
        rmdir(llvm_cmake_dir)
    else:
        log_info(f"Configuring llvm to {llvm_cmake_dir}...")
    os.makedirs(llvm_cmake_dir)

    cmd = [
        "cmake",
        "-S",
        os.path.join(repo_path, "llvm"),
        "-B",
        llvm_cmake_dir,
        f"-DCMAKE_INSTALL_PREFIX={llvm_out_dir}",
        "-DLLVM_TARGETS_TO_BUILD=host",
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    cprint(_stringify_args(cmd), CMD_COLOR)
    try:
        subprocess.run(cmd, check=True)
    except:
        rmdir(llvm_cmake_dir)
        raise

    log_success(f"Llvm configured successfully to {llvm_cmake_dir}")

def _build_llvm_project(llvm_version: int, temp_dir: str, repo_path: str, force: bool):
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    llvm_cmake_dir = os.path.join(temp_dir, f"llvm-cmake-{llvm_version}-{os_name}-{arch_name}")
    llvm_out_dir = os.path.join(temp_dir, f"llvm-{llvm_version}-{os_name}-{arch_name}")

    if os.path.exists(llvm_out_dir):
        if not force:
            log_info(f"Llvm already built in {llvm_out_dir}. Use -force to rebuild.")
            return
        log_warning(f"Llvm already built in {llvm_out_dir}. Rebuilding...")
        rmdir(llvm_out_dir)
    else:
        log_info(f"Building llvm to {llvm_out_dir}...")
    os.makedirs(llvm_out_dir)

    cmd = [
        "cmake",
        "--build",
        llvm_cmake_dir,
        "--target",
        "install",
        "--config",
        "Release",
    ]
    cprint(_stringify_args(cmd), CMD_COLOR)

    try:
        subprocess.run(cmd, check=True)
    except:
        rmdir(llvm_out_dir)
        raise

    log_success(f"Llvm built successfully to {llvm_out_dir}")

def _validate_llvm_project(llvm_version: int, temp_dir: str, repo_path: str, force: bool):
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    llvm_out_dir = os.path.join(temp_dir, f"llvm-{llvm_version}-{os_name}-{arch_name}")

    llvm_configs = ["llvm-config", "llvm-config.exe", "llvm_config", "llvm_config.exe"]
    llvm_config_path = None
    for llvm_config in llvm_configs:
        _config_path = os.path.join(llvm_out_dir, "bin", llvm_config)
        if os.path.exists(_config_path):
            llvm_config_path = _config_path
            break

    if llvm_config_path is None:
        raise Exception(f"Llvm config file not found in {llvm_out_dir}")

    cmd = [
        llvm_config_path,
        "--version",
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def _stringify_args(args: list[str]) -> str:
    return ' '.join(_escape_arg(arg) for arg in args)

def _escape_arg(arg: str) -> str:
    arg = arg.replace('"', '\\"')
    if " " in arg:
        arg = f'"{arg}"'
    return arg
