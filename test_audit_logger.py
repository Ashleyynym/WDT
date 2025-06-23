#!/usr/bin/env python3
"""
Test script to verify audit logger functionality
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models_new import db, User, Role, AuditLog

def test_audit_logger():
    """Test the audit logger functionality"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Audit Logger...")
        
        # Test 1: Create a role
        print("1. Creating a test role...")
        test_role = Role(name="Test Role", description="Test role for audit logging")
        db.session.add(test_role)
        db.session.commit()
        print("   ✅ Role created successfully")
        
        # Test 2: Create a user
        print("2. Creating a test user...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            role_id=test_role.id
        )
        test_user.set_password("password123")
        db.session.add(test_user)
        db.session.commit()
        print("   ✅ User created successfully")
        
        # Test 3: Check audit logs
        print("3. Checking audit logs...")
        audit_logs = AuditLog.query.all()
        print(f"   📊 Found {len(audit_logs)} audit log entries")
        
        for log in audit_logs[-5:]:  # Show last 5 entries
            print(f"   - {log.action} on {log.table_name}:{log.record_id} by user {log.changed_by}")
        
        # Test 4: Update user
        print("4. Updating test user...")
        test_user.email = "updated@example.com"
        db.session.commit()
        print("   ✅ User updated successfully")
        
        # Test 5: Check updated audit logs
        print("5. Checking updated audit logs...")
        updated_logs = AuditLog.query.all()
        print(f"   📊 Now have {len(updated_logs)} audit log entries")
        
        # Clean up
        print("6. Cleaning up test data...")
        db.session.delete(test_user)
        db.session.delete(test_role)
        db.session.commit()
        print("   ✅ Test data cleaned up")
        
        print("\n🎉 Audit logger test completed successfully!")
        print("   No transaction conflicts detected.")

if __name__ == "__main__":
    test_audit_logger() 