from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.app import AppRunner
from src.core.settings import get_settings, resolve_download_dir
from src.scraper.progress import DownloadEvent
from src.utils.env_file import update_env_variable


class ScraperGui:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Etykiety SOR – pobieranie PDF")
        self.root.geometry("980x760")
        self.root.minsize(860, 620)

        self.runner = AppRunner(download_dir=Path("."))
        initial = self._load_download_dir()
        self._initial_download_dir = initial.resolve() if initial else None
        self.downloaded_count = 0
        self.uptodate_count = 0
        self.failed_count = 0
        self._cancelling = False
        self._ui_busy = False

        self._setup_progress_styles()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll_progress()

    def _load_download_dir(self) -> Path | None:
        return resolve_download_dir(get_settings().download_dir)

    def _download_dir_display(self) -> str:
        path = self._load_download_dir()
        return str(path) if path else ""

    def _setup_progress_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.layout("Green.Horizontal.TProgressbar", style.layout("Horizontal.TProgressbar"))
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#dddddd",
            background="#43a047",
            bordercolor="#dddddd",
            lightcolor="#43a047",
            darkcolor="#2e7d32",
        )

    def _reset_progress_idle(self) -> None:
        self.progress.stop()
        self.progress.configure(
            mode="determinate",
            maximum=100,
            value=0,
            style="Horizontal.TProgressbar",
        )

    def _start_progress_running(self) -> None:
        self.progress.stop()
        self.progress.configure(mode="indeterminate", style="Horizontal.TProgressbar")
        self.progress.start(12)

    def _set_progress_complete(self) -> None:
        self.progress.stop()
        self.progress.configure(
            mode="determinate",
            maximum=100,
            value=100,
            style="Green.Horizontal.TProgressbar",
        )

    def _set_progress_cancelled(self) -> None:
        self._reset_progress_idle()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        path_frame = ttk.LabelFrame(main, text="Katalog zapisu plików PDF (DOWNLOAD_DIR)", padding=8)
        path_frame.pack(fill=tk.X, pady=(0, 8))

        self.path_var = tk.StringVar(value=self._download_dir_display())
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        ttk.Button(path_frame, text="Wybierz…", command=self._browse_directory).pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(main, text="Postęp pobierania", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            height=24,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Consolas", 9),
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X)

        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100, value=0)
        self.progress.pack(fill=tk.X, pady=(0, 6))

        status_row = ttk.Frame(bottom)
        status_row.pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar(value="Gotowy do pobierania.")
        ttk.Label(status_row, textvariable=self.status_var).pack(side=tk.LEFT, anchor=tk.W)

        self.stats_var = tk.StringVar(value="Pobrane: 0 | aktualne: 0 | błędy: 0")
        ttk.Label(status_row, textvariable=self.stats_var).pack(side=tk.RIGHT, anchor=tk.E)

        footer = ttk.Frame(bottom)
        footer.pack(fill=tk.X)

        buttons = ttk.Frame(footer)
        buttons.pack(side=tk.RIGHT, anchor=tk.SE)

        self.start_button = ttk.Button(
            buttons,
            text="Rozpocznij pobieranie",
            command=self._start_scraper,
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 8))

        self.cancel_button = ttk.Button(
            buttons,
            text="Anuluj",
            command=self._cancel_scraper,
            state=tk.DISABLED,
        )
        self.cancel_button.pack(side=tk.LEFT)

    def _browse_directory(self) -> None:
        selected = filedialog.askdirectory(
            title="Wybierz katalog zapisu plików PDF",
            initialdir=self.path_var.get() or str(Path.home()),
        )
        if selected:
            self.path_var.set(selected)
            self.runner.download_dir = Path(selected)

    def _persist_download_dir_if_changed(self, download_dir: Path) -> bool:
        resolved = download_dir.resolve()
        if self._initial_download_dir is not None and resolved == self._initial_download_dir:
            return False

        try:
            update_env_variable("DOWNLOAD_DIR", str(resolved))
            self._initial_download_dir = resolved
            self.path_var.set(str(resolved))
            self.runner.download_dir = resolved
            return True
        except OSError as exc:
            messagebox.showerror("Błąd", f"Nie udało się zapisać katalogu w .env: {exc}")
            raise

    def _start_scraper(self) -> None:
        if self.runner.is_running:
            return

        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Błąd", "Podaj katalog zapisu plików PDF.")
            return

        download_dir = Path(path).resolve()
        try:
            saved = self._persist_download_dir_if_changed(download_dir)
        except OSError:
            return

        try:
            download_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Błąd", f"Nie można utworzyć katalogu: {exc}")
            return

        self.runner.download_dir = download_dir
        self.downloaded_count = 0
        self.uptodate_count = 0
        self.failed_count = 0
        self._cancelling = False
        self._ui_busy = True
        self._update_stats()
        self._clear_log()
        self._append_log("Uruchamianie scrapera…")
        if saved:
            self._append_log(f"Zapisano nowy katalog w .env: {download_dir}")

        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self._start_progress_running()
        self.status_var.set("Trwa pobieranie plików PDF…")
        self.runner.start()

    def _cancel_scraper(self) -> None:
        if not self.runner.is_running or self._cancelling:
            return
        self._cancelling = True
        self.status_var.set("Anulowanie pobierania…")
        self._append_log("Anulowanie pobierania…")
        self.runner.cancel()
        self._finish_run(
            DownloadEvent(
                kind="cancelled",
                message="Pobieranie przerwane przez użytkownika.",
                stats={
                    "file_status_count/downloaded": self.downloaded_count,
                    "file_status_count/uptodate": self.uptodate_count,
                    "log_count/ERROR": 0,
                },
            )
        )

    def _finish_run(self, event: DownloadEvent) -> None:
        if not self._ui_busy:
            return

        if event.kind == "cancelled":
            self._set_progress_cancelled()
        else:
            self._set_progress_complete()

        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self._cancelling = False
        self._ui_busy = False
        downloaded = self.downloaded_count
        uptodate = self.uptodate_count
        if event.kind == "cancelled":
            self.status_var.set("Przerwano.")
        else:
            self.status_var.set("Zakończono.")
            self._show_completion_popup(downloaded, uptodate, self.failed_count)
        self._update_stats()
        self._append_log(event.message)

    def _show_completion_popup(self, downloaded: int, uptodate: int, failed: int) -> None:
        messagebox.showinfo(
            "Pobieranie zakończone",
            (
                "Pobieranie plików zakończone.\n"
                "Statystyka końcowa\n"
                f"Pobrane pliki: {downloaded}\n"
                f"Pliki bez zmian: {uptodate}\n"
                f"Błędne pliki: {failed}"
            ),
        )

    def _handle_event(self, event: DownloadEvent) -> None:
        if event.kind == "started":
            self._append_log(event.message)
            return

        if event.kind == "info":
            self._append_log(event.message)
            return

        if event.kind == "downloading":
            if self._cancelling:
                return
            self._append_log(f"  >> {event.message}")
            return

        if event.kind == "file":
            if self._cancelling:
                return
            if event.status == "downloaded":
                self.downloaded_count += 1
            elif event.status == "uptodate":
                self.uptodate_count += 1
            else:
                self.failed_count += 1
            self._update_stats()
            self._append_log(event.message)
            return

        if event.kind in {"finished", "cancelled"}:
            self._finish_run(event)

    def _update_stats(self) -> None:
        self.stats_var.set(
            f"Pobrane: {self.downloaded_count} | aktualne: {self.uptodate_count} | błędy: {self.failed_count}"
        )

    def _append_log(self, message: str) -> None:
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _clear_log(self) -> None:
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _poll_progress(self) -> None:
        progress_queue = self.runner.progress_queue
        if progress_queue is not None:
            while True:
                try:
                    event = progress_queue.get_nowait()
                except queue.Empty:
                    break
                self._handle_event(event)

        if (
            self._ui_busy
            and not self.runner.is_running
            and (self._cancelling or self.runner.was_killed)
        ):
            self._finish_run(
                DownloadEvent(
                    kind="cancelled",
                    message="Pobieranie przerwane przez użytkownika.",
                    stats={
                        "file_status_count/downloaded": self.downloaded_count,
                        "file_status_count/uptodate": self.uptodate_count,
                        "log_count/ERROR": 0,
                    },
                )
            )

        self.root.after(200, self._poll_progress)

    def _on_close(self) -> None:
        if self.runner.is_running or self.runner.is_alive():
            if messagebox.askokcancel(
                "Zamknij aplikację",
                "Trwa pobieranie plików. Przerwać i zamknąć aplikację?",
            ):
                self.runner.cancel()
                self.runner.join(timeout=10)
            else:
                return
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_gui() -> None:
    import multiprocessing

    multiprocessing.freeze_support()
    ScraperGui().run()
