from datetime import datetime, timedelta
from flask import current_app
from models_new import (
    db, MAWB, MAWBWorkflow, WorkflowStep, ScheduledJob, 
    MAWBEvent, User, EmailTemplate, EmailLog
)
import json
import logging

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Workflow engine for managing MAWB lifecycle"""
    
    def __init__(self):
        self.workflow_steps = {}
        # Don't load workflow steps during initialization to avoid app context issues
    
    def _load_workflow_steps(self):
        """Load workflow steps from database"""
        steps = {}
        try:
            # Only load if we have an app context
            if current_app:
                for step in WorkflowStep.query.filter_by(is_active=True).all():
                    steps[step.code] = {
                        'id': step.id,
                        'name': step.name,
                        'description': step.description,
                        'next_step': step.next_step
                    }
        except Exception as e:
            logger.warning(f"Could not load workflow steps: {str(e)}")
            # Return empty dict if tables don't exist yet or no app context
            steps = {}
        return steps
    
    def get_workflow_steps(self):
        """Get workflow steps, loading them if needed"""
        if not self.workflow_steps:
            self.workflow_steps = self._load_workflow_steps()
        return self.workflow_steps
    
    def create_workflow(self, mawb_id, initial_step='T01'):
        """Create a new workflow for a MAWB"""
        try:
            # Check if workflow already exists
            existing = MAWBWorkflow.query.filter_by(
                mawb_id=mawb_id, is_active=True
            ).first()
            
            if existing:
                return existing
            
            workflow = MAWBWorkflow(
                mawb_id=mawb_id,
                current_step=initial_step
            )
            
            db.session.add(workflow)
            db.session.commit()
            
            logger.info(f"Created workflow for MAWB {mawb_id} with step {initial_step}")
            return workflow
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating workflow for MAWB {mawb_id}: {str(e)}")
            raise
    
    def advance_workflow(self, mawb_id, user_id, event_details=None):
        """Advance workflow to next step"""
        try:
            workflow = MAWBWorkflow.query.filter_by(
                mawb_id=mawb_id, is_active=True
            ).first()
            
            if not workflow:
                raise ValueError(f"No active workflow found for MAWB {mawb_id}")
            
            if workflow.is_completed:
                raise ValueError(f"Workflow for MAWB {mawb_id} is already completed")
            
            workflow_steps = self.get_workflow_steps()
            current_step_info = workflow_steps.get(workflow.current_step)
            if not current_step_info:
                raise ValueError(f"Invalid workflow step: {workflow.current_step}")
            
            next_step = current_step_info['next_step']
            if not next_step:
                raise ValueError(f"No next step defined for {workflow.current_step}")
            
            # Update workflow
            old_step = workflow.current_step
            workflow.current_step = next_step
            workflow.updated_at = datetime.utcnow()
            
            # Check if workflow is completed
            if next_step == 'COMPLETE':
                workflow.completed_at = datetime.utcnow()
                mawb = MAWB.query.get(mawb_id)
                if mawb:
                    mawb.status = 'complete'
                    mawb.progress = 'delivered'
            
            # Create workflow event
            event = MAWBEvent(
                mawb_id=mawb_id,
                event_type='workflow_advanced',
                event_time=datetime.utcnow(),
                details={
                    'from_step': old_step,
                    'to_step': next_step,
                    'step_name': current_step_info['name'],
                    'user_id': user_id,
                    **(event_details or {})
                },
                created_by=user_id
            )
            
            db.session.add(event)
            db.session.commit()
            
            logger.info(f"Advanced workflow for MAWB {mawb_id}: {old_step} -> {next_step}")
            
            # Trigger step-specific actions
            self._handle_step_actions(mawb_id, next_step, user_id)
            
            return workflow
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error advancing workflow for MAWB {mawb_id}: {str(e)}")
            raise
    
    def _handle_step_actions(self, mawb_id, step_code, user_id):
        """Handle step-specific actions"""
        mawb = MAWB.query.get(mawb_id)
        if not mawb:
            return
        
        if step_code == 'T03':  # Pickup Scheduled
            # Schedule pickup reminder
            self._schedule_pickup_reminder(mawb_id)
            
        elif step_code == 'T05':  # At Origin Port
            # Send pre-alert email
            self._send_pre_alert_email(mawb_id)
            
        elif step_code == 'T06':  # Loaded on Vessel
            # Schedule LFD reminders
            if mawb.lfd:
                self._schedule_lfd_reminders(mawb_id, mawb.lfd)
                
        elif step_code == 'T11':  # Customs Clearance
            # Schedule ISC payment reminders
            self._schedule_isc_reminders(mawb_id)
            
        elif step_code == 'T14':  # Delivered
            # Schedule empty return reminder
            self._schedule_empty_return_reminder(mawb_id)
    
    def _schedule_pickup_reminder(self, mawb_id):
        """Schedule pickup reminder job"""
        reminder_time = datetime.utcnow() + timedelta(hours=24)
        
        job = ScheduledJob(
            mawb_id=mawb_id,
            job_type='pickup_reminder',
            run_at=reminder_time,
            payload={'reminder_type': 'pickup'}
        )
        
        db.session.add(job)
        db.session.commit()
    
    def _schedule_lfd_reminders(self, mawb_id, lfd_date):
        """Schedule LFD reminder jobs"""
        # 3 days before LFD
        reminder_3_days = lfd_date - timedelta(days=3)
        if reminder_3_days > datetime.now().date():
            job = ScheduledJob(
                mawb_id=mawb_id,
                job_type='lfd_reminder',
                run_at=datetime.combine(reminder_3_days, datetime.min.time()),
                payload={'reminder_type': 'lfd_3_days'}
            )
            db.session.add(job)
        
        # 1 day before LFD
        reminder_1_day = lfd_date - timedelta(days=1)
        if reminder_1_day > datetime.now().date():
            job = ScheduledJob(
                mawb_id=mawb_id,
                job_type='lfd_reminder',
                run_at=datetime.combine(reminder_1_day, datetime.min.time()),
                payload={'reminder_type': 'lfd_1_day'}
            )
            db.session.add(job)
        
        db.session.commit()
    
    def _schedule_isc_reminders(self, mawb_id):
        """Schedule ISC payment reminders"""
        # Morning reminder (9 AM)
        morning_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        if morning_time < datetime.now():
            morning_time += timedelta(days=1)
        
        job = ScheduledJob(
            mawb_id=mawb_id,
            job_type='isc_reminder',
            run_at=morning_time,
            payload={'reminder_type': 'isc_morning'}
        )
        db.session.add(job)
        
        # Afternoon reminder (2 PM)
        afternoon_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        if afternoon_time < datetime.now():
            afternoon_time += timedelta(days=1)
        
        job = ScheduledJob(
            mawb_id=mawb_id,
            job_type='isc_reminder',
            run_at=afternoon_time,
            payload={'reminder_type': 'isc_afternoon'}
        )
        db.session.add(job)
        
        db.session.commit()
    
    def _schedule_empty_return_reminder(self, mawb_id):
        """Schedule empty return reminder"""
        reminder_time = datetime.utcnow() + timedelta(days=7)
        
        job = ScheduledJob(
            mawb_id=mawb_id,
            job_type='empty_return_reminder',
            run_at=reminder_time,
            payload={'reminder_type': 'empty_return'}
        )
        
        db.session.add(job)
        db.session.commit()
    
    def _send_pre_alert_email(self, mawb_id):
        """Send pre-alert email"""
        try:
            mawb = MAWB.query.get(mawb_id)
            if not mawb:
                return
            
            # Get pre-alert template
            template = EmailTemplate.query.filter_by(
                name='PRE-ALERT', is_active=True
            ).first()
            
            if not template:
                logger.warning("PRE-ALERT email template not found")
                return
            
            # Render template
            email_body = template.render_template(
                mawb_number=mawb.mawb_number,
                origin_port=mawb.origin_port or 'N/A',
                dest_port=mawb.dest_port or 'N/A',
                eta=mawb.eta.strftime('%Y-%m-%d') if mawb.eta else 'N/A',
                consignee=mawb.consignee or 'N/A',
                pieces=mawb.pieces or 0,
                weight=mawb.weight or 0
            )
            
            # Log email (in real implementation, send actual email)
            email_log = EmailLog(
                cargo_id=None,  # Will be updated when we link to cargo
                template_name='PRE-ALERT',
                recipients='operations@company.com',  # Configure based on business rules
                subject=template.subject,
                body=email_body,
                sent_by_id=1  # System user
            )
            
            db.session.add(email_log)
            db.session.commit()
            
            logger.info(f"Pre-alert email logged for MAWB {mawb_id}")
            
        except Exception as e:
            logger.error(f"Error sending pre-alert email for MAWB {mawb_id}: {str(e)}")

class JobProcessor:
    """Process scheduled jobs"""
    
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
    
    def process_pending_jobs(self):
        """Process all pending jobs that are due"""
        try:
            # Only process if we have an app context
            if not current_app:
                logger.warning("No Flask app context available for job processing")
                return
                
            now = datetime.utcnow()
            pending_jobs = ScheduledJob.query.filter(
                ScheduledJob.status == 'pending',
                ScheduledJob.run_at <= now
            ).all()
            
            for job in pending_jobs:
                self._process_job(job)
                
        except Exception as e:
            logger.error(f"Error processing pending jobs: {str(e)}")
    
    def _process_job(self, job):
        """Process a single job"""
        try:
            logger.info(f"Processing job {job.id} of type {job.job_type}")
            
            if job.job_type == 'pickup_reminder':
                self._handle_pickup_reminder(job)
            elif job.job_type == 'lfd_reminder':
                self._handle_lfd_reminder(job)
            elif job.job_type == 'isc_reminder':
                self._handle_isc_reminder(job)
            elif job.job_type == 'empty_return_reminder':
                self._handle_empty_return_reminder(job)
            else:
                logger.warning(f"Unknown job type: {job.job_type}")
                job.status = 'failed'
                job.attempts += 1
            
            # Mark job as completed
            job.status = 'completed'
            job.updated_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            job.status = 'failed'
            job.attempts += 1
            job.updated_at = datetime.utcnow()
            
            if job.attempts >= job.max_attempts:
                job.status = 'failed_permanent'
            
            db.session.commit()
    
    def _handle_pickup_reminder(self, job):
        """Handle pickup reminder"""
        mawb = MAWB.query.get(job.mawb_id)
        if not mawb:
            return
        
        # Create reminder event
        event = MAWBEvent(
            mawb_id=job.mawb_id,
            event_type='pickup_reminder_sent',
            details={'reminder_type': 'pickup'},
            created_by=1  # System user
        )
        db.session.add(event)
        
        logger.info(f"Pickup reminder processed for MAWB {job.mawb_id}")
    
    def _handle_lfd_reminder(self, job):
        """Handle LFD reminder"""
        mawb = MAWB.query.get(job.mawb_id)
        if not mawb:
            return
        
        reminder_type = job.payload.get('reminder_type', 'unknown')
        
        # Create reminder event
        event = MAWBEvent(
            mawb_id=job.mawb_id,
            event_type='lfd_reminder_sent',
            details={
                'reminder_type': reminder_type,
                'lfd_date': mawb.lfd.isoformat() if mawb.lfd else None
            },
            created_by=1  # System user
        )
        db.session.add(event)
        
        logger.info(f"LFD reminder processed for MAWB {job.mawb_id}: {reminder_type}")
    
    def _handle_isc_reminder(self, job):
        """Handle ISC payment reminder"""
        mawb = MAWB.query.get(job.mawb_id)
        if not mawb:
            return
        
        reminder_type = job.payload.get('reminder_type', 'unknown')
        
        # Create reminder event
        event = MAWBEvent(
            mawb_id=job.mawb_id,
            event_type='isc_reminder_sent',
            details={'reminder_type': reminder_type},
            created_by=1  # System user
        )
        db.session.add(event)
        
        logger.info(f"ISC reminder processed for MAWB {job.mawb_id}: {reminder_type}")
    
    def _handle_empty_return_reminder(self, job):
        """Handle empty return reminder"""
        mawb = MAWB.query.get(job.mawb_id)
        if not mawb:
            return
        
        # Create reminder event
        event = MAWBEvent(
            mawb_id=job.mawb_id,
            event_type='empty_return_reminder_sent',
            details={'reminder_type': 'empty_return'},
            created_by=1  # System user
        )
        db.session.add(event)
        
        logger.info(f"Empty return reminder processed for MAWB {job.mawb_id}")

# Global instances
# job_processor = JobProcessor() 