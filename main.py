import sys
import argparse
from src.app import App
from src.shared.model.job import JobParams, set_job_params

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FB Login Automation CLI")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--log-path", required=True, dest="log_path")
    parser.add_argument("--result-path", required=True, dest="result_path")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    job = JobParams.from_args(args)
    set_job_params(job)
    app = App(job)
    sys.exit(app.run())