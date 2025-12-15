#!/usr/bin/env python3
import json
import logging
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from heapq import heappush, heappop
from pathlib import Path
from typing import List, Tuple, Optional
import argparse



# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
POLL_INTERVAL = 1.0  # seconds


# -------------------------------------------------------------------
# CLI Arguments
# -------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Mini Render Queue"
    )

    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Seconds to wait between job scans (default: 1.0)",
    )

    return parser.parse_args()

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "render_queue.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# -------------------------------------------------------------------
# Job Item Data Structure
# -------------------------------------------------------------------
@dataclass(order=True)
class JobItem:
    """
    Represents a job loaded from a JSON file.
    Implements order-by-priority using heapq.
    Note: heapq pops the smallest value first,
    so priority is stored as negative for descending order.
    """
    sort_index: Tuple[int, float] = field(init=False, repr=False)
    priority: int
    created_at: float
    job_id: str
    command: str
    raw: dict = field(compare=False, default_factory=dict)

    def __post_init__(self):
        self.sort_index = (-self.priority, self.created_at)


# -------------------------------------------------------------------
# Priority Queue Wrapper
# -------------------------------------------------------------------
class JobQueue:
    def __init__(self):
        self._queue: List[JobItem] = []

    def push(self, job: JobItem):
        heappush(self._queue, job)
        logging.info(f"Queued job={job.job_id} priority={job.priority}")

    def pop(self) -> Optional[JobItem]:
        if not self._queue:
            return None
        return heappop(self._queue)

    def __len__(self):
        return len(self._queue)


# -------------------------------------------------------------------
# Load Jobs from JSON Files
# -------------------------------------------------------------------
def load_job_file(path: Path) -> JobItem:
    """
    Reads a JSON job file and converts it into a JobItem.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    job_id = data.get("id", path.stem)
    priority = int(data.get("priority", 0))
    command = data["command"]
    created_at = path.stat().st_mtime

    return JobItem(
        priority=priority,
        created_at=created_at,
        job_id=job_id,
        command=command,
        raw=data,
    )


def scan_jobs_directory(queue: JobQueue):
    """
    Scans the jobs/ directory for new JSON job files.
    Once loaded, the file is removed to avoid duplicate processing.
    """
    JOBS_DIR.mkdir(parents=True, exist_ok=True)

    for path in JOBS_DIR.glob("*.json"):
        try:
            job_item = load_job_file(path)
            queue.push(job_item)
            logging.info(f"Loaded job file: {path.name}")
            path.unlink()  # Prevent double execution
        except Exception as e:
            logging.error(f"Failed to load job {path.name}: {e}", exc_info=True)


# -------------------------------------------------------------------
# Execute a Job
# -------------------------------------------------------------------
def process_job(job: JobItem):
    """
    Runs the job command using subprocess and logs the output.
    """
    logging.info(f"[START] job={job.job_id} command='{job.command}'")

    try:
        result = subprocess.run(
            job.command,
            shell=True,
            text=True,
            capture_output=True,
            check=True,
        )

        if result.stdout:
            logging.info(f"[OUTPUT] job={job.job_id} stdout:\n{result.stdout}")
        if result.stderr:
            logging.warning(f"[OUTPUT] job={job.job_id} stderr:\n{result.stderr}")

        logging.info(f"[SUCCESS] job={job.job_id}")

    except subprocess.CalledProcessError as e:
        logging.error(
            f"[FAILED] job={job.job_id} exit_code={e.returncode}\n"
            f"stdout={e.stdout}\nstderr={e.stderr}"
        )
    except Exception as e:
        logging.error(f"[FAILED] job={job.job_id} unexpected error: {e}", exc_info=True)


# -------------------------------------------------------------------
# Graceful Shutdown Handler
# -------------------------------------------------------------------
class GracefulKiller:
    """
    Ensures the program exits cleanly when receiving SIGINT / SIGTERM.
    Allows current job to finish before shutting down.
    """
    def __init__(self):
        self._kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    @property
    def kill_now(self):
        return self._kill_now

    def exit_gracefully(self, signum, frame):
        logging.info(f"Received signal {signum}, shutting down after current job...")
        self._kill_now = True


# -------------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------------
def main():
    logging.info("Mini Render Queue started.")
    logging.info(f"Watching directory: {JOBS_DIR}")

    queue = JobQueue()
    killer = GracefulKiller()

    while not killer.kill_now:
        scan_jobs_directory(queue)

        job = queue.pop()
        if job:
            process_job(job)
        else:
            time.sleep(POLL_INTERVAL)

    logging.info("Render Queue stopped cleanly. Goodbye!")


if __name__ == "__main__":
    main()

