import os
import time
import signal
import logging
import subprocess
from redis import Redis
from rq import Queue

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/autoscaler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Autoscaler:
    def __init__(self):
        self.redis_conn = Redis(host='localhost', port=6379)
        self.queue = Queue('default', connection=self.redis_conn)
        self.workers = []
        self.running = True
        
    def get_desired_workers(self, queue_size):
        """Calculate desired number of workers based on queue size"""
        return min(5, max(1, queue_size // 10 + 1))
    
    def spawn_worker(self):
        """Spawn a new worker process"""
        try:
            process = subprocess.Popen(['python', 'worker.py'])
            self.workers.append(process)
            logger.info(f"Spawned worker PID {process.pid}")
            return process
        except Exception as e:
            logger.error(f"Failed to spawn worker: {str(e)}")
            return None
    
    def kill_worker(self):
        """Kill the oldest worker process"""
        if len(self.workers) > 1: 
            worker = self.workers.pop(0)
            try:
                worker.terminate()
                worker.wait(timeout=10)
                logger.info(f"Terminated worker PID {worker.pid}")
            except subprocess.TimeoutExpired:
                worker.kill()
                logger.warning(f"Force killed worker PID {worker.pid}")
            except Exception as e:
                logger.error(f"Error terminating worker: {str(e)}")
    
    def cleanup_dead_workers(self):
        """Remove dead worker processes from list"""
        alive_workers = []
        for worker in self.workers:
            if worker.poll() is None:
                alive_workers.append(worker)
            else:
                logger.info(f"Removed dead worker PID {worker.pid}")
        self.workers = alive_workers
    
    def scale_workers(self):
        """Scale workers based on queue size"""
        queue_size = len(self.queue)
        current_workers = len(self.workers)
        desired_workers = self.get_desired_workers(queue_size)
        
        logger.info(f"Queue: {queue_size}, Workers: {current_workers}, Desired: {desired_workers}")
        
        if desired_workers > current_workers:
            for _ in range(desired_workers - current_workers):
                self.spawn_worker()
                time.sleep(1) 
        elif desired_workers < current_workers:
            for _ in range(current_workers - desired_workers):
                self.kill_worker()
    
    def run(self):
        """Main autoscaler loop"""
        logger.info("Starting autoscaler")
        
        if not self.workers:
            self.spawn_worker()
        
        while self.running:
            try:
                self.cleanup_dead_workers()
                self.scale_workers()
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"Autoscaler error: {str(e)}")
                time.sleep(5)
        
        logger.info("Shutting down workers")
        for worker in self.workers:
            try:
                worker.terminate()
                worker.wait(timeout=5)
            except:
                worker.kill()

if __name__ == '__main__':
    autoscaler = Autoscaler()
    
    def signal_handler(signum, frame):
        autoscaler.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    autoscaler.run()