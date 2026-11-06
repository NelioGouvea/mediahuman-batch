import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT_DIR / "lista.txt"

APP_EXECUTABLE = Path("/opt/youtube-to-mp3/YouTubeToMP3")
APP_BINARY_NAME = "YouTubeToMP3"
APP_DOWNLOAD_PAGE = "https://www.mediahuman.com/youtube-to-mp3-converter/"

APP_STARTUP_DELAY = 10
SEND_TIMEOUT = 30
SEND_INTERVAL = 0.5


def find_app_executable():
    if APP_EXECUTABLE.exists():
        return str(APP_EXECUTABLE)
    return shutil.which(APP_BINARY_NAME)
