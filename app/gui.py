import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import pyautogui
from yt_dlp.utils import DownloadError

from app.automation import AutomationError, capture_around_cursor, ensure_app_running, paste_queue
from app.config import (
    DEFAULT_FIXED_DELAY,
    LOADING_CALIBRATION_COUNTDOWN,
    LOADING_INDICATOR,
    PASTE_BUTTON,
    PASTE_CALIBRATION_COUNTDOWN,
    QUEUE_FILE,
)
from app.playlist import extract_video_urls, parse_input
from app.url_queue import UrlQueue

MIN_DELAY = 1
MAX_DELAY = 120


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediaHuman Batch")
        self.geometry("680x560")
        self.minsize(560, 460)

        self.url_queue = UrlQueue(QUEUE_FILE)
        self.events = queue.Queue()
        self.delay_var = tk.StringVar(value=str(DEFAULT_FIXED_DELAY))
        self.status_var = tk.StringVar()

        self._build_layout()
        self.refresh_status()
        self.after(100, self._drain_events)

    def _build_layout(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Cole uma ou mais URLs de playlists do YouTube, uma por linha:").pack(anchor=tk.W)
        self.input_text = ScrolledText(frame, height=7, wrap=tk.NONE)
        self.input_text.pack(fill=tk.X, pady=(4, 8))

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X)
        self.action_buttons = [
            ttk.Button(actions, text="Importar", command=self.on_import),
            ttk.Button(actions, text="Calibrar botão", command=self.on_calibrate_paste_button),
            ttk.Button(actions, text="Calibrar carregamento", command=self.on_calibrate_loading),
        ]
        for button in self.action_buttons:
            button.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Spinbox(actions, from_=MIN_DELAY, to=MAX_DELAY, width=5, textvariable=self.delay_var).pack(side=tk.RIGHT)
        ttk.Label(actions, text="Espera fixa (s):").pack(side=tk.RIGHT, padx=(0, 4))

        ttk.Label(frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(10, 4))

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        self.log_text = ScrolledText(frame, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def refresh_status(self):
        pending = len(self.url_queue.read())
        button = "calibrado" if PASTE_BUTTON.exists() else "não calibrado"
        wait = "indicador visual" if LOADING_INDICATOR.exists() else "espera fixa"
        self.status_var.set(f"Fila: {pending} pendente(s) | Botão: {button} | Espera: {wait}")

    def read_fixed_delay(self):
        try:
            delay = int(self.delay_var.get())
        except ValueError:
            return DEFAULT_FIXED_DELAY
        return min(max(delay, MIN_DELAY), MAX_DELAY)

    def emit(self, kind, payload=None):
        self.events.put((kind, payload))

    def log(self, message):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _drain_events(self):
        while True:
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break
            self._handle_event(kind, payload)
        self.after(100, self._drain_events)

    def _handle_event(self, kind, payload):
        if kind == "log":
            self.log(payload)
        elif kind == "progress":
            value, maximum = payload
            self.progress.configure(value=value, maximum=maximum)
        elif kind == "hide":
            self.iconify()
        elif kind == "error":
            self.deiconify()
            self.log(f"Erro: {payload}")
            messagebox.showerror("MediaHuman Batch", payload)
        elif kind == "done":
            self.deiconify()
            self.set_buttons_state(tk.NORMAL)
            self.refresh_status()

    def set_buttons_state(self, state):
        for button in self.action_buttons:
            button.configure(state=state)

    def run_in_background(self, work, *args):
        self.set_buttons_state(tk.DISABLED)
        threading.Thread(target=self._run_safely, args=(work, *args), daemon=True).start()

    def _run_safely(self, work, *args):
        try:
            work(*args)
        except AutomationError as error:
            self.emit("error", str(error))
        except pyautogui.FailSafeException:
            self.emit("error", "Interrompido pelo fail-safe (mouse no canto da tela). A fila pendente continua em lista.txt.")
        except Exception as error:
            self.emit("error", f"Erro inesperado: {error}")
        finally:
            self.emit("done")

    def on_import(self):
        playlists = parse_input(self.input_text.get("1.0", tk.END))
        if not playlists and not self.url_queue.read():
            messagebox.showwarning("MediaHuman Batch", "Cole ao menos uma URL de playlist.")
            return
        if not PASTE_BUTTON.exists():
            messagebox.showwarning("MediaHuman Batch", "Calibre o botão 'Colar endereço' antes de importar.")
            return

        self.input_text.delete("1.0", tk.END)
        self.run_in_background(self._import_worker, playlists, self.read_fixed_delay())

    def _import_worker(self, playlists, fixed_delay):
        for playlist_url in playlists:
            self.emit("log", f"Lendo: {playlist_url}")
            try:
                video_urls = extract_video_urls(playlist_url)
            except DownloadError as error:
                self.emit("log", f"Falha ao ler {playlist_url}: {error}")
                continue
            added = self.url_queue.append(video_urls)
            self.emit("log", f"{len(video_urls)} vídeo(s) encontrado(s), {added} novo(s) na fila.")

        pending = self.url_queue.read()
        if not pending:
            self.emit("log", "Nenhuma URL na fila.")
            return

        self.emit("log", f"Colando {len(pending)} URL(s)… Não use mouse nem teclado.")
        self.emit("progress", (0, len(pending)))
        self.emit("hide")
        time.sleep(1)
        paste_queue(self.url_queue, fixed_delay, self._on_pasted)
        self.emit("log", "Concluído.")

    def _on_pasted(self, index, total, url):
        self.emit("progress", (index, total))
        self.emit("log", f"[{index}/{total}] {url}")

    def on_calibrate_paste_button(self):
        message = (
            "O MediaHuman será aberto e esta janela será minimizada.\n\n"
            f"Deixe o mouse parado sobre o botão \"Colar endereço\" por {PASTE_CALIBRATION_COUNTDOWN} segundos."
        )
        if messagebox.askokcancel("Calibrar botão", message):
            self.run_in_background(self._calibrate_worker, PASTE_BUTTON, PASTE_CALIBRATION_COUNTDOWN)

    def on_calibrate_loading(self):
        message = (
            "Calibração opcional: sem ela, a ferramenta usa a espera fixa entre URLs.\n\n"
            "O MediaHuman será aberto e esta janela será minimizada. "
            f"Em até {LOADING_CALIBRATION_COUNTDOWN} segundos, cole uma URL manualmente no MediaHuman "
            "e deixe o mouse parado sobre o texto exibido durante o carregamento."
        )
        if messagebox.askokcancel("Calibrar carregamento", message):
            self.run_in_background(self._calibrate_worker, LOADING_INDICATOR, LOADING_CALIBRATION_COUNTDOWN)

    def _calibrate_worker(self, target, countdown):
        ensure_app_running()
        self.emit("hide")
        time.sleep(countdown)
        capture_around_cursor(target)
        self.emit("log", f"Recorte salvo em {target}")
