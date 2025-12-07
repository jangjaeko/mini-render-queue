from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"


def ensure_jobs_dir():
    """
    Make sure jobs directory exists.
    """
    JOBS_DIR.mkdir(parents=True, exist_ok=True)


def list_job_files():
    """
    Print all JSON job files in the jobs directory.
    """
    ensure_jobs_dir()
    
    job_files = list(JOBS_DIR.glob("*.json"))

    if not job_files:
        print("No job files found in jobs directory.")
        return
    
    for path in job_files:
        print("Found job file:", path.name)


if __name__ == "__main__":
    list_job_files()
