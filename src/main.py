import json
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"



def load_job_file (path: Path) :
    """
    Read a JSON job file and return a dir with job metadata
    Example return value 
    {
        "id" : "sample_job",
        "priority" : 5,
        "command" : "echo hello"
    }
    """
    # open json file with json.load()
    # return job_id , priority , command with dict type

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    job_id = data.get("id", path.stem)
    priority = int(data.get("priority", 0))
    command = data["command"]
    return {
        "id": job_id,
        "priority": priority,
        "command": command
    }






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
        # print loaded job metadata
        job_metadata = load_job_file(path)
        print("  Job ID:", job_metadata["id"])
        print("  Priority:", job_metadata["priority"])
        print("  Command:", job_metadata["command"])


if __name__ == "__main__":
    list_job_files()
