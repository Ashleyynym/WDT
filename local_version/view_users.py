#!/usr/bin/env python3
"""
Script to view all users in the database.
"""

from app import app
from models import User, Role, db
import json

def view_all_users():
    with app.app_context():
        print("=== ALL USERS IN DATABASE ===\n")
        
        users = User.query.all()
        
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role.name if user.role else 'No Role'}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            
            if user.role and user.role.permissions:
                try:
                    permissions = json.loads(user.role.permissions)
                    print(f"Permissions: {permissions}")
                except:
                    print(f"Permissions: {user.role.permissions}")
            else:
                print("Permissions: None")
            
            print("-" * 50)

def view_all_roles():
    with app.app_context():
        print("\n=== ALL ROLES IN DATABASE ===\n")
        
        roles = Role.query.all()
        
        if not roles:
            print("No roles found in database.")
            return
        
        for role in roles:
            print(f"Role ID: {role.id}")
            print(f"Name: {role.name}")
            print(f"Description: {role.description}")
            
            if role.permissions:
                try:
                    permissions = json.loads(role.permissions)
                    print(f"Permissions: {permissions}")
                except:
                    print(f"Permissions: {role.permissions}")
            else:
                print("Permissions: None")
            
            print(f"Users with this role: {len(role.users)}")
            print("-" * 50)

if __name__ == '__main__':
    view_all_users()
    view_all_roles() 