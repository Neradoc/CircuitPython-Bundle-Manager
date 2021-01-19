import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
from pathlib import Path
import requests
import traceback
from time import sleep
from bundle_tools.create_logger import create_logger
import logging

logger = create_logger(name=__name__, level=logging.DEBUG)


def close_window(window: tk.Toplevel):
    logger.debug(f"Closing download dialog!")
    window.grab_release()
    window.destroy()


def download_file(status_widget: ttk.Label, url: str, path: Path):
    logger.debug(f"Downloading {repr(url)} to {repr(path)}")
    req = requests.get(url=url, stream=True)
    total_length = req.headers.get("content-length")
    logger.debug(f"Length of data is {repr(total_length)}")
    data_length = 0
    if total_length is None:
        path.write_bytes(req.content)
    else:
        with path.open(mode="wb") as file:
            file.seek(0)
            for chunk in req.iter_content(1024):
                data_length += len(chunk)
                logger.debug(f"Length of data currently is {data_length}")
                file.write(chunk)
                text = f"{round(data_length / 1024, 2)}/{round(int(total_length) / 1024, 2)} kB"
                logger.debug(f"Updated: {text}")
                status_widget.config(text=text)
                status_widget.update_idletasks()
            text = f"Wrote {round(int(total_length) / 1024, 2)} kB"
            logger.debug(f"Updated: {text}")
            status_widget.config(text=text)
            status_widget.update_idletasks()


def download(master: tk.Tk, url: str, path: Path, show_traceback: bool = False):
    dialog = tk.Toplevel(master=master)
    dialog.protocol("WM_DELETE_WINDOW", lambda: close_window(window=dialog))
    dialog.transient(master=master)
    dialog.wait_visibility()
    dialog.grab_set()
    label = ttk.Label(master=dialog, text="Please wait, downloading...")
    label.grid(row=0, column=0, padx=1, pady=1, sticky=tk.NW)
    status = ttk.Label(master=dialog, text="0/infinity kB")
    status.grid(row=1, column=0, padx=1, pady=1, sticky=tk.NW)
    dialog.update_idletasks()
    try:
        download_file(status_widget=status, url=url, path=path)
    except requests.exceptions.ConnectionError:
        logger.exception("Uh oh! Something happened!")
        mbox.showerror("CircuitPython Bundle Manager: ERROR!",
                       "Oh no! An error occurred while downloading this file!\n"
                       "Something happened while trying to access the internet! "
                       "Do you have a working internet connection?\n\n" + (
                       traceback.format_exc() if show_traceback else ""))
    except requests.exceptions.ChunkedEncodingError:
        logger.exception("Uh oh! Something happened!")
        mbox.showerror("CircuitPython Bundle Manager: ERROR!",
                       "Oh no! An error occurred while downloading this file!\n"
                       "Something happened while trying to access the internet! "
                       "Did you internet connection break?\n\n" + (
                       traceback.format_exc() if show_traceback else ""))
    except Exception as _:
        logger.exception("Uh oh! Something happened!")
        mbox.showerror("CircuitPython Bundle Manager: ERROR!",
                       "Oh no! An error occurred while downloading this file!"
                       "\n\n" + (traceback.format_exc() if show_traceback else ""))
    master.after(1000, func=lambda: close_window(window=dialog))
