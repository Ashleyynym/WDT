from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

from extensions import db, login_manager

# ============================================================================
# NEW BACKEND SCHEMA MODELS
# ============================================================================

class Carrier(db.Model):
    __tablename__ = 'carriers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    api_endpoint = db.Column(db.String(255))
    api_key = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mawbs = db.relationship('MAWB', backref='carrier')

class FileType(db.Model):
    __tablename__ = 'file_types'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feature(db.Model):
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RoleFeature(db.Model):
    __tablename__ = 'role_features'
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserOverride(db.Model):
    __tablename__ = 'user_overrides'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'), nullable=False)
    granted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feature = db.relationship('Feature')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'feature_id'),)

class MAWB(db.Model):
    __tablename__ = 'mawbs'
    
    id = db.Column(db.Integer, primary_key=True)
    mawb_number = db.Column(db.String(50), unique=True, nullable=False)
    origin_port = db.Column(db.String(100))
    dest_port = db.Column(db.String(100))
    carrier_id = db.Column(db.Integer, db.ForeignKey('carriers.id'))
    eta = db.Column(db.Date)
    etd = db.Column(db.Date)
    lfd = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default='in_progress')
    progress = db.Column(db.String(50), nullable=False, default='not_shipped')
    consignee = db.Column(db.String(255))
    shipper = db.Column(db.String(255))
    pieces = db.Column(db.Integer)
    weight = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hawbs = db.relationship('HAWB', backref='mawb', cascade='all, delete-orphan')
    events = db.relationship('MAWBEvent', backref='mawb', cascade='all, delete-orphan')
    workflows = db.relationship('MAWBWorkflow', backref='mawb', cascade='all, delete-orphan')
    scheduled_jobs = db.relationship('ScheduledJob', backref='mawb', cascade='all, delete-orphan')
    
    @property
    def time_until_lfd(self):
        """Calculate days until LFD"""
        if self.lfd:
            delta = self.lfd - datetime.now().date()
            return delta.days
        return None
    
    @property
    def is_overdue(self):
        """Check if LFD has passed"""
        if self.lfd:
            return self.lfd < datetime.now().date()
        return False

class HAWB(db.Model):
    __tablename__ = 'hawbs'
    
    id = db.Column(db.Integer, primary_key=True)
    hawb_number = db.Column(db.String(50), unique=True, nullable=False)
    mawb_id = db.Column(db.Integer, db.ForeignKey('mawbs.id'), nullable=False)
    consignee = db.Column(db.String(255))
    shipper = db.Column(db.String(255))
    pieces = db.Column(db.Integer)
    weight = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='in_progress')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('HAWBEvent', backref='hawb', cascade='all, delete-orphan')
    scheduled_jobs = db.relationship('ScheduledJob', backref='hawb', cascade='all, delete-orphan')

