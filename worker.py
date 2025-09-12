import os
import logging
from redis import Redis
from rq import Worker

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/worker.log'),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    redis_conn = Redis(host='localhost', port=6379)
    worker = Worker(['default'], connection=redis_conn)
    
    logging.info(f"Starting worker {worker.name}")
    worker.work()