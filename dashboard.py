import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="S3-for-Compute Dashboard", layout="wide")
st.title("S3-for-Compute: Job Dashboard")

if "autorefresh" not in st.session_state:
    st.session_state.autorefresh = 0
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="autorefresh")

if "recent_job_ids" not in st.session_state:
    st.session_state.recent_job_ids = []
if "metrics_history" not in st.session_state:
    st.session_state.metrics_history = []

st.sidebar.header("Upload Function & Submit Job")
with st.sidebar.form("upload_form"):
    file = st.file_uploader("Code file (.py or .js)", type=["py", "js"])
    runtime = st.selectbox("Runtime", ["python", "node"])
    payload = st.text_area("Payload (JSON)", value="{}", height=100)
    submit_upload = st.form_submit_button("Upload & Submit Job")

try:
    resp = requests.get("http://localhost:5000/metrics")
    if resp.ok:
        metrics = resp.json()
        queue_size = metrics.get("queue_size", 0)
        active_workers = metrics.get("active_workers", 0)
        total_cost = metrics.get("total_cost", 0.0)

        # Show metric cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Queue Size", queue_size)
        col3.metric("Total Cost ($)", f"{total_cost:.4f}")

        # Track history
        if "history" not in st.session_state:
            st.session_state.history = {"time": [], "queue": [], "workers": []}
        now = datetime.now().strftime("%H:%M:%S")
        st.session_state.history["time"].append(now)
        st.session_state.history["queue"].append(queue_size)
        st.session_state.history["workers"].append(active_workers)

        # Show chart
        st.line_chart({
            "Queue Size": st.session_state.history["queue"],
            "Active Workers": st.session_state.history["workers"],
        })
except Exception as e:
    st.error(f"Metrics fetch failed: {e}")


job_id = None
upload_result = None
if submit_upload and file:
    files = {"file": (file.name, file, "application/octet-stream")}
    data = {"runtime": runtime, "payload": payload}
    try:
        resp = requests.post("http://localhost:5000/upload", files=files, data=data)
        upload_result = resp.json()
        job_id = upload_result.get("job_id")
        st.sidebar.success(f"Job submitted! Job ID: {job_id}")
        # Store job_id in session state
        if job_id:
            st.session_state.recent_job_ids = [job_id] + st.session_state.recent_job_ids[:19]
    except Exception as e:
        st.sidebar.error(f"Upload failed: {e}")

st.header("Job Status & Result")
if job_id:
    status_btn = st.button("Check Job Status", key="status_btn")
    if status_btn:
        try:
            resp = requests.get(f"http://localhost:5000/status/{job_id}")
            job_status = resp.json()
            st.json(job_status)
        except Exception as e:
            st.error(f"Status fetch failed: {e}")
else:
    job_id_input = st.text_input("Enter Job ID to check status")
    if job_id_input:
        try:
            resp = requests.get(f"http://localhost:5000/status/{job_id_input}")
            job_status = resp.json()
            st.json(job_status)
        except Exception as e:
            st.error(f"Status fetch failed: {e}")

# --- Recent Jobs Table ---
st.header("Recent Jobs")
N = 10
recent_jobs = []
for jid in st.session_state.recent_job_ids[:N]:
    try:
        resp = requests.get(f"http://localhost:5000/status/{jid}")
        if resp.ok:
            job = resp.json()
            recent_jobs.append({
                "job_id": jid,
                "runtime": job.get("runtime", ""),
                "status": job.get("status", ""),
                "retries": job.get("retries", 0),
                "execution_time": job.get("execution_time", 0),
                "cost": job.get("cost", 0.0),
            })
    except Exception:
        continue

if recent_jobs:
    st.dataframe(recent_jobs)
else:
    st.info("No recent jobs yet.")

st.header("Autoscaler Logs")
try:
    resp = requests.get("http://localhost:5000/logs")
    if resp.ok:
        logs = resp.json().get("logs", [])
        st.code("".join(logs), language="log")
    else:
        st.warning("Could not fetch logs.")
except Exception as e:
    st.warning(f"Log fetch failed: {e}")
