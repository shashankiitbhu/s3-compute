import os
import logging
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
from rq.job import Job
from executor import run_job

import threading
import time
import uuid
from datetime import datetime
# Setup logging
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
redis_conn = Redis(host='localhost', port=6379)
queue = Queue('default', connection=redis_conn)

# In-memory trigger storage
triggers = []

# Background scheduler thread
def scheduler_loop():
    while True:
        now = datetime.now()
        for trig in triggers:
            if trig['type'] == 'cron':
                # Simple cron: run every N seconds
                interval = trig.get('interval', 60)
                last_run = trig.get('last_run', 0)
                if time.time() - last_run >= interval:
                    queue.enqueue(run_job, trig['function'], trig.get('payload', {}))
                    trig['last_run'] = time.time()
        time.sleep(1)

threading.Thread(target=scheduler_loop, daemon=True).start()


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

@app.route('/trigger', methods=['POST'])
def register_trigger():
    """Register a trigger (cron or webhook)"""
    try:
        data = request.get_json()
        trig_type = data.get('type')
        function = data.get('function')
        payload = data.get('payload', {})
        if not trig_type or not function:
            return jsonify({'error': 'type and function required'}), 400
        trig = {
            'id': str(uuid.uuid4()),
            'type': trig_type,
            'function': function,
            'payload': payload
        }
        if trig_type == 'cron':
            trig['interval'] = data.get('interval', 60)  # seconds
            trig['last_run'] = 0
        if trig_type == 'webhook':
            trig['event_type'] = data.get('event_type')
        triggers.append(trig)
        logger.info(f"Registered trigger {trig}")
        return jsonify({'trigger_id': trig['id']})
    except Exception as e:
        logger.error(f"Error registering trigger: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/event', methods=['POST'])
def receive_event():
    """Receive an event and enqueue job if trigger matches"""
    try:
        data = request.get_json()
        event_type = data.get('event_type')
        for trig in triggers:
            if trig['type'] == 'webhook' and trig.get('event_type') == event_type:
                queue.enqueue(run_job, trig['function'], trig.get('payload', {}))
                logger.info(f"Triggered function {trig['function']} for event {event_type}")
        return jsonify({'status': 'event processed'})
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return jsonify({'error': str(e)}), 500
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
            'retries': job.meta.get('retries', 0),
            'cost': job.meta.get('cost', None)
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