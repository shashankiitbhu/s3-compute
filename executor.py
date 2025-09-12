import os
import time
import logging
import importlib.util
from rq import get_current_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job(function_name, payload):
    """
    Execute a function with the given payload.
    Dynamically imports the function module and calls its handler.
    """
    worker_tag = os.environ.get('WORKER_TAG', 'unknown-worker')
    job = get_current_job()
    start_time = time.time()

    logger.info(f"Starting job {job.id} for function {function_name} on worker {worker_tag}")
    try:
        # Load function module
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
        
        # Store metadata
        job.meta['execution_time'] = execution_time
        job.meta['worker_tag'] = worker_tag
        job.meta['retries'] = getattr(job, 'retry_count', 0)
        job.meta['success'] = True
        job.save_meta()

        logger.info(f"Job {job.id} completed in {execution_time:.3f}s on {worker_tag}")
        return result

    except Exception as e:
        execution_time = time.time() - start_time
        job.meta['execution_time'] = execution_time
        job.meta['retries'] = getattr(job, 'retries_left', 0)
        job.meta['success'] = False
        job.meta['worker_tag'] = worker_tag
        job.save_meta()
        
        logger.error(f"Job {job.id} failed after {execution_time:.3f}s: {str(e)}")
        raise