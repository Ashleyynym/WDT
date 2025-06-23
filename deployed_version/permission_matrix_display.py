#!/usr/bin/env python3
"""
Script to display the current permission matrix in a table format.
This helps verify that the permissions match the specification exactly.
"""

from app import app
from models import Role, db, PERMISSIONS
import json

def display_permission_matrix():
    with app.app_context():
        print("=== CURRENT PERMISSION MATRIX ===\n")
        
        # Get all roles
        roles = Role.query.all()
        
        # Get all permissions
        all_permissions = list(PERMISSIONS.keys())
        
        # Create header
        header = "| Feature                        |"
        separator = "| ------------------------------ |"
        
        for role in roles:
            header += f" {role.name[:15]:<15} |"
            separator += " " + "-" * 15 + " |"
        
        print(header)
        print(separator)
        
        # Create rows for each permission
        for permission in all_permissions:
            row = f"| {PERMISSIONS[permission]:<30} |"
            
            for role in roles:
                role_permissions = json.loads(role.permissions) if role.permissions else []
                if permission in role_permissions:
                    row += " ✅             |"
                else:
                    row += "                |"
            
            print(row)
        
        print("\n=== ROLE SUMMARIES ===")
        for role in roles:
            permissions = json.loads(role.permissions) if role.permissions else []
            print(f"\n{role.name}:")
            print(f"  Users: {len(role.users)}")
            print(f"  Permissions: {permissions}")

if __name__ == '__main__':
    display_permission_matrix() 