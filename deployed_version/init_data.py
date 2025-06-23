#!/usr/bin/env python3
"""
Initial Data Setup Script for WDT Container Tracking Platform
This script populates the database with essential data for the system to function properly.
"""

from app import create_app, db
from models_new import (
    User, Role, Feature, RoleFeature, UserOverride, WorkflowStep, 
    Carrier, FileType, EmailTemplate
)
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

def create_roles():
    """Create default roles with permissions"""
    print("Creating roles...")
    
    # Define features
    features = {
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
        'log_destruction': 'Log destruction records',
        'view_mawb': 'View MAWB details',
        'edit_mawb': 'Edit MAWB information',
        'view_workflow': 'View workflow status',
        'advance_workflow': 'Advance workflow steps',
        'view_audit': 'View audit logs',
        'schedule_jobs': 'Schedule background jobs'
    }
    
    # Create features
    for key, description in features.items():
        feature = Feature.query.filter_by(key=key).first()
        if not feature:
            feature = Feature(key=key, description=description)
            db.session.add(feature)
            print(f"  Created feature: {key}")
    
    # Define roles with permissions
    roles_data = {
        'Admin': [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills',
            'send_emails', 'view_archives', 'archive_records', 'modify_status',
            'manage_users', 'manage_templates', 'manage_roles', 'view_mawb',
            'edit_mawb', 'view_workflow', 'advance_workflow', 'view_audit',
            'schedule_jobs'
        ],
        'US Operations Staff': [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills',
            'send_emails', 'view_archives', 'archive_records', 'modify_status',
            'view_mawb', 'edit_mawb', 'view_workflow', 'advance_workflow'
        ],
        'Domestic Operations Staff': [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills',
            'send_emails', 'view_archives', 'archive_records', 'modify_status',
            'view_mawb', 'edit_mawb', 'view_workflow', 'advance_workflow'
        ],
        'Warehouse Staff': [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'sign_do_pod',
            'view_archives', 'view_mawb', 'view_workflow'
        ],
        'Customs Brokers': [
            'view_cargo', 'view_archives', 'archive_records', 'view_mawb',
            'view_workflow'
        ],
        'Airline Representatives': [
            'view_cargo', 'view_archives', 'archive_records', 'view_mawb',
            'view_workflow'
        ],
        'Inspection Centers (CES)': [
            'view_cargo', 'view_archives', 'archive_records', 'log_inspection',
            'view_mawb', 'view_workflow'
        ],
        'Destruction Companies': [
            'view_cargo', 'view_archives', 'archive_records', 'log_destruction',
            'view_mawb', 'view_workflow'
        ]
    }
    
    # Create roles and assign features
    for role_name, permissions in roles_data.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(
                name=role_name,
                description=f"Default {role_name} role",
                permissions=json.dumps(permissions)
            )
            db.session.add(role)
            print(f"  Created role: {role_name}")
        
        # Assign features to role
        for perm in permissions:
            feature = Feature.query.filter_by(key=perm).first()
            if feature:
                # Check if role-feature relationship already exists
                existing = RoleFeature.query.filter_by(
                    role_id=role.id, feature_id=feature.id
                ).first()
                if not existing:
                    role_feature = RoleFeature(role_id=role.id, feature_id=feature.id)
                    db.session.add(role_feature)
    
    db.session.commit()
    print("Roles created successfully!")

