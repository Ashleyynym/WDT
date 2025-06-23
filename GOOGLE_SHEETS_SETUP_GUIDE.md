# Google Sheets Setup Guide for WDT Supply Chain

## 🚀 Quick Setup Instructions

### Step 1: Set Up Your Google Sheet

1. **Go to your Google Sheet**: [WDT Supply Chain Data](https://docs.google.com/spreadsheets/d/e/2PACX-1vRDvTYjmphSWhboVSZ0f0etf4h4O-8jxUFjfcd6GsarXZGAtZSCr_YD0r8e0JWfAJxBLtpuO4sTDzU1/pub?output=csv)

2. **Add Data to Your Sheet**:
   - Currently your sheet appears to be empty
   - Add the following data structure to get started

### Step 2: Add Sample Data

#### Sheet 1: Roles
| name | description |
|------|-------------|
| Admin | Full system access |
| US Operations Staff | Cargo and document management |
| Domestic Operations Staff | Similar to US Ops |
| Warehouse Staff | Limited cargo access with DO/POD signing |

#### Sheet 2: Users
| username | email | password_hash | is_active | role_name |
|----------|-------|---------------|-----------|-----------|
| admin | admin@wdt.com | admin123 | True | Admin |
| demo | demo@wdt.com | demo123 | True | US Operations Staff |

#### Sheet 3: MAWBs
| mawb_number | origin_port | dest_port | eta | status |
|-------------|-------------|-----------|-----|--------|
| 123-45678901 | LAX | JFK | 2024-01-15 | in_progress |
| 123-45678902 | ORD | LAX | 2024-01-16 | in_progress |

#### Sheet 4: Cargo
| main_awb | customer_name | flight_no | eta | lfd_date | status |
|----------|---------------|-----------|-----|----------|--------|
| 123-45678901 | TechCorp Inc. | AA123 | 2024-01-15T10:00:00 | 2024-01-17T10:00:00 | PRE-ALERT |
| 123-45678902 | Global Logistics Ltd. | UA456 | 2024-01-16T14:30:00 | 2024-01-18T14:30:00 | IN_TRANSIT |

#### Sheet 5: Bills
| id | supplier_name | category | amount | currency | payment_status | cargo_id |
|----|---------------|----------|--------|----------|----------------|----------|
| 1 | American Airlines | Airline | 1500.00 | USD | Unpaid | 1 |
| 2 | Fast Trucking | Trucking | 250.00 | USD | Paid | 1 |

#### Sheet 6: Email Templates
| name | subject | body |
|------|---------|------|
| Truck Dispatch | Truck Dispatch for {MAWB} | Dear {Trucking Company}, Please dispatch truck for MAWB {MAWB}... |
| Inspection Notice | Inspection Required for {MAWB} | Dear {Inspection Center}, Inspection required for MAWB {MAWB}... |

#### Sheet 7: External Contacts
| name | company | contact_type | email | phone | address |
|------|---------|--------------|-------|-------|---------|
| American Airlines | American Airlines | Airline | ops@aa.com | +1-555-0123 | 123 Aviation Blvd |
| Fast Trucking | Fast Trucking Co | Trucking | dispatch@fasttruck.com | +1-555-0456 | 456 Logistics Ave |

### Step 3: Publish Your Sheets

For each sheet tab:

1. **Click on the sheet tab** (e.g., "Roles")
2. **File → Share → Publish to web**
3. **Choose:**
   - **Entire Document** or **Specific sheets**
   - **Format: Comma-separated values (.csv)**
   - **Published content & settings: Automatically republish when changes are made**
4. **Click "Publish"**
5. **Copy the URL** for each sheet

### Step 4: Update Sync Script URLs

Once you have the URLs for each sheet, update `sync_from_sheet.py`:

```python
SHEET_URLS = {
    'users': 'YOUR_USERS_SHEET_URL',
    'roles': 'YOUR_ROLES_SHEET_URL',
    'mawbs': 'YOUR_MAWBS_SHEET_URL',
    'cargo': 'YOUR_CARGO_SHEET_URL',
    'bills': 'YOUR_BILLS_SHEET_URL',
    'email_templates': 'YOUR_EMAIL_TEMPLATES_SHEET_URL',
    'external_contacts': 'YOUR_EXTERNAL_CONTACTS_SHEET_URL',
}
```

### Step 5: Test the Sync

```bash
# Test the structure
python sync_from_sheet.py --show-structure

# Run the sync
python sync_from_sheet.py
```

## 🔧 Troubleshooting

### If the sheet is empty:
1. **Add some data** to your Google Sheet first
2. **Make sure you've published** the sheet to web
3. **Check the URL format** - it should end with `?output=csv`

### If sync fails:
1. **Check the column names** match exactly
2. **Verify the sheet is published** and accessible
3. **Test the URL** in a browser to see the CSV output

## 📊 Current Status

Your Google Sheet URL: `https://docs.google.com/spreadsheets/d/e/2PACX-1vRDvTYjmphSWhboVSZ0f0etf4h4O-8jxUFjfcd6GsarXZGAtZSCr_YD0r8e0JWfAJxBLtpuO4sTDzU1/pub?output=csv`

**Status**: Empty (0 characters returned)

**Next Steps**:
1. Add the sample data above to your sheet
2. Publish each sheet tab
3. Update the URLs in the sync script
4. Test the sync functionality

## 🎯 Benefits of This Approach

✅ **Free** - No database hosting costs  
✅ **Collaborative** - Multiple people can edit simultaneously  
✅ **Visible** - Non-technical users can view/edit data  
✅ **Real-time** - Changes sync automatically  
✅ **No binary files** - Clean Git repository  

---

**Need help?** Add some data to your sheet and let me know when you're ready to test the sync! 