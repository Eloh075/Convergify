"""
Parallel Processing System with Thread Pool and Single Database Writer

Implements producer-consumer pattern:
- Worker threads: Process tasks via API calls
- Database writer thread: Writes results to database
- KeyPoolManager: Manages API key rotation and health
"""
import logging
import time
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from .gemini_client import GeminiClient
from .config import PipelineConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from processing a task"""
    task_id: str
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float = 0.0
    worker_id: int = 0


class KeyPoolManager:
    """Manages API keys with health tracking and circuit breaker"""
    
    def __init__(self, api_keys: List[str], cooldown_minutes: int = 1, shutdown_flag=None):
        self.available_keys = Queue()
        self.failed_keys = {}  # key -> failure_time
        self.all_keys = api_keys
        self.cooldown_seconds = cooldown_minutes * 60
        self.lock = threading.Lock()
        self.shutdown_flag = shutdown_flag or threading.Event()
        
        # Initialize queue with all keys
        for key in api_keys:
            self.available_keys.put(key)
        
        logger.info(f"KeyPoolManager initialized with {len(api_keys)} keys")
    
    def get_key(self, timeout: int = 30) -> Optional[str]:
        """Get an available API key"""
        # Check if any failed keys can be retried
        self._check_cooldown_keys()
        
        # Try to get key from queue
        try:
            key = self.available_keys.get(timeout=timeout)
            logger.debug(f"Checked out API key")
            return key
        except Empty:
            # No keys available, wait for cooldown to complete
            logger.warning("No API keys available, waiting for cooldown...")
            
            # Wait for at least one key to become available
            while not self.shutdown_flag.is_set():
                self._check_cooldown_keys()
                if not self.available_keys.empty():
                    key = self.available_keys.get(block=False)
                    logger.debug(f"Checked out API key after cooldown")
                    return key
                time.sleep(1)
            
            return None
    
    def return_key(self, key: str, success: bool = True):
        """Return a key to the pool"""
        if success:
            self.available_keys.put(key)
            logger.debug(f"Returned API key to pool")
        else:
            # Mark as failed with cooldown
            with self.lock:
                self.failed_keys[key] = time.time()
            logger.warning(f"Marked API key as failed (cooldown: {self.cooldown_seconds}s)")
    
    def _check_cooldown_keys(self):
        """Check if any failed keys can be retried after cooldown"""
        with self.lock:
            current_time = time.time()
            keys_to_retry = []
            
            for key, failure_time in list(self.failed_keys.items()):
                if current_time - failure_time >= self.cooldown_seconds:
                    keys_to_retry.append(key)
            
            # Return cooled-down keys to pool
            for key in keys_to_retry:
                del self.failed_keys[key]
                self.available_keys.put(key)
                logger.info(f"API key cooldown complete, returned to pool")
    
    def get_available_count(self) -> int:
        """Get count of available keys"""
        return self.available_keys.qsize()
    
    def get_stats(self) -> Dict[str, int]:
        """Get key pool statistics"""
        with self.lock:
            return {
                "total_keys": len(self.all_keys),
                "available": self.available_keys.qsize(),
                "failed": len(self.failed_keys)
            }


class ParallelProcessor:
    """Parallel processor with worker threads and single database writer"""
    
    def __init__(
        self,
        num_workers: int = 7,
        api_keys: Optional[List[str]] = None,
        max_retries: int = 3
    ):
        self.num_workers = num_workers
        self.max_retries = max_retries
        
        # Shutdown flag (must be created BEFORE KeyPoolManager)
        self.shutdown_flag = threading.Event()
        
        # Initialize key pool
        keys = api_keys or PipelineConfig.GEMINI_API_KEYS
        self.key_pool = KeyPoolManager(keys, shutdown_flag=self.shutdown_flag)
        
        # Queues
        self.task_queue = Queue()
        self.result_queue = Queue()
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "start_time": None
        }
        self.stats_lock = threading.Lock()
        
        logger.info(f"ParallelProcessor initialized with {num_workers} workers")
    
    def _worker_thread(self, worker_id: int):
        """Worker thread that processes tasks"""
        logger.info(f"Worker {worker_id} started")
        
        while not self.shutdown_flag.is_set():
            try:
                # Get task from queue (timeout to check shutdown flag)
                task = self.task_queue.get(timeout=1)
                
                if task is None:  # Shutdown signal
                    break
                
                # Process task
                result = self._process_task(task, worker_id)
                
                # Put result in result queue
                self.result_queue.put(result)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _process_task(self, task: Dict[str, Any], worker_id: int) -> ProcessingResult:
        """Process a single task with retry logic"""
        task_id = task.get("id", "unknown")
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                # Get API key
                api_key = self.key_pool.get_key()
                if not api_key:
                    raise Exception("No API keys available")
                
                # Create client and process
                client = GeminiClient(api_key=api_key)
                
                # Call the task's processing function
                process_func = task.get("process_func")
                task_data = task.get("data")
                
                result_data = process_func(client, task_data)
                
                # Return key as successful
                self.key_pool.return_key(api_key, success=True)
                
                # Success!
                processing_time = time.time() - start_time
                return ProcessingResult(
                    task_id=task_id,
                    success=True,
                    data=result_data,
                    processing_time=processing_time,
                    worker_id=worker_id
                )
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Task {task_id} attempt {attempt + 1} failed: {error_msg}")
                
                # Check if quota error
                is_quota_error = (
                    "429" in error_msg or
                    "quota" in error_msg.lower() or
                    "rate limit" in error_msg.lower()
                )
                
                if is_quota_error and api_key:
                    # Mark key as failed
                    self.key_pool.return_key(api_key, success=False)
                elif api_key:
                    # Return key for other errors
                    self.key_pool.return_key(api_key, success=True)
                
                # Last attempt failed
                if attempt == self.max_retries - 1:
                    processing_time = time.time() - start_time
                    return ProcessingResult(
                        task_id=task_id,
                        success=False,
                        data={},
                        error_message=error_msg,
                        processing_time=processing_time,
                        worker_id=worker_id
                    )
                
                # Wait before retry
                time.sleep(2 ** attempt)
        
        # Should never reach here
        return ProcessingResult(
            task_id=task_id,
            success=False,
            data={},
            error_message="Max retries exceeded",
            processing_time=time.time() - start_time,
            worker_id=worker_id
        )
    
    def _database_writer_thread(self, write_func):
        """Database writer thread that writes results"""
        logger.info("Database writer started")
        
        while not self.shutdown_flag.is_set():
            try:
                # Get result from queue (timeout to check shutdown flag)
                result = self.result_queue.get(timeout=1)
                
                if result is None:  # Shutdown signal
                    break
                
                # Write to database
                try:
                    write_func(result)
                    
                    # Update stats
                    with self.stats_lock:
                        if result.success:
                            self.stats["completed"] += 1
                        else:
                            self.stats["failed"] += 1
                    
                    logger.debug(f"Wrote result for task {result.task_id}")
                    
                except Exception as e:
                    logger.error(f"Database write error for task {result.task_id}: {e}")
                
                # Mark result as done
                self.result_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Database writer error: {e}")
        
        logger.info("Database writer stopped")
    
    def _monitoring_thread(self):
        """Monitoring thread that prints statistics"""
        logger.info("Monitoring thread started")
        
        while not self.shutdown_flag.is_set():
            time.sleep(5)
            
            if self.stats["start_time"]:
                elapsed = time.time() - self.stats["start_time"]
                
                with self.stats_lock:
                    completed = self.stats["completed"]
                    failed = self.stats["failed"]
                    total = self.stats["total_tasks"]
                
                remaining = total - completed - failed
                throughput = ((completed + failed) / elapsed) * 60 if elapsed > 0 else 0
                eta = remaining / (throughput / 60) if throughput > 0 else 0
                
                key_stats = self.key_pool.get_stats()
                
                print(f"""
