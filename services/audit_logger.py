from datetime import datetime
from flask import current_app, g
from models_new import db, AuditLog, User
from sqlalchemy import event
import json
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    """Audit logging service for tracking changes to key tables"""
    
    def __init__(self):
        self.tracked_tables = {
            'mawbs': 'MAWB',
            'hawbs': 'HAWB', 
            'mawb_events': 'MAWBEvent',
            'hawb_events': 'HAWBEvent',
            'mawb_workflows': 'MAWBWorkflow',
            'scheduled_jobs': 'ScheduledJob',
            'user': 'User',
            'roles': 'Role',
            'features': 'Feature',
            'carriers': 'Carrier',
            'file_types': 'FileType'
        }
    
    def log_change(self, table_name, record_id, action, old_values=None, new_values=None, user_id=None):
        """Log a change to the audit log"""
        try:
            if user_id is None:
                # Try to get current user from Flask-Login
                from flask_login import current_user
                if hasattr(current_user, 'id') and current_user.is_authenticated:
                    user_id = current_user.id
            
            audit_entry = AuditLog(
                table_name=table_name,
                record_id=record_id,
                action=action,
                old_values=old_values,
                new_values=new_values,
                changed_by=user_id,
                changed_at=datetime.utcnow()
            )
            
            db.session.add(audit_entry)
            db.session.commit()
            
            logger.info(f"Audit log: {action} on {table_name}:{record_id} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging audit entry: {str(e)}")
            db.session.rollback()
    
    def log_insert(self, table_name, record_id, new_values=None, user_id=None):
        """Log an insert operation"""
        self.log_change(table_name, record_id, 'INSERT', new_values=new_values, user_id=user_id)
    
    def log_update(self, table_name, record_id, old_values=None, new_values=None, user_id=None):
        """Log an update operation"""
        self.log_change(table_name, record_id, 'UPDATE', old_values=old_values, new_values=new_values, user_id=user_id)
    
    def log_delete(self, table_name, record_id, old_values=None, user_id=None):
        """Log a delete operation"""
        self.log_change(table_name, record_id, 'DELETE', old_values=old_values, user_id=user_id)
    
    def get_changes_for_record(self, table_name, record_id, limit=50):
        """Get audit log entries for a specific record"""
        return AuditLog.query.filter_by(
            table_name=table_name,
            record_id=record_id
        ).order_by(AuditLog.changed_at.desc()).limit(limit).all()
    
    def get_changes_by_user(self, user_id, limit=50):
        """Get audit log entries by a specific user"""
        return AuditLog.query.filter_by(
            changed_by=user_id
        ).order_by(AuditLog.changed_at.desc()).limit(limit).all()
    
    def get_recent_changes(self, table_name=None, limit=50):
        """Get recent audit log entries"""
        query = AuditLog.query
        if table_name:
            query = query.filter_by(table_name=table_name)
        
        return query.order_by(AuditLog.changed_at.desc()).limit(limit).all()
    
    def format_values_for_log(self, obj, include_fields=None, exclude_fields=None):
        """Format object values for audit logging"""
        if obj is None:
            return None
        
        if hasattr(obj, '__table__'):
            # SQLAlchemy model instance
            data = {}
            for column in obj.__table__.columns:
                field_name = column.name
                
                # Skip excluded fields
                if exclude_fields and field_name in exclude_fields:
                    continue
                
                # Include only specified fields
                if include_fields and field_name not in include_fields:
                    continue
                
                # Skip sensitive fields
                if field_name in ['password_hash', 'api_key', 'secret_key']:
                    data[field_name] = '[REDACTED]'
                    continue
                
                value = getattr(obj, field_name)
                
                # Handle datetime objects
                if hasattr(value, 'isoformat'):
                    data[field_name] = value.isoformat()
                else:
                    data[field_name] = value
            
            return data
        else:
            # Regular dictionary or object
            return obj
    
    def setup_model_hooks(self, app):
        """Set up SQLAlchemy event hooks for automatic audit logging"""
        from sqlalchemy import event
        
        @event.listens_for(db.session, 'after_flush')
        def after_flush(session, context):
            """Log changes after session flush"""
            for obj in session.new:
                if hasattr(obj, '__tablename__') and obj.__tablename__ in self.tracked_tables:
                    table_name = obj.__tablename__
                    record_id = getattr(obj, 'id', None)
                    if record_id:
                        new_values = self.format_values_for_log(obj)
                        self.log_insert(table_name, record_id, new_values)
            
            for obj in session.dirty:
                if hasattr(obj, '__tablename__') and obj.__tablename__ in self.tracked_tables:
                    table_name = obj.__tablename__
                    record_id = getattr(obj, 'id', None)
                    if record_id:
                        # Get the original state
                        original_state = session.get_state(obj)
                        if original_state:
                            old_values = self.format_values_for_log(original_state)
                            new_values = self.format_values_for_log(obj)
                            self.log_update(table_name, record_id, old_values, new_values)
            
            for obj in session.deleted:
                if hasattr(obj, '__tablename__') and obj.__tablename__ in self.tracked_tables:
                    table_name = obj.__tablename__
                    record_id = getattr(obj, 'id', None)
                    if record_id:
                        old_values = self.format_values_for_log(obj)
                        self.log_delete(table_name, record_id, old_values)

# Global audit logger instance
audit_logger = AuditLogger()

def init_audit_logger(app):
    """Initialize audit logger with the Flask app"""
    audit_logger.setup_model_hooks(app)
    logger.info("Audit logger initialized")

def log_manual_change(table_name, record_id, action, old_values=None, new_values=None, user_id=None):
    """Manually log a change (for operations not caught by SQLAlchemy hooks)"""
    audit_logger.log_change(table_name, record_id, action, old_values, new_values, user_id)

def get_audit_trail(table_name, record_id):
    """Get complete audit trail for a record"""
    return audit_logger.get_changes_for_record(table_name, record_id)

def get_user_activity(user_id):
    """Get all activity by a specific user"""
    return audit_logger.get_changes_by_user(user_id)

def get_recent_activity(table_name=None, limit=50):
    """Get recent activity across all tables or a specific table"""
    return audit_logger.get_recent_changes(table_name, limit) 