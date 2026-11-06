import os
import sys
import tkinter as tk
from tkinter import messagebox

WAYLAND_MESSAGE = (
    "O MediaHuman Batch precisa de uma sessão X11 (por exemplo, \"Xfce Session\") "
    "para controlar o mouse e capturar a tela. No Wayland isso não funciona.\n\n"
    "Veja a seção \"Sessão X11\" do README."
)


def show_wayland_error():
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("MediaHuman Batch", WAYLAND_MESSAGE)
    root.destroy()


def main():
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        show_wayland_error()
        sys.exit(1)

    from app.gui import App

    App().mainloop()


if __name__ == "__main__":
    main()
