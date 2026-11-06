import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from yt_dlp.utils import DownloadError

from app.config import QUEUE_FILE, find_app_executable
from app.mediahuman import MediaHumanError, install_app, send_queue
from app.playlist import extract_video_urls, parse_input
from app.url_queue import UrlQueue


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediaHuman Batch")
        self.geometry("680x520")
        self.minsize(560, 420)

        self.url_queue = UrlQueue(QUEUE_FILE)
        self.events = queue.Queue()
        self.status_var = tk.StringVar()

        self._build_layout()
        self.refresh_status()
        self.after(100, self._drain_events)
        self.after(500, self.offer_app_install)

    def _build_layout(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Cole uma ou mais URLs de playlists do YouTube, uma por linha:").pack(anchor=tk.W)
        self.input_text = ScrolledText(frame, height=7, wrap=tk.NONE)
        self.input_text.pack(fill=tk.X, pady=(4, 8))

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X)
        self.import_button = ttk.Button(actions, text="Importar", command=self.on_import)
        self.import_button.pack(side=tk.LEFT)
        ttk.Label(actions, textvariable=self.status_var).pack(side=tk.LEFT, padx=12)

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=8)

        self.log_text = ScrolledText(frame, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def refresh_status(self):
        self.status_var.set(f"Fila: {len(self.url_queue.read())} pendente(s)")

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
            self.refresh_status()
        elif kind == "error":
            self.log(f"Erro: {payload}")
            messagebox.showerror("MediaHuman Batch", payload)
        elif kind == "done":
            self.import_button.configure(state=tk.NORMAL)
            self.refresh_status()

    def run_in_background(self, work, *args):
        self.import_button.configure(state=tk.DISABLED)
        threading.Thread(target=self._run_safely, args=(work, *args), daemon=True).start()

    def _run_safely(self, work, *args):
        try:
            work(*args)
        except MediaHumanError as error:
            self.emit("error", str(error))
        except Exception as error:
            self.emit("error", f"Erro inesperado: {error}")
        finally:
            self.emit("done")

    def offer_app_install(self):
        if find_app_executable() is not None:
            return
        message = (
            "O MediaHuman YouTube to MP3 não está instalado.\n\n"
            "Deseja baixar e instalar agora? Será pedida a senha de administrador."
        )
        if messagebox.askyesno("MediaHuman não encontrado", message):
            self.run_in_background(self._install_app)

    def _install_app(self):
        self.emit("log", "Baixando e instalando o MediaHuman YouTube to MP3…")
        install_app()
        self.emit("log", "MediaHuman instalado.")

    def on_import(self):
        playlists = parse_input(self.input_text.get("1.0", tk.END))
        if not playlists and not self.url_queue.read():
            messagebox.showwarning("MediaHuman Batch", "Cole ao menos uma URL de playlist.")
            return

        self.input_text.delete("1.0", tk.END)
        self.run_in_background(self._import, playlists)

    def _import(self, playlists):
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

        self.emit("log", f"Enviando {len(pending)} URL(s) ao MediaHuman…")
        self.emit("progress", (0, len(pending)))
        send_queue(self.url_queue, self._on_sent)
        self.emit("log", "Concluído.")

    def _on_sent(self, index, total, url):
        self.emit("progress", (index, total))
        self.emit("log", f"[{index}/{total}] {url}")
