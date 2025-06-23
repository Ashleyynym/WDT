#!/usr/bin/env python3
"""
WDT Supply Chain - Google Sheets API Sync Script
Two-way sync between local SQLite database and Google Sheets
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from app import create_app, db
from models_new import User, Role, MAWB, Cargo, Bill, Attachment, EmailTemplate, ExternalContact

# Configuration
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Environment variables (set these in your .env file)
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', 'your_sheet_id_here')

# Sheet tab names
SHEET_TABS = {
    'roles': 'Roles',
    'users': 'Users', 
    'mawbs': 'MAWBs',
    'cargo': 'Cargo',
    'bills': 'Bills',
    'email_templates': 'EmailTemplates',
    'external_contacts': 'ExternalContacts'
}

class GoogleSheetsSync:
    def __init__(self):
        """Initialize Google Sheets connection"""
        try:
            # Authenticate with service account
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_CREDENTIALS_PATH, SCOPE
            )
            self.gc = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.spreadsheet = self.gc.open_by_key(GOOGLE_SHEET_ID)
            print(f"✅ Connected to Google Sheets: {self.spreadsheet.title}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Google Sheets: {e}")
            print("Please check your credentials and sheet ID")
            raise
    
    def get_or_create_worksheet(self, tab_name):
        """Get existing worksheet or create new one"""
        try:
            worksheet = self.spreadsheet.worksheet(tab_name)
            print(f"  📄 Using existing worksheet: {tab_name}")
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=20)
            print(f"  📄 Created new worksheet: {tab_name}")
        return worksheet
    
    def sync_roles_to_sheet(self):
        """Sync roles from database to Google Sheets"""
        print("🔄 Syncing roles...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['roles'])
        
        # Get data from database
        roles = Role.query.all()
        
        # Prepare data
        data = [['name', 'description']]  # Header
        for role in roles:
            data.append([
                role.name,
                role.description or ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(roles)} roles")
    
    def sync_users_to_sheet(self):
        """Sync users from database to Google Sheets"""
        print("🔄 Syncing users...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['users'])
        
        # Get data from database
        users = User.query.all()
        
        # Prepare data
        data = [['username', 'email', 'is_active', 'role_name']]  # Header
        for user in users:
            role_name = user.role.name if user.role else ''
            data.append([
                user.username,
                user.email,
                str(user.is_active),
                role_name
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(users)} users")
    
    def sync_mawbs_to_sheet(self):
        """Sync MAWBs from database to Google Sheets"""
        print("🔄 Syncing MAWBs...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['mawbs'])
        
        # Get data from database
        mawbs = MAWB.query.all()
        
        # Prepare data
        data = [['mawb_number', 'status', 'progress', 'eta', 'lfd']]  # Header
        for mawb in mawbs:
            data.append([
                mawb.mawb_number,
                mawb.status,
                mawb.progress,
                mawb.eta.strftime('%Y-%m-%d') if mawb.eta else '',
                mawb.lfd.strftime('%Y-%m-%d') if mawb.lfd else ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(mawbs)} MAWBs")
    
    def sync_cargo_to_sheet(self):
        """Sync cargo from database to Google Sheets"""
        print("🔄 Syncing cargo...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['cargo'])
        
        # Get data from database
        cargo_list = Cargo.query.all()
        
        # Prepare data
        data = [['main_awb', 'customer_name', 'flight_no', 'eta', 'lfd_date', 'status']]  # Header
        for cargo in cargo_list:
            data.append([
                cargo.main_awb,
                cargo.customer_name or '',
                cargo.flight_no or '',
                cargo.eta.strftime('%Y-%m-%dT%H:%M:%S') if cargo.eta else '',
                cargo.lfd_date.strftime('%Y-%m-%dT%H:%M:%S') if cargo.lfd_date else '',
                cargo.status or ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(cargo_list)} cargo records")
    
    def sync_bills_to_sheet(self):
        """Sync bills from database to Google Sheets"""
        print("🔄 Syncing bills...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['bills'])
        
        # Get data from database
        bills = Bill.query.all()
        
        # Prepare data
        data = [['id', 'supplier_name', 'category', 'amount', 'currency', 'payment_status', 'cargo_id']]  # Header
        for bill in bills:
            data.append([
                str(bill.id),
                bill.supplier_name,
                bill.category,
                str(bill.amount),
                bill.currency,
                bill.payment_status,
                str(bill.cargo_id) if bill.cargo_id else ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(bills)} bills")
    
    def sync_email_templates_to_sheet(self):
        """Sync email templates from database to Google Sheets"""
        print("🔄 Syncing email templates...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['email_templates'])
        
        # Get data from database
        templates = EmailTemplate.query.all()
        
        # Prepare data
        data = [['name', 'subject', 'category']]  # Header
        for template in templates:
            data.append([
                template.name,
                template.subject,
                template.category or ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(templates)} email templates")
    
    def sync_external_contacts_to_sheet(self):
        """Sync external contacts from database to Google Sheets"""
        print("🔄 Syncing external contacts...")
        worksheet = self.get_or_create_worksheet(SHEET_TABS['external_contacts'])
        
        # Get data from database
        contacts = ExternalContact.query.all()
        
        # Prepare data
        data = [['name', 'company', 'contact_type', 'email', 'phone']]  # Header
        for contact in contacts:
            data.append([
                contact.name,
                contact.company or '',
                contact.contact_type,
                contact.email or '',
                contact.phone or ''
            ])
        
        # Clear and update worksheet
        worksheet.clear()
        worksheet.update(data)
        print(f"  ✅ Synced {len(contacts)} external contacts")
    
    def sync_all_to_sheets(self):
        """Sync all data from database to Google Sheets"""
        print("🚀 Starting full sync to Google Sheets...")
        print("=" * 60)
        
        try:
            self.sync_roles_to_sheet()
            self.sync_users_to_sheet()
            self.sync_mawbs_to_sheet()
            self.sync_cargo_to_sheet()
            self.sync_bills_to_sheet()
            self.sync_email_templates_to_sheet()
            self.sync_external_contacts_to_sheet()
            
            print("=" * 60)
            print("✅ Full sync completed successfully!")
            print(f"📊 Updated Google Sheets: {self.spreadsheet.title}")
            print(f"🔗 Sheet URL: {self.spreadsheet.url}")
            
        except Exception as e:
            print(f"❌ Error during sync: {e}")
            raise
    
    def get_sync_summary(self):
        """Get summary of data to be synced"""
        print("📊 Sync Summary:")
        print("=" * 50)
        
        try:
            print(f"  Roles: {Role.query.count()} records")
            print(f"  Users: {User.query.count()} records")
            print(f"  MAWBs: {MAWB.query.count()} records")
            print(f"  Cargo: {Cargo.query.count()} records")
            print(f"  Bills: {Bill.query.count()} records")
            print(f"  Email Templates: {EmailTemplate.query.count()} records")
            print(f"  External Contacts: {ExternalContact.query.count()} records")
        except Exception as e:
            print(f"❌ Error getting summary: {e}")

def main():
    """Main function"""
    import sys
    
    # Check if credentials file exists
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        print(f"❌ Credentials file not found: {GOOGLE_CREDENTIALS_PATH}")
        print("\n📋 Setup Instructions:")
        print("1. Create a Google Cloud Service Account")
        print("2. Download the JSON credentials file")
        print("3. Save it as 'credentials.json' in your project folder")
        print("4. Share your Google Sheet with the service account email")
        print("5. Set GOOGLE_SHEET_ID in your .env file")
        return
    
    # Check if sheet ID is configured
    if GOOGLE_SHEET_ID == 'your_sheet_id_here':
        print("❌ Google Sheet ID not configured")
        print("Please set GOOGLE_SHEET_ID in your .env file")
        return
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        try:
            # Initialize sync
            sync = GoogleSheetsSync()
            
            if len(sys.argv) > 1 and sys.argv[1] == '--summary':
                sync.get_sync_summary()
            else:
                sync.sync_all_to_sheets()
                
        except Exception as e:
            print(f"❌ Sync failed: {e}")

if __name__ == '__main__':
    main() 