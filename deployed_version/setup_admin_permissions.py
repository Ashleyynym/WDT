#!/usr/bin/env python3
"""
Script to set up admin permissions for user management.
This ensures the admin user has the 'manage_users' permission.
"""

from app import app
from models import User, Role, db, PERMISSIONS
import json

def setup_admin_permissions():
    with app.app_context():
        # Find or create Admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='System Administrator')
            db.session.add(admin_role)
            db.session.commit()
            print("Created Admin role")
        
        # Set all permissions for Admin role
        all_permissions = list(PERMISSIONS.keys())
        admin_role.permissions = json.dumps(all_permissions)
        db.session.commit()
        print(f"Set Admin role permissions: {all_permissions}")
        
        # Find admin user and assign Admin role if not already assigned
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            if admin_user.role_id != admin_role.id:
                admin_user.role_id = admin_role.id
                db.session.commit()
                print("Assigned Admin role to admin user")
            else:
                print("Admin user already has Admin role")
        else:
            print("No admin user found. Please create an admin user first.")
        
        # Also check for any user with 'Admin' role name
        admin_users = User.query.join(Role).filter(Role.name == 'Admin').all()
        if admin_users:
            print(f"Found {len(admin_users)} user(s) with Admin role:")
            for user in admin_users:
                print(f"  - {user.username} ({user.email})")
        else:
            print("No users found with Admin role")

if __name__ == '__main__':
    setup_admin_permissions() 