import json
from pathlib import Path
from dataclasses import dataclass, field
from heapq import heappush, heappop
from typing import List, Optional

# -------------------------------------------------------------------


JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"

@dataclass(order=True) # this enables comparison operators
class JobItem:
    """
    Represents a single job with priority.
    'order=True' lets us compare JobItem objects for heapq.
    """
    sort_index: int = field(init=False, repr=False)
    priority: int
    job_id: str
    command: str
    raw: dict = field(compare=False, default_factory=dict)

    def __post_init__(self):
        # heapq is a min-heap, so we invert priority
        # so that higher priority jobs come out first
        self.sort_index = -self.priority

class JobQueue:
    """
    Simple priority queue wrapper around heapq.
    """
    def __init__(self):
        self._queue: List[JobItem] = []

    def push(self, job: JobItem):
        heappush(self._queue, job)
        print(f"Queued job={job.job_id} priority={job.priority}")

    def pop(self) -> Optional[JobItem]:
        if not self._queue:
            return None
        return heappop(self._queue)

    def __len__(self):
        return len(self._queue)



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
    return JobItem(
        priority=priority,
        job_id=job_id,
        command=command,
        raw=data,
    )

def ensure_jobs_dir():
    """
    Make sure jobs directory exists.
    """
    JOBS_DIR.mkdir(parents=True, exist_ok=True)


def list_job_files():
    """
    Load all jobs and process them in priority order.
    """
    ensure_jobs_dir()
    
    job_files = list(JOBS_DIR.glob("*.json"))

    if not job_files:
        print("No job files found in jobs directory.")
        return

    queue = JobQueue()

    # 1) 모든 job 파일을 읽어서 큐에 넣기
    for path in job_files:
        job = load_job_file(path)
        # TODO: 여기서 queue.push(job) 호출
        # 그리고 "Queued job ..." 같은 출력도 찍어보기
        queue.push(job)
        print(f"Queued job={job.job_id} priority={job.priority}")


    # 2) 큐에서 하나씩 꺼내서 priority 순서 확인
    print("\nProcessing jobs in priority order:")
    # TODO: while len(queue) > 0:
    #          job = queue.pop()
    #          job 정보 출력 (id, priority, command)
    while len(queue) > 0:
        job = queue.pop()
        print(f"Processing job={job.job_id} priority={job.priority} command={job.command}")



if __name__ == "__main__":
    list_job_files()