def create_users():
    """Create default users"""
    print("Creating users...")
    
    # Get admin role
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        print("Error: Admin role not found. Please run create_roles() first.")
        return
    
    # Create admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@wdt.com',
            password_hash=generate_password_hash('admin123'),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin_user)
        print("  Created admin user: admin/admin123")
    
    # Create demo user
    demo_user = User.query.filter_by(username='demo').first()
    if not demo_user:
        demo_user = User(
            username='demo',
            email='demo@wdt.com',
            password_hash=generate_password_hash('demo123'),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(demo_user)
        print("  Created demo user: demo/demo123")
    
    db.session.commit()
    print("Users created successfully!")

def create_workflow_steps():
    """Create default workflow steps for MAWB processing"""
    print("Creating workflow steps...")
    
    workflow_steps = [
        {
            'code': 'T01',
            'name': 'MAWB Created',
            'description': 'Master Airway Bill has been created and entered into the system',
            'next_step': 'T02'
        },
        {
            'code': 'T02',
            'name': 'Documentation Received',
            'description': 'All required documentation has been received and verified',
            'next_step': 'T03'
        },
        {
            'code': 'T03',
            'name': 'Pickup Scheduled',
            'description': 'Pickup from shipper has been scheduled',
            'next_step': 'T04'
        },
        {
            'code': 'T04',
            'name': 'Picked Up',
            'description': 'Cargo has been picked up from shipper',
            'next_step': 'T05'
        },
        {
            'code': 'T05',
            'name': 'At Origin Port',
            'description': 'Cargo has arrived at origin port',
            'next_step': 'T06'
        },
        {
            'code': 'T06',
            'name': 'Loaded on Vessel',
            'description': 'Cargo has been loaded onto the vessel',
            'next_step': 'T07'
        },
        {
            'code': 'T07',
            'name': 'In Transit',
            'description': 'Vessel is in transit to destination',
            'next_step': 'T08'
        },
        {
            'code': 'T08',
            'name': 'Arrived at Destination',
            'description': 'Vessel has arrived at destination port',
            'next_step': 'T09'
        },
        {
            'code': 'T09',
            'name': 'Unloaded',
            'description': 'Cargo has been unloaded from vessel',
            'next_step': 'T10'
        },
        {
            'code': 'T10',
            'name': 'Customs Hold',
            'description': 'Cargo is being held for customs inspection',
            'next_step': 'T11'
        },
        {
            'code': 'T11',
            'name': 'Customs Clearance',
            'description': 'Cargo has cleared customs',
            'next_step': 'T12'
        },
        {
            'code': 'T12',
            'name': 'ISC Payment Required',
            'description': 'Import Service Charge payment is required',
            'next_step': 'T13'
        },
        {
            'code': 'T13',
            'name': 'Ready for Delivery',
            'description': 'Cargo is ready for final delivery',
            'next_step': 'T14'
        },
        {
            'code': 'T14',
            'name': 'Delivered',
            'description': 'Cargo has been delivered to consignee',
            'next_step': 'COMPLETE'
        },
        {
            'code': 'COMPLETE',
            'name': 'Workflow Complete',
            'description': 'MAWB workflow has been completed',
            'next_step': None
        }
    ]
    
    for step_data in workflow_steps:
        step = WorkflowStep.query.filter_by(code=step_data['code']).first()
        if not step:
            step = WorkflowStep(**step_data)
            db.session.add(step)
            print(f"  Created workflow step: {step_data['code']} - {step_data['name']}")
    
    db.session.commit()
    print("Workflow steps created successfully!")

def create_carriers():
    """Create default carriers"""
    print("Creating carriers...")
    
    carriers = [
        {
            'name': 'FedEx Express',
            'code': 'FX',
            'api_endpoint': 'https://api.fedex.com/track',
            'is_active': True
        },
        {
            'name': 'UPS Airlines',
            'code': '5X',
            'api_endpoint': 'https://api.ups.com/track',
            'is_active': True
        },
        {
            'name': 'DHL Express',
            'code': 'DH',
            'api_endpoint': 'https://api.dhl.com/track',
            'is_active': True
        },
        {
            'name': 'American Airlines Cargo',
            'code': 'AA',
            'api_endpoint': 'https://api.aa.com/cargo',
            'is_active': True
        },
        {
            'name': 'Delta Cargo',
            'code': 'DL',
            'api_endpoint': 'https://api.delta.com/cargo',
            'is_active': True
        },
        {
            'name': 'United Cargo',
            'code': 'UA',
            'api_endpoint': 'https://api.united.com/cargo',
            'is_active': True
        }
    ]
    
    for carrier_data in carriers:
        carrier = Carrier.query.filter_by(code=carrier_data['code']).first()
        if not carrier:
            carrier = Carrier(**carrier_data)
            db.session.add(carrier)
            print(f"  Created carrier: {carrier_data['name']} ({carrier_data['code']})")
    
    db.session.commit()
    print("Carriers created successfully!")

def create_file_types():
    """Create default file types"""
    print("Creating file types...")
    
    file_types = [
        {'key': 'isc_payment', 'description': 'ISC Payment Receipt'},
        {'key': 'delivery_order', 'description': 'Delivery Order (DO)'},
        {'key': 'proof_of_delivery', 'description': 'Proof of Delivery (POD)'},
        {'key': 'inspection_report', 'description': 'Inspection Report'},
        {'key': 'customs_document', 'description': 'Customs Documentation'},
        {'key': 'bill_of_lading', 'description': 'Bill of Lading'},
        {'key': 'invoice', 'description': 'Invoice'},
        {'key': 'packing_list', 'description': 'Packing List'},
        {'key': 'certificate_of_origin', 'description': 'Certificate of Origin'},
        {'key': 'airway_bill', 'description': 'Airway Bill'},
        {'key': 'destruction_certificate', 'description': 'Destruction Certificate'},
        {'key': 'other', 'description': 'Other Document'}
    ]
    
    for file_type_data in file_types:
        file_type = FileType.query.filter_by(key=file_type_data['key']).first()
        if not file_type:
            file_type = FileType(**file_type_data)
            db.session.add(file_type)
            print(f"  Created file type: {file_type_data['description']}")
    
    db.session.commit()
    print("File types created successfully!")

def create_email_templates():
    """Create default email templates"""
    print("Creating email templates...")
    
    templates = [
        {
            'name': 'Pickup Reminder',
            'subject': 'Pickup Reminder - MAWB {{mawb_number}}',
            'body': '''Dear {{shipper_name}},

This is a reminder that pickup for MAWB {{mawb_number}} is scheduled for {{pickup_date}}.

Please ensure all documentation is ready and cargo is properly packaged.

Best regards,
WDT Operations Team''',
            'variables': json.dumps(['mawb_number', 'shipper_name', 'pickup_date']),
            'category': 'Pickup'
        },
        {
            'name': 'LFD Reminder',
            'subject': 'LFD Reminder - MAWB {{mawb_number}}',
            'body': '''Dear {{consignee_name}},

This is a reminder that the Last Free Day (LFD) for MAWB {{mawb_number}} is {{lfd_date}}.

Please ensure all necessary arrangements are made to avoid storage charges.

Best regards,
WDT Operations Team''',
            'variables': json.dumps(['mawb_number', 'consignee_name', 'lfd_date']),
            'category': 'LFD'
        },
        {
            'name': 'ISC Payment Reminder',
            'subject': 'ISC Payment Required - MAWB {{mawb_number}}',
            'body': '''Dear {{consignee_name}},

ISC payment is required for MAWB {{mawb_number}}.

Amount: {{isc_amount}}
Due Date: {{due_date}}

Please process payment to avoid delays in delivery.

Best regards,
WDT Operations Team''',
            'variables': json.dumps(['mawb_number', 'consignee_name', 'isc_amount', 'due_date']),
            'category': 'Payment'
        },
        {
            'name': 'Delivery Notification',
            'subject': 'Delivery Scheduled - MAWB {{mawb_number}}',
            'body': '''Dear {{consignee_name}},

Delivery for MAWB {{mawb_number}} has been scheduled for {{delivery_date}}.

Please ensure someone is available to receive the cargo and sign the delivery documents.

Best regards,
WDT Operations Team''',
            'variables': json.dumps(['mawb_number', 'consignee_name', 'delivery_date']),
            'category': 'Delivery'
        }
    ]
    
    # Get admin user for created_by
    admin_user = User.query.filter_by(username='admin').first()
    created_by_id = admin_user.id if admin_user else 1
    
    for template_data in templates:
        template = EmailTemplate.query.filter_by(name=template_data['name']).first()
        if not template:
            template_data['created_by_id'] = created_by_id
            template = EmailTemplate(**template_data)
            db.session.add(template)
            print(f"  Created email template: {template_data['name']}")
    
    db.session.commit()
    print("Email templates created successfully!")

def main():
    """Main function to run all initialization"""
    app = create_app()
    
    with app.app_context():
        print("Starting database initialization...")
        print("=" * 50)
        
        try:
            create_roles()
            print()
            create_users()
            print()
            create_workflow_steps()
            print()
            create_carriers()
            print()
            create_file_types()
            print()
            create_email_templates()
            print()
            
            print("=" * 50)
            print("Database initialization completed successfully!")
            print("\nDefault login credentials:")
            print("  Username: admin, Password: admin123")
            print("  Username: demo, Password: demo123")
            print("\nYou can now start the application with: python app.py")
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main() 