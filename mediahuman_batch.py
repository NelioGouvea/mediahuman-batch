import argparse
import subprocess
import sys
import time
from pathlib import Path

import pyautogui
import pyperclip

APP_PATH = Path("/opt/youtube-to-mp3/YouTubeToMP3")
ASSETS_DIR = Path(__file__).parent / "assets"
PASTE_BUTTON = ASSETS_DIR / "colar_endereco.png"
LOADING_INDICATOR = ASSETS_DIR / "carregando.png"

CONFIDENCE = 0.85
APP_STARTUP_TIMEOUT = 30
POLL_INTERVAL = 0.5
LOADING_APPEAR_TIMEOUT = 5
LOADING_FINISH_TIMEOUT = 120
SETTLE_DELAY = 1.5
DEFAULT_FIXED_DELAY = 10.0

pyautogui.FAILSAFE = True


def load_urls(args):
    urls = list(args.urls)
    if args.file:
        urls += Path(args.file).read_text(encoding="utf-8").splitlines()
    return list(dict.fromkeys(url.strip() for url in urls if url.strip()))


def find_on_screen(image):
    try:
        return pyautogui.locateCenterOnScreen(str(image), confidence=CONFIDENCE)
    except pyautogui.ImageNotFoundException:
        return None


def is_visible(image):
    return find_on_screen(image) is not None


def wait_until(condition, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(POLL_INTERVAL)
    return False


def wait_for(image, timeout):
    if not wait_until(lambda: is_visible(image), timeout):
        raise TimeoutError(f"Elemento '{image.name}' não encontrado na tela em {timeout}s.")
    return find_on_screen(image)


def wait_for_load(fixed_delay):
    if not LOADING_INDICATOR.exists():
        time.sleep(fixed_delay)
        return

    if not wait_until(lambda: is_visible(LOADING_INDICATOR), LOADING_APPEAR_TIMEOUT):
        print("    aviso: indicador de carregamento não detectado, seguindo.")
        return

    if not wait_until(lambda: not is_visible(LOADING_INDICATOR), LOADING_FINISH_TIMEOUT):
        raise TimeoutError(f"Carregamento não terminou em {LOADING_FINISH_TIMEOUT}s.")

    time.sleep(SETTLE_DELAY)


def launch_app():
    if not APP_PATH.exists():
        raise FileNotFoundError(f"Executável não encontrado: {APP_PATH}")
    subprocess.Popen([str(APP_PATH)])
    return wait_for(PASTE_BUTTON, APP_STARTUP_TIMEOUT)


def paste_urls(urls, paste_location, fixed_delay):
    total = len(urls)
    for index, url in enumerate(urls, start=1):
        pyperclip.copy(url)
        pyautogui.click(paste_location)
        print(f"[{index}/{total}] colado: {url}")
        wait_for_load(fixed_delay)


def parse_args():
    parser = argparse.ArgumentParser(description="Cola URLs em lote no MediaHuman YouTube to MP3")
    parser.add_argument("urls", nargs="*", help="URLs separadas por espaço")
    parser.add_argument("--file", help="Arquivo .txt com uma URL por linha")
    parser.add_argument("--no-launch", action="store_true", help="Não abre o app (usa a janela já aberta)")
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_FIXED_DELAY,
        help="Espera fixa em segundos entre URLs, usada quando não existe assets/carregando.png",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    urls = load_urls(args)

    if not urls:
        sys.exit("Nenhuma URL informada. Passe URLs como argumento ou use --file lista.txt")

    mode = "indicador visual" if LOADING_INDICATOR.exists() else f"espera fixa de {args.delay}s"
    print(f"Modo de espera: {mode}")

    paste_location = wait_for(PASTE_BUTTON, 5) if args.no_launch else launch_app()
    paste_urls(urls, paste_location, args.delay)
    print(f"Concluído: {len(urls)} URL(s) colada(s).")


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        sys.exit("Abortado pelo fail-safe (mouse no canto da tela).")
    except (TimeoutError, FileNotFoundError) as error:
        sys.exit(str(error))
