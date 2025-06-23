#!/usr/bin/env python3
"""
WDT Supply Chain - Google Sheets Sync Script
Syncs data from published Google Sheets to local SQLite database
"""

import csv
import io
import requests
import os
from datetime import datetime
from app import create_app, db
from models_new import User, Role, MAWB, Cargo, Bill, Attachment, EmailTemplate, ExternalContact

# Google Sheets URLs (you'll need to update these with your actual sheet URLs)
SHEET_URLS = {
    'users': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0',
    'roles': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=1',
    'mawbs': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=2',
    'cargo': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=3',
    'bills': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=4',
    'attachments': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=5',
    'email_templates': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=6',
    'external_contacts': 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=7',
}

def fetch_csv(url):
    """Fetch CSV data from Google Sheets URL"""
    try:
        print(f"Fetching data from: {url}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return csv.DictReader(io.StringIO(resp.text))
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def sync_roles():
    """Sync roles from Google Sheets"""
    print("Syncing roles...")
    reader = fetch_csv(SHEET_URLS['roles'])
    if not reader:
        return
    
    for row in reader:
        role = Role.query.filter_by(name=row['name']).first()
        if not role:
            role = Role()
            role.name = row['name']
            role.description = row.get('description', '')
            db.session.add(role)
            print(f"  Added role: {role.name}")
        else:
            role.description = row.get('description', '')
            print(f"  Updated role: {role.name}")

def sync_users():
    """Sync users from Google Sheets"""
    print("Syncing users...")
    reader = fetch_csv(SHEET_URLS['users'])
    if not reader:
        return
    
    for row in reader:
        user = User.query.filter_by(username=row['username']).first()
        if not user:
            user = User()
            user.username = row['username']
            user.email = row['email']
            user.password_hash = row.get('password_hash', '')  # In production, hash passwords
            user.is_active = row.get('is_active', 'True').lower() == 'true'
            user.created_at = datetime.now()
            
            # Link to role
            if 'role_name' in row:
                role = Role.query.filter_by(name=row['role_name']).first()
                if role:
                    user.role_id = role.id
            
            db.session.add(user)
            print(f"  Added user: {user.username}")
        else:
            user.email = row['email']
            user.is_active = row.get('is_active', 'True').lower() == 'true'
            print(f"  Updated user: {user.username}")

def sync_mawbs():
    """Sync MAWBs from Google Sheets"""
    print("Syncing MAWBs...")
    reader = fetch_csv(SHEET_URLS['mawbs'])
    if not reader:
        return
    
    for row in reader:
        mawb = MAWB.query.filter_by(mawb_number=row['mawb_number']).first()
        if not mawb:
            mawb = MAWB()
            mawb.mawb_number = row['mawb_number']
            mawb.origin = row.get('origin', '')
            mawb.destination = row.get('destination', '')
            mawb.eta = datetime.fromisoformat(row['eta']) if row.get('eta') else None
            mawb.status = row.get('status', 'PRE-ALERT')
            mawb.created_at = datetime.now()
            db.session.add(mawb)
            print(f"  Added MAWB: {mawb.mawb_number}")
        else:
            mawb.origin = row.get('origin', '')
            mawb.destination = row.get('destination', '')
            mawb.eta = datetime.fromisoformat(row['eta']) if row.get('eta') else None
            mawb.status = row.get('status', 'PRE-ALERT')
            print(f"  Updated MAWB: {mawb.mawb_number}")

def sync_cargo():
    """Sync cargo from Google Sheets"""
    print("Syncing cargo...")
    reader = fetch_csv(SHEET_URLS['cargo'])
    if not reader:
        return
    
    for row in reader:
        cargo = Cargo.query.filter_by(main_awb=row['main_awb']).first()
        if not cargo:
            cargo = Cargo()
            cargo.main_awb = row['main_awb']
            cargo.customer_name = row.get('customer_name', '')
            cargo.flight_number = row.get('flight_number', '')
            cargo.eta = datetime.fromisoformat(row['eta']) if row.get('eta') else None
            cargo.lfd = datetime.fromisoformat(row['lfd']) if row.get('lfd') else None
            cargo.status = row.get('status', 'PRE-ALERT')
            cargo.created_at = datetime.now()
            db.session.add(cargo)
            print(f"  Added cargo: {cargo.main_awb}")
        else:
            cargo.customer_name = row.get('customer_name', '')
            cargo.flight_number = row.get('flight_number', '')
            cargo.eta = datetime.fromisoformat(row['eta']) if row.get('eta') else None
            cargo.lfd = datetime.fromisoformat(row['lfd']) if row.get('lfd') else None
            cargo.status = row.get('status', 'PRE-ALERT')
            print(f"  Updated cargo: {cargo.main_awb}")

def sync_bills():
    """Sync bills from Google Sheets"""
    print("Syncing bills...")
    reader = fetch_csv(SHEET_URLS['bills'])
    if not reader:
        return
    
    for row in reader:
        bill = Bill.query.filter_by(id=row['id']).first() if row.get('id') else None
        if not bill:
            bill = Bill()
            bill.vendor = row.get('vendor', '')
            bill.bill_type = row.get('bill_type', '')
            bill.amount = float(row.get('amount', 0))
            bill.currency = row.get('currency', 'USD')
            bill.payment_status = row.get('payment_status', 'PENDING')
            bill.notes = row.get('notes', '')
            bill.created_at = datetime.now()
            
            # Link to MAWB
            if 'mawb_number' in row:
                mawb = MAWB.query.filter_by(mawb_number=row['mawb_number']).first()
                if mawb:
                    bill.mawb_id = mawb.id
            
            db.session.add(bill)
            print(f"  Added bill: {bill.vendor} - {bill.amount}")
        else:
            bill.vendor = row.get('vendor', '')
            bill.bill_type = row.get('bill_type', '')
            bill.amount = float(row.get('amount', 0))
            bill.currency = row.get('currency', 'USD')
            bill.payment_status = row.get('payment_status', 'PENDING')
            bill.notes = row.get('notes', '')
            print(f"  Updated bill: {bill.vendor} - {bill.amount}")

def sync_email_templates():
    """Sync email templates from Google Sheets"""
    print("Syncing email templates...")
    reader = fetch_csv(SHEET_URLS['email_templates'])
    if not reader:
        return
    
    for row in reader:
        template = EmailTemplate.query.filter_by(name=row['name']).first()
        if not template:
            template = EmailTemplate()
            template.name = row['name']
            template.subject = row.get('subject', '')
            template.body = row.get('body', '')
            template.created_at = datetime.now()
            db.session.add(template)
            print(f"  Added template: {template.name}")
        else:
            template.subject = row.get('subject', '')
            template.body = row.get('body', '')
            print(f"  Updated template: {template.name}")

def sync_external_contacts():
    """Sync external contacts from Google Sheets"""
    print("Syncing external contacts...")
    reader = fetch_csv(SHEET_URLS['external_contacts'])
    if not reader:
        return
    
    for row in reader:
        contact = ExternalContact.query.filter_by(name=row['name']).first()
        if not contact:
            contact = ExternalContact()
            contact.name = row['name']
            contact.contact_type = row.get('contact_type', '')
            contact.email = row.get('email', '')
            contact.phone = row.get('phone', '')
            contact.address = row.get('address', '')
            contact.created_at = datetime.now()
            db.session.add(contact)
            print(f"  Added contact: {contact.name}")
        else:
            contact.contact_type = row.get('contact_type', '')
            contact.email = row.get('email', '')
            contact.phone = row.get('phone', '')
            contact.address = row.get('address', '')
            print(f"  Updated contact: {contact.name}")

def sync_all():
    """Sync all data from Google Sheets"""
    print("🔄 Starting Google Sheets sync...")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        try:
            # Sync in order (roles first, then users that reference roles)
            sync_roles()
            sync_users()
            sync_mawbs()
            sync_cargo()
            sync_bills()
            sync_email_templates()
            sync_external_contacts()
            
            # Commit all changes
            db.session.commit()
            print("=" * 50)
            print("✅ Sync completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during sync: {e}")
            raise

def create_sample_sheets():
    """Create sample Google Sheets structure"""
    print("📋 Sample Google Sheets Structure:")
    print("=" * 50)
    
    sheets = {
        'roles': ['name', 'description'],
        'users': ['username', 'email', 'password_hash', 'is_active', 'role_name'],
        'mawbs': ['mawb_number', 'origin', 'destination', 'eta', 'status'],
        'cargo': ['main_awb', 'customer_name', 'flight_number', 'eta', 'lfd', 'status'],
        'bills': ['id', 'vendor', 'bill_type', 'amount', 'currency', 'payment_status', 'notes', 'mawb_number'],
        'email_templates': ['name', 'subject', 'body'],
        'external_contacts': ['name', 'contact_type', 'email', 'phone', 'address']
    }
    
    for sheet_name, columns in sheets.items():
        print(f"\n📊 {sheet_name.upper()} Sheet:")
        print(f"   Columns: {', '.join(columns)}")
        print(f"   URL: {SHEET_URLS[sheet_name]}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--show-structure':
        create_sample_sheets()
    else:
        sync_all() 