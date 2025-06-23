from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

from extensions import db, login_manager

# Import all models from models_new.py to avoid duplicates
from models_new import (
    responsible_association, User, Role, Feature, RoleFeature, UserOverride,
    Cargo, Attachment, Bill, EventLog, EmailLog, ExternalContact, 
    EmailTemplate, StatusMilestone
)

# Predefined permissions
PERMISSIONS = {
    'view_cargo': 'View cargo details',
    'edit_cargo': 'Edit cargo information',
    'upload_attachments': 'Upload attachments',
    'create_bills': 'Create bills',
    'send_emails': 'Send emails',
    'sign_do_pod': 'Sign DO/POD documents',
    'view_archives': 'View archives',
    'archive_records': 'Archive inspection/destruction records',
    'modify_status': 'Modify cargo status',
    'manage_users': 'Manage users',
    'manage_templates': 'Manage email templates',
    'manage_roles': 'Manage role information',
    'log_inspection': 'Log inspection records',
    'log_destruction': 'Log destruction records'
}

# Predefined roles with permissions based on Appendix D: User Permissions Matrix (Flipped Axis)
DEFAULT_ROLES = {
    'Admin': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 
        'send_emails', 'view_archives', 'archive_records', 'modify_status', 
        'manage_users', 'manage_templates', 'manage_roles'
    ],
    'US Operations Staff': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 
        'send_emails', 'view_archives', 'archive_records', 'modify_status'
    ],
    'Domestic Operations Staff': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 
        'send_emails', 'view_archives', 'archive_records', 'modify_status'
    ],
    'Warehouse Staff': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'sign_do_pod', 'view_archives'
    ],
    'Customs Brokers (log only)': [
        'archive_records'
    ],
    'Airline Representatives (log only)': [
        'archive_records'
    ],
    'Inspection Centers (CES) (log only)': [
        'archive_records'
    ],
    'Destruction Companies (log only)': [
        'archive_records'
    ]
}

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None



