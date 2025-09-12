import os
import logging
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue, Job
from executor import run_job

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
redis_conn = Redis(host='localhost', port=6379, decode_responses=True)
queue = Queue('default', connection=redis_conn)

@app.route('/submit', methods=['POST'])
def submit_job():
    try:
        data = request.get_json()
        function_name = data.get('function')
        payload = data.get('payload', {})
        
        if not function_name:
            return jsonify({'error': 'function name required'}), 400
        
        job = queue.enqueue(run_job, function_name, payload)
        logger.info(f"Job {job.id} submitted for function {function_name}")
        
        return jsonify({'job_id': job.id})
    
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>')
def get_status(job_id):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        status = job.get_status()
        result = {
            'job_id': job_id,
            'status': status,
            'execution_time': job.meta.get('execution_time'),
            'retries': job.meta.get('retries', 0)
        }
        
        if status == 'finished':
            result['result'] = job.result
        elif status == 'failed':
            result['error'] = str(job.exc_info)
            
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error getting status for job {job_id}: {str(e)}")
        return jsonify({'error': 'Job not found'}), 404

if __name__ == '__main__':
    logger.info("Starting Flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)