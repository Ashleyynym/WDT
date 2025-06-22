"""Backend Schema Implementation

Revision ID: 20240121_backend_schema
Revises: 1320064b6ff0
Create Date: 2024-01-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20240121_backend_schema'
down_revision = '1320064b6ff0'
branch_labels = None
depends_on = None


def upgrade():
    # Create carriers table
    op.create_table('carriers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create file_types table
    op.create_table('file_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False, unique=True),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create features table
    op.create_table('features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False, unique=True),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('permissions', sa.Text(), nullable=True),  # JSON string
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create role_features table
    op.create_table('role_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('feature_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'feature_id')
    )

    # Create user_overrides table
    op.create_table('user_overrides',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feature_id', sa.Integer(), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'feature_id')
    )

    # Create workflow_steps table
    op.create_table('workflow_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('next_step', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mawbs table
    op.create_table('mawbs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mawb_number', sa.String(length=20), nullable=False, unique=True),
        sa.Column('shipper_name', sa.String(length=200), nullable=False),
        sa.Column('shipper_address', sa.Text(), nullable=True),
        sa.Column('consignee_name', sa.String(length=200), nullable=False),
        sa.Column('consignee_address', sa.Text(), nullable=True),
        sa.Column('origin', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=True),
        sa.Column('flight_number', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('eta', sa.DateTime(), nullable=True),
        sa.Column('lfd', sa.DateTime(), nullable=True),
        sa.Column('current_step', sa.String(length=10), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),  # JSON string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create hawbs table
    op.create_table('hawbs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hawb_number', sa.String(length=20), nullable=False, unique=True),
        sa.Column('mawb_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('pieces', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('metadata', sa.Text(), nullable=True),  # JSON string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['mawb_id'], ['mawbs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mawb_events table
    op.create_table('mawb_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mawb_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),  # JSON string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['mawb_id'], ['mawbs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create hawb_events table
    op.create_table('hawb_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hawb_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),  # JSON string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['hawb_id'], ['hawbs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mawb_workflows table
    op.create_table('mawb_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mawb_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),  # JSON string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['mawb_id'], ['mawbs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scheduled_jobs table
    op.create_table('scheduled_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('mawb_id', sa.Integer(), nullable=True),
        sa.Column('hawb_id', sa.Integer(), nullable=True),
        sa.Column('run_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('max_attempts', sa.Integer(), nullable=False, default=3),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['hawb_id'], ['hawbs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mawb_id'], ['mawbs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('table_name', sa.String(length=100), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),  # INSERT, UPDATE, DELETE
        sa.Column('old_values', sa.Text(), nullable=True),  # JSON string
        sa.Column('new_values', sa.Text(), nullable=True),  # JSON string
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['changed_by'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_mawbs_mawb_number', 'mawbs', ['mawb_number'])
    op.create_index('idx_mawbs_status', 'mawbs', ['status'])
    op.create_index('idx_mawbs_eta', 'mawbs', ['eta'])
    op.create_index('idx_mawbs_lfd', 'mawbs', ['lfd'])
    op.create_index('idx_hawbs_hawb_number', 'hawbs', ['hawb_number'])
    op.create_index('idx_hawbs_mawb_id', 'hawbs', ['mawb_id'])
    op.create_index('idx_mawb_events_mawb_id', 'mawb_events', ['mawb_id'])
    op.create_index('idx_mawb_events_event_time', 'mawb_events', ['event_time'])
    op.create_index('idx_mawb_events_event_type', 'mawb_events', ['event_type'])
    op.create_index('idx_hawb_events_hawb_id', 'hawb_events', ['hawb_id'])
    op.create_index('idx_hawb_events_event_time', 'hawb_events', ['event_time'])
    op.create_index('idx_scheduled_jobs_run_at', 'scheduled_jobs', ['run_at'])
    op.create_index('idx_scheduled_jobs_status', 'scheduled_jobs', ['status'])
    op.create_index('idx_scheduled_jobs_mawb_id', 'scheduled_jobs', ['mawb_id'])
    op.create_index('idx_audit_log_table_record', 'audit_log', ['table_name', 'record_id'])
    op.create_index('idx_audit_log_changed_at', 'audit_log', ['changed_at'])

    # Insert default data
    op.execute("""
        INSERT INTO carriers (name, code, is_active) VALUES 
        ('Maersk', 'MAERSK', 1),
        ('CMA CGM', 'CMACGM', 1),
        ('COSCO', 'COSCO', 1),
        ('MSC', 'MSC', 1),
        ('ONE', 'ONE', 1)
    """)

    op.execute("""
        INSERT INTO file_types (key, description) VALUES 
        ('ISC_fee', 'ISC Fee Receipt'),
        ('customs_doc', 'Customs Documentation'),
        ('DO', 'Delivery Order'),
        ('POD', 'Proof of Delivery'),
        ('inspection', 'Inspection Report'),
        ('BOL', 'Bill of Lading'),
        ('invoice', 'Invoice'),
        ('packing_list', 'Packing List'),
        ('certificate', 'Certificate of Origin'),
        ('other', 'Other Document')
    """)

    op.execute("""
        INSERT INTO features (key, description) VALUES 
        ('view_dashboard', 'View Dashboard'),
        ('view_cargo', 'View Cargo Management'),
        ('edit_cargo', 'Edit Cargo'),
        ('delete_cargo', 'Delete Cargo'),
        ('view_bills', 'View Bills'),
        ('edit_bills', 'Edit Bills'),
        ('view_attachments', 'View Attachments'),
        ('upload_attachments', 'Upload Attachments'),
        ('delete_attachments', 'Delete Attachments'),
        ('view_users', 'View Users'),
        ('edit_users', 'Edit Users'),
        ('manage_roles', 'Manage Roles'),
        ('view_reports', 'View Reports'),
        ('export_data', 'Export Data'),
        ('import_data', 'Import Data'),
        ('manage_workflows', 'Manage Workflows'),
        ('view_audit_log', 'View Audit Log')
    """)

    op.execute("""
        INSERT INTO roles (name, description, is_active) VALUES 
        ('Admin', 'Full system access', 1),
        ('US Ops', 'US Operations team', 1),
        ('Warehouse', 'Warehouse staff', 1),
        ('Dispatcher', 'Dispatch team', 1),
        ('Customer', 'Customer access', 1),
        ('Viewer', 'Read-only access', 1)
    """)

    # Insert workflow steps based on SOP
    op.execute("""
        INSERT INTO workflow_steps (code, name, description, next_step, is_active) VALUES 
        ('T01', 'Booking Confirmed', 'Initial booking confirmation received', 'T02', 1),
        ('T02', 'Container Assigned', 'Container number assigned', 'T03', 1),
        ('T03', 'Pickup Scheduled', 'Pickup from shipper scheduled', 'T04', 1),
        ('T04', 'Container Picked Up', 'Container picked up from shipper', 'T05', 1),
        ('T05', 'At Origin Port', 'Container arrived at origin port', 'T06', 1),
        ('T06', 'Loaded on Vessel', 'Container loaded on vessel', 'T07', 1),
        ('T07', 'Vessel Departed', 'Vessel departed origin port', 'T08', 1),
        ('T08', 'In Transit', 'Container in transit', 'T09', 1),
        ('T09', 'Vessel Arrived', 'Vessel arrived at destination port', 'T10', 1),
        ('T10', 'Container Discharged', 'Container discharged from vessel', 'T11', 1),
        ('T11', 'Customs Clearance', 'Customs clearance in progress', 'T12', 1),
        ('T12', 'Customs Cleared', 'Customs clearance completed', 'T13', 1),
        ('T13', 'Delivery Scheduled', 'Delivery to consignee scheduled', 'T14', 1),
        ('T14', 'Delivered', 'Container delivered to consignee', 'T15', 1),
        ('T15', 'Empty Return', 'Empty container returned', 'COMPLETE', 1)
    """)

    # Assign features to roles
    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'Admin'
    """)

    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'US Ops' AND f.key IN (
            'view_dashboard', 'view_cargo', 'edit_cargo', 'view_bills', 
            'edit_bills', 'view_attachments', 'upload_attachments', 
            'view_reports', 'export_data', 'import_data'
        )
    """)

    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'Warehouse' AND f.key IN (
            'view_dashboard', 'view_cargo', 'view_attachments', 
            'upload_attachments', 'view_reports'
        )
    """)

    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'Dispatcher' AND f.key IN (
            'view_dashboard', 'view_cargo', 'edit_cargo', 'view_bills', 
            'view_attachments', 'upload_attachments', 'view_reports'
        )
    """)

    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'Customer' AND f.key IN (
            'view_dashboard', 'view_cargo', 'view_attachments', 'view_reports'
        )
    """)

    op.execute("""
        INSERT INTO role_features (role_id, feature_id) 
        SELECT r.id, f.id FROM roles r, features f 
        WHERE r.name = 'Viewer' AND f.key IN (
            'view_dashboard', 'view_cargo', 'view_bills', 'view_attachments', 'view_reports'
        )
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_audit_log_changed_at', 'audit_log')
    op.drop_index('idx_audit_log_table_record', 'audit_log')
    op.drop_index('idx_scheduled_jobs_mawb_id', 'scheduled_jobs')
    op.drop_index('idx_scheduled_jobs_status', 'scheduled_jobs')
    op.drop_index('idx_scheduled_jobs_run_at', 'scheduled_jobs')
    op.drop_index('idx_hawb_events_event_time', 'hawb_events')
    op.drop_index('idx_hawb_events_hawb_id', 'hawb_events')
    op.drop_index('idx_mawb_events_event_type', 'mawb_events')
    op.drop_index('idx_mawb_events_event_time', 'mawb_events')
    op.drop_index('idx_mawb_events_mawb_id', 'mawb_events')
    op.drop_index('idx_hawbs_mawb_id', 'hawbs')
    op.drop_index('idx_hawbs_hawb_number', 'hawbs')
    op.drop_index('idx_mawbs_lfd', 'mawbs')
    op.drop_index('idx_mawbs_eta', 'mawbs')
    op.drop_index('idx_mawbs_status', 'mawbs')
    op.drop_index('idx_mawbs_mawb_number', 'mawbs')

    # Drop tables
    op.drop_table('audit_log')
    op.drop_table('scheduled_jobs')
    op.drop_table('mawb_workflows')
    op.drop_table('workflow_steps')
    op.drop_table('hawb_events')
    op.drop_table('mawb_events')
    op.drop_table('hawbs')
    op.drop_table('mawbs')
    op.drop_table('user_overrides')
    op.drop_table('role_features')
    op.drop_table('features')
    op.drop_table('file_types')
    op.drop_table('carriers') 