class MAWBEvent(db.Model):
    __tablename__ = 'mawb_events'
    
    id = db.Column(db.Integer, primary_key=True)
    mawb_id = db.Column(db.Integer, db.ForeignKey('mawbs.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')

class HAWBEvent(db.Model):
    __tablename__ = 'hawb_events'
    
    id = db.Column(db.Integer, primary_key=True)
    hawb_id = db.Column(db.Integer, db.ForeignKey('hawbs.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')

class WorkflowStep(db.Model):
    __tablename__ = 'workflow_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    next_step = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MAWBWorkflow(db.Model):
    __tablename__ = 'mawb_workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    mawb_id = db.Column(db.Integer, db.ForeignKey('mawbs.id'), nullable=False)
    current_step = db.Column(db.String(50), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def is_completed(self):
        return self.completed_at is not None

class ScheduledJob(db.Model):
    __tablename__ = 'scheduled_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    mawb_id = db.Column(db.Integer, db.ForeignKey('mawbs.id'))
    hawb_id = db.Column(db.Integer, db.ForeignKey('hawbs.id'))
    job_type = db.Column(db.String(100), nullable=False)
    run_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    payload = db.Column(db.JSON)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    max_attempts = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def can_retry(self):
        return self.attempts < self.max_attempts and self.status in ['failed', 'pending']

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')

# ============================================================================
# ENHANCED EXISTING MODELS
# ============================================================================

# Association table between Cargo and User (for responsible persons)
responsible_association = db.Table(
    'responsible_association',
    db.Column('cargo_id', db.Integer, db.ForeignKey('cargo.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Role(db.Model):
    __tablename__ = "role"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string of permissions
    
    # New relationships for enhanced permissions
    features = db.relationship('Feature', secondary='role_features', backref='roles')
    users    = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"
    
    def has_permission(self, permission):
        """Check if role has specific permission"""
        # Check if role has the feature with the given key
        feature = Feature.query.filter_by(key=permission).first()
        if not feature:
            return False
        
        # Check if this role has this feature
        return feature in self.features

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

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(64), unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(128), nullable=False)
    role_id        = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active      = db.Column(db.Boolean, default=True)

    assigned_cargos = db.relationship(
        'Cargo',
        secondary=responsible_association,
        back_populates='responsibles'
    )
    
    # New relationships for enhanced permissions
    user_overrides = db.relationship('UserOverride', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        # Check role permissions
        if self.role and self.role.has_permission(permission):
            return True
        
        # Check user overrides - join with Feature table to get feature key
        override = self.user_overrides.join(Feature).filter_by(key=permission).first()
        if override:
            return override.granted
        
        return False
    
    def can_view_cargo(self):
        return self.has_permission('view_cargo')
    
    def can_edit_cargo(self):
        return self.has_permission('edit_cargo')
    
    def can_upload_attachments(self):
        return self.has_permission('upload_attachments')
    
    def can_create_bills(self):
        return self.has_permission('create_bills')
    
    def can_send_emails(self):
        return self.has_permission('send_emails')
    
    def can_sign_do_pod(self):
        return self.has_permission('sign_do_pod')
    
    def can_manage_users(self):
        return self.has_permission('manage_users')

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

class Cargo(db.Model):
    __tablename__ = "cargo"
    id            = db.Column(db.Integer, primary_key=True)
    main_awb      = db.Column(db.String(100), unique=True, nullable=False)
    flight_no     = db.Column(db.String(50), nullable=True)
    eta           = db.Column(db.DateTime, nullable=True)
    lfd_date      = db.Column(db.DateTime, nullable=True)
    status        = db.Column(db.String(50), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    origin        = db.Column(db.String(100), nullable=True)
    destination   = db.Column(db.String(100), nullable=True)
    weight        = db.Column(db.Float, nullable=True)
    pieces        = db.Column(db.Integer, nullable=True)
    description   = db.Column(db.Text, nullable=True)
    special_handling = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived   = db.Column(db.Boolean, default=False)

    responsibles = db.relationship(
        'User',
        secondary=responsible_association,
        back_populates='assigned_cargos'
    )

    attachments = db.relationship('Attachment', backref='cargo', lazy=True)
    bills       = db.relationship('Bill', backref='cargo', lazy=True)
    events      = db.relationship('EventLog', backref='cargo', lazy=True)
    emails      = db.relationship('EmailLog', backref='cargo', lazy=True)
    milestones  = db.relationship('StatusMilestone', backref='cargo', lazy=True, order_by='StatusMilestone.timestamp')

    def __repr__(self):
        return f"<Cargo AWB={self.main_awb} Flight={self.flight_no}>"
    
    def get_lfd_days_left(self):
        """Calculate days left until LFD"""
        if not self.eta or not self.lfd_date:
            return None
        from datetime import date
        today = date.today()
        lfd_date = self.lfd_date.date()
        return (lfd_date - today).days
    
    def is_approaching_lfd(self, days_threshold=3):
        """Check if cargo is approaching LFD"""
        days_left = self.get_lfd_days_left()
        return days_left is not None and 0 <= days_left <= days_threshold
    
    def has_unpaid_bills(self):
        """Check if cargo has unpaid bills"""
        return any(bill.payment_status == 'Unpaid' for bill in self.bills)

class Attachment(db.Model):
    __tablename__ = "attachment"
    id          = db.Column(db.Integer, primary_key=True)
    cargo_id    = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)
    filename    = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_type   = db.Column(db.String(50))  # ISC Payment, DO, Inspection, etc.
    file_size   = db.Column(db.Integer)  # File size in bytes
    mime_type   = db.Column(db.String(100))
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes       = db.Column(db.String(200))
    is_archived = db.Column(db.Boolean, default=False)

    uploader = db.relationship('User', backref='uploaded_files')

    def __repr__(self):
        return f"<Attachment {self.filename}>"

    @staticmethod
    def get_file_types():
        return [
            'ISC Payment',
            'DO (Delivery Order)',
            'POD (Proof of Delivery)',
            'Inspection Report',
            'Customs Documentation',
            'Bill of Lading',
            'Invoice',
            'Packing List',
            'Certificate of Origin',
            'Other'
        ]

    def get_file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

class Bill(db.Model):
    __tablename__ = "bill"
    id              = db.Column(db.Integer, primary_key=True)
    cargo_id        = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)
    supplier_name   = db.Column(db.String(100), nullable=False)
    category        = db.Column(db.String(50), nullable=False)  # Airline, Trucking, CES, Destruction
    amount          = db.Column(db.Float, nullable=False)
    currency        = db.Column(db.String(10), default='USD')
    payment_status  = db.Column(db.String(20), default='Unpaid')
    due_date        = db.Column(db.DateTime, nullable=True)
    payment_date    = db.Column(db.DateTime, nullable=True)
    invoice_number  = db.Column(db.String(50), nullable=True)
    uploaded_at     = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id  = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes           = db.Column(db.String(200))
    is_archived     = db.Column(db.Boolean, default=False)

    uploaded_by = db.relationship('User', backref='uploaded_bills')

    def __repr__(self):
        return f"<Bill {self.invoice_number} - {self.supplier_name}>"

    @staticmethod
    def get_categories():
        return [
            'Airline',
            'Trucking',
            'CES (Inspection)',
            'Destruction',
            'Customs',
            'Storage',
            'Other'
        ]

class EventLog(db.Model):
    __tablename__ = "event_log"
    id              = db.Column(db.Integer, primary_key=True)
    cargo_id        = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)
    description     = db.Column(db.String(200), nullable=False)
    performed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    performed_by = db.relationship('User', backref='event_logs')

    def __repr__(self):
        return f"<EventLog {self.description} at {self.timestamp}>"

class EmailLog(db.Model):
    __tablename__ = "email_log"
    id            = db.Column(db.Integer, primary_key=True)
    cargo_id      = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)
    template_name = db.Column(db.String(100))
    recipients    = db.Column(db.String(300))
    subject       = db.Column(db.String(200))
    body          = db.Column(db.Text)
    sent_at       = db.Column(db.DateTime, default=datetime.utcnow)
    sent_by_id    = db.Column(db.Integer, db.ForeignKey('user.id'))

    sent_by = db.relationship('User', backref='sent_emails')

    def __repr__(self):
        return f"<EmailLog {self.subject} to {self.recipients}>"

class ExternalContact(db.Model):
    __tablename__ = "external_contact"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    company         = db.Column(db.String(100), nullable=False)
    contact_type    = db.Column(db.String(50), nullable=False)  # Airline, Trucking, CES, Customs, Destruction
    email           = db.Column(db.String(120))
    phone           = db.Column(db.String(20))
    address         = db.Column(db.Text)
    default_template = db.Column(db.String(100))  # Default email template for this contact
    notes           = db.Column(db.Text)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExternalContact {self.name} - {self.company}>"

class EmailTemplate(db.Model):
    __tablename__ = "email_template"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    subject     = db.Column(db.String(200), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    variables   = db.Column(db.Text)  # JSON string of available variables
    category    = db.Column(db.String(50))  # Truck Dispatch, Inspection Notice, etc.
    is_active   = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.relationship('User', backref='created_templates')

    def __repr__(self):
        return f"<EmailTemplate {self.name}>"

    def get_variables(self):
        """Return list of available variables"""
        if self.variables:
            try:
                return json.loads(self.variables)
            except:
                return []
        return []

    def render_template(self, **kwargs):
        """Render template with provided variables"""
        body = self.body
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            body = body.replace(placeholder, str(value))
        return body

class StatusMilestone(db.Model):
    __tablename__ = "status_milestone"
    id            = db.Column(db.Integer, primary_key=True)
    cargo_id      = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)
    milestone_type = db.Column(db.String(50), nullable=False)  # PRE-ALERT, Payment, Inspection, DO received, POD signed, etc.
    timestamp     = db.Column(db.DateTime, default=datetime.utcnow)
    notes         = db.Column(db.String(200))
    completed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    completed_by = db.relationship('User', backref='completed_milestones')

    def __repr__(self):
        return f"<StatusMilestone {self.milestone_type} at {self.timestamp}>" 