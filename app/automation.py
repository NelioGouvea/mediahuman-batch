import subprocess
import time

import pyautogui
import pyperclip

from app.config import (
    APP_DOWNLOAD_PAGE,
    APP_STARTUP_TIMEOUT,
    APP_WINDOW_NAME,
    CALIBRATION_REGION_SIZE,
    CONFIDENCE,
    LOADING_APPEAR_TIMEOUT,
    LOADING_FINISH_TIMEOUT,
    LOADING_INDICATOR,
    PASTE_BUTTON,
    PASTE_BUTTON_TIMEOUT,
    POLL_INTERVAL,
    SETTLE_DELAY,
    find_app_executable,
)

pyautogui.FAILSAFE = True


class AutomationError(Exception):
    pass


def find_on_screen(image):
    try:
        return pyautogui.locateCenterOnScreen(str(image), confidence=CONFIDENCE)
    except pyautogui.ImageNotFoundException:
        return None


def wait_until(condition, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(POLL_INTERVAL)
    return False


def find_window_id():
    result = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--name", APP_WINDOW_NAME],
        capture_output=True,
        text=True,
    )
    window_ids = result.stdout.split()
    return window_ids[-1] if window_ids else None


def activate_app():
    window_id = find_window_id()
    if window_id is None:
        raise AutomationError(f"Janela '{APP_WINDOW_NAME}' não encontrada.")
    subprocess.run(["xdotool", "windowactivate", "--sync", window_id], check=False)
    time.sleep(0.5)


def ensure_app_running():
    if find_window_id() is not None:
        activate_app()
        return

    executable = find_app_executable()
    if executable is None:
        raise AutomationError(
            f"MediaHuman YouTube to MP3 não está instalado. Baixe em {APP_DOWNLOAD_PAGE}"
        )

    subprocess.Popen(
        [executable],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not wait_until(lambda: find_window_id() is not None, APP_STARTUP_TIMEOUT):
        raise AutomationError(f"O MediaHuman não abriu em {APP_STARTUP_TIMEOUT}s.")
    activate_app()


def locate_paste_button():
    if not PASTE_BUTTON.exists():
        raise AutomationError("Botão 'Colar endereço' não calibrado. Calibre primeiro.")
    if not wait_until(lambda: find_on_screen(PASTE_BUTTON) is not None, PASTE_BUTTON_TIMEOUT):
        raise AutomationError(
            f"Botão 'Colar endereço' não encontrado na tela em {PASTE_BUTTON_TIMEOUT}s. Recalibre."
        )
    return find_on_screen(PASTE_BUTTON)


def wait_for_load(fixed_delay):
    if not LOADING_INDICATOR.exists():
        time.sleep(fixed_delay)
        return

    if not wait_until(lambda: find_on_screen(LOADING_INDICATOR) is not None, LOADING_APPEAR_TIMEOUT):
        return

    if not wait_until(lambda: find_on_screen(LOADING_INDICATOR) is None, LOADING_FINISH_TIMEOUT):
        raise AutomationError(f"O carregamento não terminou em {LOADING_FINISH_TIMEOUT}s.")

    time.sleep(SETTLE_DELAY)


def paste_queue(url_queue, fixed_delay, on_pasted):
    urls = url_queue.read()
    if not urls:
        return

    ensure_app_running()
    paste_location = locate_paste_button()

    total = len(urls)
    for index, url in enumerate(urls, start=1):
        pyperclip.copy(url)
        pyautogui.click(paste_location)
        wait_for_load(fixed_delay)
        url_queue.remove(url)
        on_pasted(index, total, url)


def capture_around_cursor(target):
    x, y = pyautogui.position()
    width, height = CALIBRATION_REGION_SIZE
    region = (max(0, x - width // 2), max(0, y - height // 2), width, height)

    pyautogui.moveRel(0, height * 4)
    time.sleep(0.4)

    target.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot(str(target), region=region)
