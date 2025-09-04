import os
import shutil
import zipfile
import tarfile
import stat
import urllib.request
import subprocess

from .command_helpers import check_if_command_exists
from .helpers import log_info, log_warning, log_success, OS, Arch, rmdir

def verify_and_install_cmake(temp_dir: str, force: bool):
    log_info("Verifying CMake... ")
    if check_if_command_exists("cmake"):
        log_success("CMake found!")
        return
    
    log_warning("No global CMake. Checking locally...")
    cmake_dir = _get_cmake_dir(temp_dir)
    cmake_bin_dir = _get_cmake_bin_dir(temp_dir)
    if os.path.exists(cmake_dir):
        if not force:
            log_info("Found local CMake. Adding to PATH...")
            os.environ["PATH"] += os.pathsep + cmake_bin_dir
            return
        log_warning("Local CMake found, but force is true. Reinstalling...")
        rmdir(cmake_dir)
    else:
        log_info("No local CMake found. Installing...")

    if (installer := _INSTALL_CMAKE_MAP.get(OS.get_current())) is not None:
        installer(temp_dir)
    else:
        raise Exception("Unsupported OS")

    os.environ["PATH"] += os.pathsep + cmake_bin_dir
    log_success("CMake installed successfully")

def _get_cmake_dir(temp_dir: str) -> str:
    return os.path.join(temp_dir, "cmake")

def _get_cmake_bin_dir(temp_dir: str) -> str:
    return os.path.join(_get_cmake_dir(temp_dir), "bin")

def _install_cmake_on_windows(temp_dir: str):
    arch = Arch.get_current()
    if arch == Arch.X86_64:
        cmake_url = "https://github.com/Kitware/CMake/releases/download/v4.1.0-rc3/cmake-4.1.0-rc3-windows-x86_64.zip"
    elif arch == Arch.ARM64:
        cmake_url = "https://github.com/Kitware/CMake/releases/download/v4.1.0-rc3/cmake-4.1.0-rc3-windows-arm64.zip"
    else:
        raise Exception("Unsupported architecture")

    cmake_zip_dst = os.path.join(temp_dir, "cmake.zip")
    urllib.request.urlretrieve(cmake_url, cmake_zip_dst)
    with zipfile.ZipFile(cmake_zip_dst, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    os.remove(cmake_zip_dst)

    cmake_dirs = []
    for name in os.listdir(temp_dir):
        if name.startswith("cmake-"):
            cmake_dirs.append(name)
    
    if len(cmake_dirs) != 1:
        raise Exception("Expected 1 CMake directory, got " + str(len(cmake_dirs)))
    
    os.rename(os.path.join(temp_dir, cmake_dirs[0]), _get_cmake_dir(temp_dir))

def _install_cmake_on_linux(temp_dir: str):
    arch = Arch.get_current()
    if arch == Arch.X86_64:
        cmake_url = "https://github.com/Kitware/CMake/releases/download/v4.1.0-rc4/cmake-4.1.0-rc4-linux-x86_64.tar.gz"
    elif arch == Arch.ARM64:
        cmake_url = "https://github.com/Kitware/CMake/releases/download/v4.1.0-rc4/cmake-4.1.0-rc4-linux-aarch64.tar.gz"
    else:
        raise Exception("Unsupported architecture")

    cmake_tar_dst = os.path.join(temp_dir, "cmake.tar.gz")
    urllib.request.urlretrieve(cmake_url, cmake_tar_dst)
    with tarfile.open(cmake_tar_dst, "r:gz") as tar:
        tar.extractall(temp_dir)
    os.remove(cmake_tar_dst)

    cmake_dirs = []
    for name in os.listdir(temp_dir):
        if name.startswith("cmake-"):
            cmake_dirs.append(name)
    
    if len(cmake_dirs) != 1:
        raise Exception("Expected 1 CMake directory, got " + str(len(cmake_dirs)))
    
    os.rename(os.path.join(temp_dir, cmake_dirs[0]), _get_cmake_dir(temp_dir))

def _install_cmake_on_macos(temp_dir: str):
    if not check_if_command_exists("hdiutil"):
        raise Exception("hdiutil not found. Please install hdiutil.")

    dmg_name = "cmake-4.0.3-macos-universal.dmg"
    cmake_url = f"https://github.com/Kitware/CMake/releases/download/v4.0.3/{dmg_name}"
    cmake_dmg_dst = os.path.join(temp_dir, dmg_name)
    urllib.request.urlretrieve(cmake_url, cmake_dmg_dst)

    mount_point = "/Volumes/cmake-macos"

    env = os.environ.copy()
    env["PAGER"] = "cat"
    cmd = ["hdiutil", "attach", "-quiet", "-mountpoint", mount_point, cmake_dmg_dst]
    subprocess.run(cmd, check=True, env=env)

    if not os.path.exists(mount_point):
        os.remove(cmake_dmg_dst)
        raise Exception(f"Failed to mount {dmg_name}")

    try:
        dst_dir = os.path.join(temp_dir, "cmake")
        cmd = ["cp", "-R", os.path.join(mount_point, "CMake.app", "Contents"), dst_dir]
        subprocess.run(cmd, check=True)
    finally:
        os.remove(cmake_dmg_dst)
        cmd = ["hdiutil", "detach", mount_point]
        subprocess.run(["hdiutil", "detach", mount_point], check=True)


_INSTALL_CMAKE_MAP = {
    OS.Windows: _install_cmake_on_windows,
    OS.Linux: _install_cmake_on_linux,
    OS.MacOS: _install_cmake_on_macos,
}
