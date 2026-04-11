import os
import pathlib
import subprocess

from .command_helpers import check_if_command_exists
from .helpers import Arch

DRIVE = pathlib.Path.cwd().anchor

_PROGRAM_FILES = [
    os.environ.get("ProgramFiles(x86)", os.path.join(DRIVE, "Program Files (x86)")),
    os.environ.get("ProgramFiles", os.path.join(DRIVE, "Program Files"))
]

_VSWHERE_REL_PATH = os.path.join("Microsoft Visual Studio", "Installer", "vswhere.exe")
_VCVARSALL_REL_PATH = os.path.join("VC", "Auxiliary", "Build", "vcvarsall.bat")
_CMD = "cmd"


def validate_windows_env():
    for expected_var in ["INCLUDE", "LIB", "PATH"]:
        if expected_var not in os.environ:
            raise Exception(f"MSVC environment not initialized: [{expected_var}] env variable not found")

    if not check_if_command_exists("cl"):
        raise Exception("MSVC environment not initialized: [cl] command not found")

def update_windows_env():
    if not check_if_command_exists(_CMD):
        raise Exception(f"MSVC environment not initialized: {_CMD} shell not found")
    vswhere = _search_for_vswhere()
    vs_installation_path = _get_vs_installation_path(vswhere)
    vcvarsall_path = _find_vcvarsall(vs_installation_path)
    vc_env = _get_vc_env(vcvarsall_path)
    _update_current_env(vc_env)
    validate_windows_env()

def _search_for_vswhere() -> str:
    for program_file in _PROGRAM_FILES:
        vswhere_path = os.path.join(program_file, _VSWHERE_REL_PATH)
        vswhere_exe = os.path.realpath(vswhere_path)
        if os.path.exists(vswhere_path):
            return vswhere_path
    raise Exception("MSVC environment not initialized: vswhere.exe not found")

def _get_vs_installation_path(vswhere: str) -> str:
    cmd = [vswhere, "-latest", "-products", "*", "-property", "installationPath"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def _find_vcvarsall(vs_installation_path: str) -> str:
    vcvarsall_path = os.path.join(vs_installation_path, _VCVARSALL_REL_PATH)
    if os.path.exists(vcvarsall_path):
        return vcvarsall_path
    raise Exception("MSVC environment not initialized: vcvarsall.bat not found")

def _get_vc_env(vcvarsall_path: str) -> dict:
    arch = Arch.get_current()
    arch_arg = None
    if arch == Arch.X86_64:
        arch_arg = "x64"
    elif arch == Arch.X86:
        arch_arg = "x86"

    if arch_arg is None:
        raise Exception(f"MSVC environment not initialized: unsupported architecture: [{arch}]")

    cmd = [_CMD, "/d", "/c", "call", vcvarsall_path, arch_arg, "&&", "set"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    env = {}
    for line in result.stdout.splitlines():
        if line.startswith("ERROR") or line.startswith("[ERROR"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            continue
        env[key.strip().upper()] = value.strip()

    return env

def _update_current_env(env: dict):
    for key, value in env.items():
        os.environ[key] = value
