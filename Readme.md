# Mini Render Queue (Python)

This is a small project I built to practice how a simple render-farm style job queue works.  
The script watches a `jobs/` folder for JSON files, loads them into a priority queue, and executes each job as a shell command. Log output is saved into `logs/render_queue.log`.

I started this on Linux (AWS EC2) and finished it on Windows, so the project works on both environments.

---

## How It Works

1. Place a `.json` file in the `jobs/` folder
2. The script picks it up automatically
3. Job is added to a priority queue
4. How to run : python(3) src/main.py
5. Success/failure is logged
6. Failed jobs can retry (optional)

Example job file:

```json
{
  "id": "sample_job",
  "priority": 5,
  "command": "echo Rendering sample frame && sleep 1",
  "max_retries": 2,
  "retry_delay": 1
}
```