📊 Status:
   Jobs: {completed + failed}/{total} ({(completed + failed)/total*100:.1f}%)
   Success: {completed} | Failed: {failed}
   Queue: {self.task_queue.qsize()} tasks, {self.result_queue.qsize()} results
   Keys: {key_stats['available']}/{key_stats['total_keys']} available, {key_stats['failed']} failed
   Throughput: {throughput:.1f} tasks/min
   ETA: {eta/60:.1f} minutes
                """)
        
        logger.info("Monitoring thread stopped")
    
    def process_tasks(
        self,
        tasks: List[Dict[str, Any]],
        write_func,
        enable_monitoring: bool = True
    ):
        """
        Process tasks in parallel
        
        Args:
            tasks: List of task dictionaries with 'id', 'data', and 'process_func'
            write_func: Function to write results to database
            enable_monitoring: Whether to enable monitoring thread
        """
        self.stats["total_tasks"] = len(tasks)
        self.stats["start_time"] = time.time()
        
        logger.info(f"Starting parallel processing of {len(tasks)} tasks")
        
        # Add tasks to queue
        for task in tasks:
            self.task_queue.put(task)
        
        # Start database writer thread
        db_thread = threading.Thread(
            target=self._database_writer_thread,
            args=(write_func,),
            daemon=True
        )
        db_thread.start()
        
        # Start monitoring thread
        if enable_monitoring:
            monitor_thread = threading.Thread(
                target=self._monitoring_thread,
                daemon=True
            )
            monitor_thread.start()
        
        # Start worker threads
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for i in range(self.num_workers):
                executor.submit(self._worker_thread, i)
            
            # Wait for all tasks to be processed
            self.task_queue.join()
            
            # Send shutdown signals to workers
            for _ in range(self.num_workers):
                self.task_queue.put(None)
        
        # Wait for all results to be written
        self.result_queue.join()
        
        # Send shutdown signal to database writer
        self.result_queue.put(None)
        db_thread.join()
        
        # Stop monitoring
        self.shutdown_flag.set()
        
        # Print final stats
        elapsed = time.time() - self.stats["start_time"]
        with self.stats_lock:
            completed = self.stats["completed"]
            failed = self.stats["failed"]
            total = self.stats["total_tasks"]
        
        print(f"""
{'='*80}
PARALLEL PROCESSING COMPLETE
{'='*80}
Total tasks: {total}
✅ Successful: {completed} ({completed/total*100:.1f}%)
❌ Failed: {failed} ({failed/total*100:.1f}%)
⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)
⚡ Average: {elapsed/total:.2f} seconds per task
{'='*80}
        """)
        
        logger.info("Parallel processing complete")
