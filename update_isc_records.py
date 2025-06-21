#!/usr/bin/env python3
"""
Script to update existing database records from Chinese "ISC付款" to English "ISC Payment"
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Attachment

def update_isc_records():
    """Update any existing 'ISC付款' records to 'ISC Payment'"""
    with app.app_context():
        # Find all attachments with Chinese "ISC付款"
        attachments = Attachment.query.filter_by(file_type='ISC付款').all()
        
        if attachments:
            print(f"Found {len(attachments)} attachments with 'ISC付款'")
            
            for attachment in attachments:
                print(f"Updating attachment {attachment.id}: {attachment.original_filename}")
                attachment.file_type = 'ISC Payment'
            
            # Commit the changes
            db.session.commit()
            print(f"Successfully updated {len(attachments)} records")
        else:
            print("No records found with 'ISC付款'")
        
        # Also check for any other Chinese text that might need updating
        all_attachments = Attachment.query.all()
        chinese_types = []
        
        for attachment in all_attachments:
            if attachment.file_type and any('\u4e00' <= char <= '\u9fff' for char in attachment.file_type):
                chinese_types.append(attachment.file_type)
        
        if chinese_types:
            print(f"Found attachments with Chinese file types: {set(chinese_types)}")
        else:
            print("No Chinese file types found in database")

if __name__ == "__main__":
    update_isc_records() 