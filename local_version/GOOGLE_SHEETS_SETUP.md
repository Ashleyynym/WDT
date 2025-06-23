# Google Sheets Setup Guide for WDT Supply Chain

This guide shows you how to set up Google Sheets as your free, shared data store for the WDT Supply Chain system.

## 🚀 Quick Start

### 1. Create Google Sheets

1. **Go to [Google Sheets](https://sheets.google.com)**
2. **Create a new spreadsheet** named "WDT Supply Chain Data"
3. **Create multiple sheets** (tabs) for each data type:
   - `roles` - User roles and permissions
   - `users` - System users
   - `mawbs` - Master Air Waybills
   - `cargo` - Cargo shipments
   - `bills` - Billing records
   - `email_templates` - Email templates
   - `external_contacts` - External contacts

### 2. Set Up Sheet Structure

#### Roles Sheet
| name | description |
|------|-------------|
| Admin | Full system access |
| US Operations Staff | Cargo and document management |
| Domestic Operations Staff | Similar to US Ops |
| Warehouse Staff | Limited cargo access with DO/POD signing |

#### Users Sheet
| username | email | password_hash | is_active | role_name |
|----------|-------|---------------|-----------|-----------|
| admin | admin@wdt.com | admin123 | True | Admin |
| demo | demo@wdt.com | demo123 | True | US Operations Staff |

#### MAWBs Sheet
| mawb_number | origin | destination | eta | status |
|-------------|--------|-------------|-----|--------|
| 123-45678901 | LAX | JFK | 2024-01-15T10:00:00 | PRE-ALERT |
| 123-45678902 | ORD | LAX | 2024-01-16T14:30:00 | IN_TRANSIT |

#### Cargo Sheet
| main_awb | customer_name | flight_number | eta | lfd | status |
|----------|---------------|---------------|-----|-----|--------|
| 123-45678901 | TechCorp Inc. | AA123 | 2024-01-15T10:00:00 | 2024-01-17T10:00:00 | PRE-ALERT |
| 123-45678902 | Global Logistics Ltd. | UA456 | 2024-01-16T14:30:00 | 2024-01-18T14:30:00 | IN_TRANSIT |

#### Bills Sheet
| id | vendor | bill_type | amount | currency | payment_status | notes | mawb_number |
|----|--------|-----------|--------|----------|----------------|-------|-------------|
| 1 | American Airlines | Airline | 1500.00 | USD | PENDING | Air freight charges | 123-45678901 |
| 2 | Fast Trucking | Trucking | 250.00 | USD | PAID | Delivery to warehouse | 123-45678901 |

#### Email Templates Sheet
| name | subject | body |
|------|---------|------|
| Truck Dispatch | Truck Dispatch for {MAWB} | Dear {Trucking Company}, Please dispatch truck for MAWB {MAWB}... |
| Inspection Notice | Inspection Required for {MAWB} | Dear {Inspection Center}, Inspection required for MAWB {MAWB}... |

#### External Contacts Sheet
| name | contact_type | email | phone | address |
|------|--------------|-------|-------|---------|
| American Airlines | Airline | ops@aa.com | +1-555-0123 | 123 Aviation Blvd |
| Fast Trucking | Trucking | dispatch@fasttruck.com | +1-555-0456 | 456 Logistics Ave |

### 3. Publish Sheets

For each sheet tab:

1. **Click on the sheet tab** (e.g., "roles")
2. **File → Share → Publish to web**
3. **Choose:**
   - **Entire Document** or **Specific sheets**
   - **Format: Comma-separated values (.csv)**
   - **Published content & settings: Automatically republish when changes are made**
4. **Click "Publish"**
5. **Copy the URL** (it will look like: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0`)

### 4. Update Sync Script URLs

Edit `sync_from_sheet.py` and replace the placeholder URLs:

```python
SHEET_URLS = {
    'users': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=0',
    'roles': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=1',
    'mawbs': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=2',
    'cargo': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=3',
    'bills': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=4',
    'email_templates': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=5',
    'external_contacts': 'https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/export?format=csv&gid=6',
}
```

**Note:** The `gid` parameter corresponds to the sheet tab number (0 = first tab, 1 = second tab, etc.)

## 🔄 Using the Sync System

### Manual Sync
```bash
# Sync all data from Google Sheets
python sync_from_sheet.py

# Show sheet structure
python sync_from_sheet.py --show-structure
```

### Automatic Sync on Startup
Add to your `.env` file:
```
SYNC_ON_STARTUP=true
```

### Scheduled Sync
The system can automatically sync every 15 minutes. This is already configured in the workflow engine.

## 📊 Data Flow

```
Google Sheets (Master Data)
         ↓
    CSV Export URLs
         ↓
   sync_from_sheet.py
         ↓
   Local SQLite Database
         ↓
   WDT Supply Chain App
```

## 🔒 Security Considerations

- **Public Access**: Published Google Sheets are publicly readable
- **No Sensitive Data**: Don't put passwords, API keys, or PII in the sheets
- **Password Hashing**: For production, implement proper password hashing
- **Access Control**: Limit who can edit the Google Sheets

## 🛠️ Troubleshooting

### Common Issues

1. **"Error fetching data"**
   - Check if the Google Sheets URL is correct
   - Ensure the sheet is published to web
   - Verify internet connection

2. **"Column not found"**
   - Check that sheet column names match exactly
   - Use the `--show-structure` flag to see expected columns

3. **"Database locked"**
   - Make sure the app is not running
   - Close any database viewers

### Testing the Setup

1. **Add test data** to your Google Sheets
2. **Run sync**: `python sync_from_sheet.py`
3. **Check database**: Use SQLite browser or command line
4. **Start app**: `python app.py`
5. **Verify data** appears in the web interface

## 📈 Scaling Considerations

- **Small Teams**: Perfect for 2-10 users
- **Data Volume**: Best for < 10,000 rows per sheet
- **Update Frequency**: Sync every 15-60 minutes
- **Real-time**: Not real-time, but near real-time with frequent syncs

## 🎯 Benefits

✅ **Free** - No database hosting costs  
✅ **Visible** - Non-technical users can view/edit data  
✅ **Collaborative** - Multiple people can edit simultaneously  
✅ **Backup** - Google automatically backs up your data  
✅ **Version History** - Track changes over time  
✅ **No Binary Files** - Clean Git repository  

## 🚀 Next Steps

1. **Set up your Google Sheets** following this guide
2. **Update the URLs** in `sync_from_sheet.py`
3. **Test the sync** with sample data
4. **Share the Google Sheets** with your team
5. **Set up automatic sync** for seamless updates

---

**Need help?** Check the troubleshooting section or create an issue in the repository. 