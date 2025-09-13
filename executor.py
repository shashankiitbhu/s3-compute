import json
import os
import time
import logging
import importlib.util
import subprocess
from rq import get_current_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job(function_name, payload, **kwargs):
    """
    Execute a function with the given payload.
    Supports both Python and Node runtimes.
    """
    worker_tag = os.environ.get('WORKER_TAG', 'unknown-worker')
    job = get_current_job()
    start_time = time.time()

    # Get runtime and filename from job meta or kwargs
    runtime = None
    filename = None
    if hasattr(job, 'meta'):
        runtime = job.meta.get('runtime')
        filename = job.meta.get('filename')
    if not runtime:
        runtime = kwargs.get('runtime', 'python')
    if not filename:
        filename = kwargs.get('filename', f"{function_name}.py")

    logger.info(f"Starting job {job.id} for function {function_name} (runtime={runtime}, filename={filename})")

    base_cost = 0.01  # base cost per job
    time_rate = 0.05  # cost per second
    try:
        result = None
        file_path = os.path.join("functions", filename)
        if not os.path.exists(file_path):
            raise ImportError(f"Function file {filename} not found")
        if runtime == "python":
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{os.path.abspath('functions')}:/app",
                "-e", f"PAYLOAD={json.dumps(payload)}",
                "python:3.11",
                "python", f"/app/{filename}"
            ]
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            if proc.returncode != 0:
                raise RuntimeError(f"Python Docker execution failed: {proc.stderr}")
            result = proc.stdout.strip()
        elif runtime == "node":
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{os.path.abspath('functions')}:/app",
                "-e", f"PAYLOAD={json.dumps(payload)}",
                "node:18",
                "node", f"/app/{filename}"
            ]
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            if proc.returncode != 0:
                raise RuntimeError(f"Node Docker execution failed: {proc.stderr}")
            result = proc.stdout.strip()
        else:
            # Default: Python import-based execution (legacy)
            module_path = f"functions/{function_name}.py"
            if not os.path.exists(module_path):
                raise ImportError(f"Function {function_name} not found")
            spec = importlib.util.spec_from_file_location(function_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if not hasattr(module, 'handler'):
                raise AttributeError(f"Function {function_name} missing handler function")
            result = module.handler(payload)

        execution_time = time.time() - start_time
        cost = base_cost + execution_time * time_rate
        # Store metadata
        job.meta['execution_time'] = execution_time
        job.meta['worker_tag'] = worker_tag
        job.meta['retries'] = getattr(job, 'retry_count', 0)
        job.meta['success'] = True
        job.meta['cost'] = round(cost, 4)
        job.meta['runtime'] = runtime
        job.meta['filename'] = filename
        job.save_meta()
        logger.info(f"Job {job.id} completed in {execution_time:.3f}s, cost: ${cost:.4f}")
        return result

    except Exception as e:
        execution_time = time.time() - start_time
        cost = base_cost + execution_time * time_rate
        job.meta['execution_time'] = execution_time
        job.meta['retries'] = getattr(job, 'retries_left', 0)
        job.meta['success'] = False
        job.meta['worker_tag'] = worker_tag
        job.meta['cost'] = round(cost, 4)
        job.meta['runtime'] = runtime
        job.meta['filename'] = filename
        job.save_meta()
        logger.error(f"Job {job.id} failed after {execution_time:.3f}s, cost: ${cost:.4f}: {str(e)}")
        raise