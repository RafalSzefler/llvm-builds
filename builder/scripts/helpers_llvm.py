import os
import shutil
import subprocess

from .command_helpers import check_if_command_exists
from .helpers import log_info, log_warning, OS, Arch, rmdir, log_success
from .termcolor import cprint

CMD_COLOR = "light_yellow"

def _repo_path(flags: dict) -> str:
    llvm_version = flags["llvm_version"]
    temp_dir = flags["temp_dir"]
    return os.path.join(temp_dir, f"llvm-project-{llvm_version}")

def _llvm_cmake_dir(flags: dict) -> str:
    llvm_version = flags["llvm_version"]
    temp_dir = flags["temp_dir"]
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    return os.path.join(temp_dir, f"llvm-cmake-{llvm_version}-{os_name}-{arch_name}")

def _llvm_out_dir(flags: dict) -> str:
    llvm_version = flags["llvm_version"]
    temp_dir = flags["temp_dir"]
    os_name = OS.get_current().value
    arch_name = Arch.get_current().value
    return os.path.join(temp_dir, f"llvm-{llvm_version}-{os_name}-{arch_name}")

def download_llvm_repo(flags: dict):
    llvm_version = flags["llvm_version"]
    force = flags["force"]
    repo_path = _repo_path(flags)
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

def configure_and_build_llvm_project(flags: dict) -> str:
    _configure_llvm_project(flags)
    _build_llvm_project(flags)
    _validate_llvm_project(flags)
    return _llvm_out_dir(flags)

def _configure_llvm_project(flags: dict):
    repo_path = _repo_path(flags)
    llvm_cmake_dir = _llvm_cmake_dir(flags)
    llvm_out_dir = _llvm_out_dir(flags)
    if os.path.exists(llvm_cmake_dir):
        if not flags["force"]:
            log_info(f"Llvm already configured in {llvm_cmake_dir}. Use -force to reconfigure.")
            return
        log_warning(f"Llvm already configured in {llvm_cmake_dir}. Reconfiguring...")
        rmdir(llvm_cmake_dir)
    else:
        log_info(f"Configuring llvm to {llvm_cmake_dir}...")
    os.makedirs(llvm_cmake_dir)

    try:
        cmd = [
            "cmake",
            "-G",
            "Ninja",
            "-S",
            os.path.join(repo_path, "llvm"),
            "-B",
            llvm_cmake_dir,
            f"-DCMAKE_INSTALL_PREFIX={llvm_out_dir}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DLLVM_ENABLE_PROJECTS=llvm;clang;clang-tools-extra;lldb;lld",
            "-DLLVM_ENABLE_RUNTIMES=libc;compiler-rt",
            "-DLLVM_TARGETS_TO_BUILD=host",
            "-DLLVM_BUILD_DOCS=OFF",
            "-DLLVM_BUILD_TESTS=OFF",
            "-DLLVM_BUILD_EXAMPLES=OFF",
            "-DLLVM_INCLUDE_TESTS=OFF",
            "-DLLVM_INCLUDE_BENCHMARKS=OFF",
            "-DLLVM_INCLUDE_EXAMPLES=OFF",
        ]

        if OS.get_current() == OS.Windows:
            cmd.append("-DLLVM_ENABLE_DIA_SDK=OFF")

        cprint(_stringify_args(cmd), CMD_COLOR)
        subprocess.run(cmd, check=True)
    except:
        rmdir(llvm_cmake_dir)
        raise

    log_success(f"Llvm configured successfully to {llvm_cmake_dir}")

def _build_llvm_project(flags: dict):
    llvm_cmake_dir = _llvm_cmake_dir(flags)
    llvm_out_dir = _llvm_out_dir(flags)

    if os.path.exists(llvm_out_dir):
        if not flags["force"]:
            log_info(f"Llvm already built in {llvm_out_dir}. Use -force to rebuild.")
            return
        log_warning(f"Llvm already built in {llvm_out_dir}. Rebuilding...")
        rmdir(llvm_out_dir)
    else:
        log_info(f"Building llvm to {llvm_out_dir}...")
    os.makedirs(llvm_out_dir)

    cmd = [
        "ninja",
        "-C",
        llvm_cmake_dir,
        "install",
    ]
    cprint(_stringify_args(cmd), CMD_COLOR)

    try:
        subprocess.run(cmd, check=True)
    except:
        rmdir(llvm_out_dir)
        raise

    log_success(f"Llvm built successfully to {llvm_out_dir}")

def _validate_llvm_project(flags: dict):
    repo_path = _repo_path(flags)
    llvm_out_dir = _llvm_out_dir(flags)

    llvm_configs = ["llvm-config", "llvm-config.exe", "llvm_config", "llvm_config.exe"]
    llvm_config_path = None
    for llvm_config in llvm_configs:
        _config_path = os.path.join(llvm_out_dir, "bin", llvm_config)
        if os.path.exists(_config_path):
            llvm_config_path = _config_path
            break

    if llvm_config_path is None:
        raise Exception(f"Llvm config file not found in {llvm_out_dir}")

    log_info("Verifying Llvm installation by calling [llvm-config --version]...")
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
