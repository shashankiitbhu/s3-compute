import streamlit as st
import requests
import json

st.set_page_config(page_title="S3-for-Compute Dashboard", layout="wide")
st.title("S3-for-Compute: Job Dashboard")

st.sidebar.header("Upload Function & Submit Job")

with st.sidebar.form("upload_form"):
    file = st.file_uploader("Code file (.py or .js)", type=["py", "js"])
    runtime = st.selectbox("Runtime", ["python", "node"])
    payload = st.text_area("Payload (JSON)", value="{}", height=100)
    submit_upload = st.form_submit_button("Upload & Submit Job")

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

st.header("Quick Job History (last 5)")
# This is a placeholder. You can extend with Redis or DB integration for real history.
st.info("Job history feature coming soon!")

st.markdown("---")
st.markdown("Made with Streamlit · S3-for-Compute")
