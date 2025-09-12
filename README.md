# s3-for-compute

A distributed compute platform using Flask, Redis, and RQ for job processing with automatic worker scaling.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis server (in separate terminal):
```bash
redis-server
```

4. Start RQ worker (in separate terminal):
```bash
python worker.py
```

5. Run Flask API server (in separate terminal):
```bash
python app.py
```

6. Run autoscaler (optional, in separate terminal):
```bash
python autoscaler.py
```

## Usage

### Submit a job
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"function": "sample_sum", "payload": {"numbers": [1, 2, 3, 4, 5]}}'
```

Response:
```json
{"job_id": "abc123"}
```

### Check job status
```bash
curl http://localhost:5000/status/abc123
```

Response:
```json
{
  "job_id": "abc123",
  "status": "finished",
  "result": 15,
  "execution_time": 0.001,
  "retries": 0
}
```

## Available Functions

- `sample_sum`: Returns sum of numbers array
- `sample_sleep`: Sleeps for N seconds then returns "done"

Example payloads:
- `{"numbers": [1, 2, 3]}`
- `{"seconds": 5}`