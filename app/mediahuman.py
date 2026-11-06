import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

from app.config import (
    APP_BINARY_NAME,
    APP_DEB_URL,
    APP_DOWNLOAD_PAGE,
    APP_STARTUP_DELAY,
    SEND_INTERVAL,
    SEND_TIMEOUT,
    find_app_executable,
)


class MediaHumanError(Exception):
    pass


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
        deb_path = Path(temp_dir) / "YouTubeToMP3.amd64.deb"
        urllib.request.urlretrieve(APP_DEB_URL, deb_path)
        deb_path.chmod(0o644)
        result = subprocess.run(["pkexec", "apt-get", "install", "-y", str(deb_path)], capture_output=True)
    if result.returncode != 0:
        raise MediaHumanError(
            f"Não foi possível instalar o MediaHuman automaticamente. Baixe em {APP_DOWNLOAD_PAGE}"
        )


def is_running():
    return subprocess.run(["pgrep", "-x", APP_BINARY_NAME], capture_output=True).returncode == 0


def ensure_running(executable):
    if is_running():
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
