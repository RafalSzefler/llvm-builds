import os
import shutil
import sys
import stat
import platform
from enum import Enum

from .termcolor import cprint


_CURRENT_OS = None

class OS(Enum):
    Windows = "windows"
    Linux = "linux"
    MacOS = "macos"

    @staticmethod
    def get_current() -> "OS":
        global _CURRENT_OS
        if _CURRENT_OS is None:        
            if sys.platform == "win32":
                _CURRENT_OS = OS.Windows
            elif sys.platform == "linux":
                _CURRENT_OS = OS.Linux
            elif sys.platform == "darwin":
                _CURRENT_OS = OS.MacOS
            else:
                raise Exception(f"Unsupported platform: {sys.platform}")
        return _CURRENT_OS

_CURRENT_ARCH = None
class Arch(Enum):
    X86 = "x86"
    X86_64 = "x86_64"
    ARM64 = "arm64"

    @staticmethod
    def get_current() -> "Arch":
        global _CURRENT_ARCH
        if _CURRENT_ARCH is None:
            machine = platform.machine().lower()
            if machine in {"amd64", "x86_64", "x64"}:
                _CURRENT_ARCH = Arch.X86_64
            elif machine in {"i386", "i686", "x86"}:
                _CURRENT_ARCH = Arch.X86
            elif machine in {"arm64", "aarch64", "aarch64_be"}:
                _CURRENT_ARCH = Arch.ARM64
            else:
                raise Exception(f"Unsupported architecture: {machine}")
        return _CURRENT_ARCH

def log_debug(message: str, with_newline: bool = True):
    log_tuple("[DEBUG] ", message, "light_grey", with_newline)

def log_info(message: str, with_newline: bool = True):
    log_tuple("[INFO] ", message, "light_cyan", with_newline)

def log_warning(message: str, with_newline: bool = True):
    log_tuple("[WARNING] ", message, "light_magenta", with_newline)

def log_error(message: str, with_newline: bool = True):
    log_tuple("[ERROR] ", message, "light_red", with_newline)

def log_success(message: str, with_newline: bool = True):
    log_tuple("[SUCCESS] ", message, "light_green", with_newline)

def log_tuple(first: str, second: str, color: str = "white", with_newline: bool = True):
    end = "\n" if with_newline else ""
    cprint(f"{first}", color, end="")
    print(second, end=end)

def _onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def rmdir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=_onerror)