import os
import sys
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    DATA_DIR = Path(os.environ["APPDATA"]) / "mediahuman-batch"
else:
    DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "mediahuman-batch"
QUEUE_FILE = DATA_DIR / "lista.txt"

APP_DISPLAY_NAME = "YouTube to MP3"
APP_DOWNLOAD_PAGE = "https://www.mediahuman.com/youtube-to-mp3-converter/"

if IS_WINDOWS:
    APP_BINARY_NAME = "YouTubeToMP3.exe"
    APP_INSTALLER_URL = "https://www.mediahuman.com/files/YouTubeToMP3-x64.exe"
    # Nome do titular do certificado que assina o instalador oficial da MediaHuman.
    APP_INSTALLER_SIGNER = "Vyacheslav Anatolievich Parygin IP"
else:
    APP_BINARY_NAME = "YouTubeToMP3"
    APP_INSTALLER_URL = "https://www.mediahuman.com/files/YouTubeToMP3.amd64.deb"
    # O .deb não é assinado: confere o SHA-256 da versão conhecida.
    # Atualize junto com o install.sh quando a MediaHuman publicar uma versão nova.
    APP_INSTALLER_SHA256 = "945dcd1a0ce4acbb958b98d4fde79f78cc07673da49dfc3b264780d160272cbc"
    APP_EXECUTABLE = Path("/opt/youtube-to-mp3/YouTubeToMP3")

APP_STARTUP_DELAY = 10
SEND_TIMEOUT = 30
SEND_INTERVAL = 0.5
