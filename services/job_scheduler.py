import time
import schedule
import threading
from datetime import datetime, timedelta
from flask import current_app
from models_new import db, ScheduledJob, MAWB, MAWBEvent, User
import logging

logger = logging.getLogger(__name__)

class JobScheduler:
    """Background job scheduler for processing scheduled tasks"""
    
    def __init__(self):
        self.scheduler = schedule.Scheduler()
        self.running = False
        self.thread = None
        self.job_processor = None
    
    def init_app(self, app):
        """Initialize the job scheduler with the Flask app"""
        with app.app_context():
            # Import and instantiate JobProcessor here to avoid circular imports
            from services.workflow_engine import JobProcessor
            self.job_processor = JobProcessor()
            
            # Schedule regular jobs
            self.scheduler.every(1).minutes.do(self.process_pending_jobs)
            self.scheduler.every().day.at("09:00").do(self.check_overdue_mawbs)
            self.scheduler.every().day.at("14:00").do(self.send_daily_reminders)
    
    def start(self):
        """Start the job scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Job scheduler started")
    
    def stop(self):
        """Stop the job scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Job scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                self.scheduler.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Wait before retrying
    
    def process_pending_jobs(self):
        """Process all pending jobs that are due"""
        if not self.job_processor:
            logger.warning("Job processor not initialized")
            return
        
        try:
            self.job_processor.process_pending_jobs()
        except Exception as e:
            logger.error(f"Error processing pending jobs: {str(e)}")
    
    def check_overdue_mawbs(self):
        """Check for overdue MAWBs and send alerts"""
        try:
            with current_app.app_context():
                overdue_mawbs = MAWB.query.filter(
                    MAWB.lfd < datetime.now().date(),
                    MAWB.status == 'in_progress'
                ).all()
                
                for mawb in overdue_mawbs:
                    logger.warning(f"MAWB {mawb.mawb_number} is overdue (LFD: {mawb.lfd})")
                    # Send alert email or notification
                    
        except Exception as e:
            logger.error(f"Error checking overdue MAWBs: {str(e)}")
    
    def send_daily_reminders(self):
        """Send daily reminders for pending tasks"""
        try:
            with current_app.app_context():
                # Get MAWBs approaching LFD (within 3 days)
                three_days_from_now = datetime.now().date() + timedelta(days=3)
                approaching_lfd = MAWB.query.filter(
                    MAWB.lfd <= three_days_from_now,
                    MAWB.lfd >= datetime.now().date(),
                    MAWB.status == 'in_progress'
                ).all()
                
                for mawb in approaching_lfd:
                    days_left = (mawb.lfd - datetime.now().date()).days
                    logger.info(f"MAWB {mawb.mawb_number} LFD in {days_left} days")
                    # Send reminder email
                    
        except Exception as e:
            logger.error(f"Error sending daily reminders: {str(e)}")
    
    def schedule_job(self, job_type, run_at, payload=None, mawb_id=None, hawb_id=None):
        """Schedule a new job"""
        try:
            with current_app.app_context():
                job = ScheduledJob(
                    mawb_id=mawb_id,
                    hawb_id=hawb_id,
                    job_type=job_type,
                    run_at=run_at,
                    payload=payload
                )
                
                db.session.add(job)
                db.session.commit()
                
                logger.info(f"Scheduled job {job_type} for {run_at}")
                return job
                
        except Exception as e:
            logger.error(f"Error scheduling job: {str(e)}")
            return None

# Global job scheduler instance
job_scheduler = JobScheduler() 