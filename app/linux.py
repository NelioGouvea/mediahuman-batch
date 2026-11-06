import hashlib
import shutil
import subprocess

from app.config import APP_BINARY_NAME, APP_EXECUTABLE, APP_INSTALLER_SHA256


def find_executable():
    if APP_EXECUTABLE.exists():
        return str(APP_EXECUTABLE)
    return shutil.which(APP_BINARY_NAME)


def is_running():
    return subprocess.run(["pgrep", "-x", APP_BINARY_NAME], capture_output=True).returncode == 0


def verify_installer(installer_path):
    digest = hashlib.sha256(installer_path.read_bytes()).hexdigest()
    return digest == APP_INSTALLER_SHA256


def run_installer(installer_path):
    result = subprocess.run(["pkexec", "apt-get", "install", "-y", str(installer_path)], capture_output=True)
    return result.returncode == 0
