import os
import subprocess
import winreg
from pathlib import Path

from app.config import APP_BINARY_NAME, APP_DISPLAY_NAME

UNINSTALL_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
]

DEFAULT_INSTALL_ROOTS = ["ProgramFiles", "ProgramFiles(x86)"]


def registry_install_locations():
    for root, path in UNINSTALL_KEYS:
        try:
            uninstall_key = winreg.OpenKey(root, path)
        except OSError:
            continue
        with uninstall_key:
            for index in range(winreg.QueryInfoKey(uninstall_key)[0]):
                with winreg.OpenKey(uninstall_key, winreg.EnumKey(uninstall_key, index)) as app_key:
                    try:
                        name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                        location = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                    except OSError:
                        continue
                if APP_DISPLAY_NAME in name and location:
                    yield Path(location)


def default_install_locations():
    for variable in DEFAULT_INSTALL_ROOTS:
        if variable in os.environ:
            yield Path(os.environ[variable]) / "MediaHuman" / "YouTube to MP3"
    yield Path(os.environ["LOCALAPPDATA"]) / "Programs" / "MediaHuman" / "YouTube to MP3"


def find_executable():
    for location in [*registry_install_locations(), *default_install_locations()]:
        executable = location / APP_BINARY_NAME
        if executable.exists():
            return str(executable)
    return None


def is_running():
    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {APP_BINARY_NAME}", "/NH"],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return APP_BINARY_NAME.lower() in result.stdout.lower()


def run_installer(installer_path):
    quoted_path = str(installer_path).replace("'", "''")
    command = (
        f"Start-Process -FilePath '{quoted_path}' "
        "-ArgumentList '/SILENT','/SUPPRESSMSGBOXES','/NORESTART' -Verb RunAs -Wait"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return result.returncode == 0
