import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

from app.config import (
    APP_DOWNLOAD_PAGE,
    APP_INSTALLER_URL,
    APP_STARTUP_DELAY,
    IS_WINDOWS,
    SEND_INTERVAL,
    SEND_TIMEOUT,
)

if IS_WINDOWS:
    from app import windows as system
else:
    from app import linux as system


class MediaHumanError(Exception):
    pass


def find_app_executable():
    return system.find_executable()


def require_executable():
    executable = find_app_executable()
    if executable is None:
        raise MediaHumanError(
            f"MediaHuman YouTube to MP3 não está instalado. Baixe em {APP_DOWNLOAD_PAGE}"
        )
    return executable


def install_app():
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir).chmod(0o755)
        installer_path = Path(temp_dir) / APP_INSTALLER_URL.rsplit("/", 1)[1]
        urllib.request.urlretrieve(APP_INSTALLER_URL, installer_path)
        installer_path.chmod(0o644)
        if not system.verify_installer(installer_path):
            raise MediaHumanError(
                "O instalador baixado não passou na verificação de segurança e não foi executado. "
                f"Baixe e instale manualmente em {APP_DOWNLOAD_PAGE}"
            )
        installed = system.run_installer(installer_path)
    if not installed or find_app_executable() is None:
        raise MediaHumanError(
            f"Não foi possível instalar o MediaHuman automaticamente. Baixe em {APP_DOWNLOAD_PAGE}"
        )


def ensure_running(executable):
    if system.is_running():
        return
    subprocess.Popen(
        [executable],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(APP_STARTUP_DELAY)


def send_url(executable, url):
    try:
        subprocess.run(
            [executable, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=SEND_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        raise MediaHumanError(f"O MediaHuman não respondeu em {SEND_TIMEOUT}s ao receber {url}")


def send_queue(url_queue, on_sent):
    urls = url_queue.read()
    if not urls:
        return

    executable = require_executable()
    ensure_running(executable)

    total = len(urls)
    for index, url in enumerate(urls, start=1):
        send_url(executable, url)
        url_queue.remove(url)
        on_sent(index, total, url)
        time.sleep(SEND_INTERVAL)
