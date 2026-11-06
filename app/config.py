import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
QUEUE_FILE = ROOT_DIR / "lista.txt"

PASTE_BUTTON = ASSETS_DIR / "colar_endereco.png"
LOADING_INDICATOR = ASSETS_DIR / "carregando.png"

APP_EXECUTABLE = Path("/opt/youtube-to-mp3/YouTubeToMP3")
APP_BINARY_NAME = "YouTubeToMP3"
APP_WINDOW_NAME = "YouTube to MP3"
APP_DOWNLOAD_PAGE = "https://www.mediahuman.com/youtube-to-mp3-converter/"

CONFIDENCE = 0.85
POLL_INTERVAL = 0.5
APP_STARTUP_TIMEOUT = 30
PASTE_BUTTON_TIMEOUT = 10
LOADING_APPEAR_TIMEOUT = 5
LOADING_FINISH_TIMEOUT = 120
SETTLE_DELAY = 1.5
DEFAULT_FIXED_DELAY = 10

CALIBRATION_REGION_SIZE = (160, 48)
PASTE_CALIBRATION_COUNTDOWN = 5
LOADING_CALIBRATION_COUNTDOWN = 10


def find_app_executable():
    if APP_EXECUTABLE.exists():
        return str(APP_EXECUTABLE)
    return shutil.which(APP_BINARY_NAME)
