#!/usr/bin/env python3
"""
Script to update all roles in the database to match the new permission matrix.
This ensures all roles have the correct permissions as defined in Appendix D.
"""

from app import app
from models import Role, db, DEFAULT_ROLES
import json

def update_roles_permissions():
    with app.app_context():
        print("=== UPDATING ROLES TO MATCH PERMISSION MATRIX ===\n")
        
        # Get all existing roles
        existing_roles = Role.query.all()
        existing_role_names = [role.name for role in existing_roles]
        
        print(f"Found {len(existing_roles)} existing roles: {existing_role_names}\n")
        
        # Update or create roles based on DEFAULT_ROLES
        for role_name, permissions in DEFAULT_ROLES.items():
            role = Role.query.filter_by(name=role_name).first()
            
            if role:
                # Update existing role
                old_permissions = role.permissions
                role.permissions = json.dumps(permissions)
                db.session.commit()
                print(f"✅ Updated role '{role_name}' with permissions: {permissions}")
                if old_permissions != role.permissions:
                    print(f"   Previous permissions: {old_permissions}")
            else:
                # Create new role
                role = Role(name=role_name, description=f"{role_name} role")
                role.permissions = json.dumps(permissions)
                db.session.add(role)
                db.session.commit()
                print(f"🆕 Created new role '{role_name}' with permissions: {permissions}")
        
        # Check for any roles that exist in database but not in DEFAULT_ROLES
        default_role_names = list(DEFAULT_ROLES.keys())
        orphaned_roles = [role for role in existing_roles if role.name not in default_role_names]
        
        if orphaned_roles:
            print(f"\n⚠️  Found {len(orphaned_roles)} roles not in permission matrix:")
            for role in orphaned_roles:
                print(f"   - {role.name} (ID: {role.id})")
                print(f"     Current permissions: {role.permissions}")
                print(f"     Users with this role: {len(role.users)}")
        
        # Show final state
        print(f"\n=== FINAL ROLE SUMMARY ===")
        all_roles = Role.query.all()
        for role in all_roles:
            permissions = json.loads(role.permissions) if role.permissions else []
            print(f"Role: {role.name}")
            print(f"  Permissions: {permissions}")
            print(f"  Users: {len(role.users)}")
            print()

if __name__ == '__main__':
    update_roles_permissions() 