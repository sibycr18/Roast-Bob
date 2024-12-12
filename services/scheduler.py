from datetime import datetime, timedelta
import asyncio
import logging
from typing import Callable, Dict, Optional
from utils.logger import get_logger

class SchedulerService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.tasks: Dict[str, asyncio.Task] = {}
        self.intervals: Dict[str, int] = {}
        self.last_run: Dict[str, datetime] = {}
        self.is_running = False

    async def schedule_task(self, name: str, task: Callable, interval_minutes: int):
        """Schedule a task to run at specified intervals"""
        self.intervals[name] = interval_minutes
        self.last_run[name] = datetime.now()
        
        async def run_scheduled_task():
            while self.is_running:
                try:
                    await task()
                    self.last_run[name] = datetime.now()
                    self.logger.info(f"Successfully ran scheduled task: {name}")
                except Exception as e:
                    self.logger.error(f"Error in scheduled task {name}: {str(e)}")
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
        
        self.tasks[name] = asyncio.create_task(run_scheduled_task())
        self.logger.info(f"Scheduled task {name} to run every {interval_minutes} minutes")

    def start(self):
        """Start the scheduler"""
        self.is_running = True
        self.logger.info("Scheduler started")

    async def stop(self):
        """Stop the scheduler and cancel all tasks"""
        self.is_running = False
        for name, task in self.tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self.logger.info(f"Cancelled scheduled task: {name}")
        self.tasks.clear()
        self.logger.info("Scheduler stopped")

    def get_task_status(self, name: str) -> Dict:
        """Get status of a scheduled task"""
        if name not in self.intervals:
            return {"status": "not_found"}
        
        next_run = self.last_run[name] + timedelta(minutes=self.intervals[name])
        return {
            "status": "running" if self.is_running else "stopped",
            "last_run": self.last_run[name],
            "next_run": next_run,
            "interval_minutes": self.intervals[name]
        }