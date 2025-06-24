from app import app
from models_new import db, Role
import json

ROLE_PERMISSIONS = {
    'Admin': [
        'manage_users', 'manage_roles', 'manage_templates', 'view_cargo', 'edit_cargo', 'upload_attachments',
        'create_bills', 'send_emails', 'sign_do_pod', 'view_archives', 'archive_records', 'modify_status',
        'log_inspection', 'log_destruction'
    ],
    'US Operations Staff': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails', 'view_archives',
        'archive_records', 'modify_status'
    ],
    'Warehouse Staff': [
        'view_cargo', 'edit_cargo', 'upload_attachments', 'sign_do_pod', 'view_archives'
    ]
}

with app.app_context():
    for role_name, perms in ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(name=role_name).first()
        if role:
            role.permissions = json.dumps(perms)
            print(f"Updated permissions for role: {role_name}")
    db.session.commit()
    print("All role permissions updated.")
