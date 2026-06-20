import argparse
import sys

from src.app import App
from src.gui import run_gui
from src.shared.model.job import JobParams, set_job_params


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pobieranie etykiet PDF środków ochrony roślin (gov.pl)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Uruchom interfejs graficzny (domyślnie, gdy brak argumentów CLI)",
    )
    parser.add_argument("--job-id", help="Identyfikator zadania (tryb CLI)")
    parser.add_argument("--log-path", dest="log_path", help="Ścieżka pliku logu (tryb CLI)")
    parser.add_argument(
        "--result-path",
        dest="result_path",
        help="Ścieżka manifestu wyników (tryb CLI)",
    )
    return parser.parse_args()


def _is_cli_mode(args: argparse.Namespace) -> bool:
    return any([args.job_id, args.log_path, args.result_path])


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    args = parse_args()

    if args.gui or not _is_cli_mode(args):
        run_gui()
        sys.exit(0)

    missing = [
        name
        for name, value in (
            ("--job-id", args.job_id),
            ("--log-path", args.log_path),
            ("--result-path", args.result_path),
        )
        if not value
    ]
    if missing:
        print(f"Tryb CLI wymaga argumentów: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    job = JobParams.from_args(args)
    set_job_params(job)
    app = App(job)
    sys.exit(app.run())
