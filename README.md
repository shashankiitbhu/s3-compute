# s3-for-compute 

A distributed compute platform built with Flask, Redis, and RQ, featuring job queuing, event-driven execution, autoscaling workers, and cost tracking.

<img width="1430" height="795" alt="Screenshot 2025-09-14 at 10 52 25 PM" src="https://github.com/user-attachments/assets/2abf4e5b-d458-4f9a-825e-fe08b4569eee" />

---

## Features

- **Job Submission API**: Submit compute jobs via REST API.
- **Job Status & Results**: Query job status, results, execution time, retries, and cost.
- **Function Registry**: Easily add new compute functions.
- **Event-Driven Triggers**: Schedule jobs with cron or fire jobs on custom events (webhooks).
- **Autoscaling Workers**: Automatically scale worker processes based on queue load.
- **Cost Awareness**: Each job includes a simulated cost estimate.
- **Extensible**: Add your own functions and triggers.

---

## Setup

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis server (in a separate terminal):**

   ```bash
   redis-server
   ```

4. **Start an RQ worker (in a separate terminal):**

   ```bash
   python worker.py
   ```

5. **Run the Flask API server (in a separate terminal):**

   ```bash
   python app.py
   ```

6. **(Optional) Start the autoscaler (in a separate terminal):**
   ```bash
   python autoscaler.py
   ```

---

## Usage

### Submit a Job

Submit a job to any registered function:

```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"function": "sample_sum", "payload": {"numbers": [1, 2, 3, 4, 5]}}'
```

**Response:**

```json
{ "job_id": "abc123" }
```

---

### Check Job Status

```bash
curl http://localhost:5000/status/abc123
```

**Response:**

```json
{
  "job_id": "abc123",
  "status": "finished",
  "result": 15,
  "execution_time": 0.001,
  "retries": 0,
  "cost": 0.0101
}
```

---

### List All Jobs

```bash
curl http://localhost:5000/jobs
```

---

### Cancel a Job

```bash
curl -X POST http://localhost:5000/cancel/abc123
```

---

### Retry a Failed Job

```bash
curl -X POST http://localhost:5000/retry/abc123
```

---

## Triggers & Event-Driven Execution

### Register a Cron Trigger (run every 30 seconds)

```bash
curl -X POST http://localhost:5000/trigger \
  -H "Content-Type: application/json" \
  -d '{"type": "cron", "function": "sample_sum", "payload": {"numbers": [1,2]}, "interval": 30}'
```

### Register a Webhook Trigger

```bash
curl -X POST http://localhost:5000/trigger \
  -H "Content-Type: application/json" \
  -d '{"type": "webhook", "function": "sample_sleep", "payload": {"seconds": 2}, "event_type": "file_uploaded"}'
```

### Fire an Event to Trigger Webhooks

```bash
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "file_uploaded"}'
```

---

## Autoscaling

The `autoscaler.py` script monitors the job queue and automatically starts or stops worker processes based on demand. This helps optimize resource usage and cost.

---

## Cost Awareness

Each job response includes a simulated cost estimate based on execution time. This helps track and manage compute expenses.

---

## Available Functions

- **sample_sum**: Returns the sum of a list of numbers.
- **sample_sleep**: Sleeps for N seconds, then returns "done".

**Example payloads:**

- `{"numbers": [1, 2, 3]}`
- `{"seconds": 5}`

You can add your own functions by editing the function registry.

---

## Extending

- **Add new compute functions**: Define your function and register it in the function registry.
- **Add new triggers**: Extend the trigger system for more event types.

---

## Project Structure

- `app.py` — Flask API server
- `worker.py` — RQ worker process
- `autoscaler.py` — Worker autoscaler
- `functions.py` — Registered compute functions
- `triggers.py` — Trigger and event logic

---

## TEAM Cybernetics 

Shashank Mittal and Shashank Kumar
