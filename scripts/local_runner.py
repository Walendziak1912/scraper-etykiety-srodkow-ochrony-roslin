import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import App
from src.shared.model.job import JobParams, set_job_params
from src.utils.io import clear_dir

today_str = datetime.now().strftime("%Y%m%d%H%M%S")
today_date = datetime.now().strftime("%Y-%m-%d")

clear_dir(Path(fr".\.artifacts\logs"))

GUID = str(uuid.uuid4())

LOG_PATH = str(Path(fr".\.artifacts\logs\{today_date}\{today_str}.log"))
RESULT_PATH = str(Path(fr".\.artifacts\logs\{today_date}\{today_str}"))

job = JobParams(
    job_id=str(GUID),
    log_path=LOG_PATH,
    result_path=RESULT_PATH
)

set_job_params(job)
app = App(job)
sys.exit(app.run())