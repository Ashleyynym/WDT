# Google Cloud Service Account Setup Guide

This guide will help you set up a Google Cloud Service Account to enable two-way sync between your WDT Supply Chain app and Google Sheets.

## 🚀 Quick Setup (Step-by-Step)

### Step 1: Create Google Cloud Project

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Note your Project ID** (you'll need this later)

### Step 2: Enable Google Sheets API

1. **In Google Cloud Console**, go to **APIs & Services** → **Library**
2. **Search for "Google Sheets API"**
3. **Click on it and press "Enable"**

### Step 3: Create Service Account

1. **Go to APIs & Services** → **Credentials**
2. **Click "Create Credentials"** → **Service Account**
3. **Fill in the details:**
   - **Service account name**: `wdt-sheets-sync`
   - **Service account ID**: `wdt-sheets-sync@your-project-id.iam.gserviceaccount.com`
   - **Description**: `Service account for WDT Supply Chain Google Sheets sync`
4. **Click "Create and Continue"**

### Step 4: Grant Permissions

1. **Role**: Select **"Editor"** (or "Sheets API" if available)
2. **Click "Continue"**
3. **Click "Done"**

### Step 5: Create and Download Key

1. **Click on your service account** (wdt-sheets-sync)
2. **Go to "Keys" tab**
3. **Click "Add Key"** → **"Create new key"**
4. **Choose "JSON"** format
5. **Click "Create"**
6. **Download the JSON file** and save it as `credentials.json` in your project folder

### Step 6: Share Your Google Sheet

1. **Open your Google Sheet**
2. **Click "Share"** (top right)
3. **Add the service account email**: `wdt-sheets-sync@your-project-id.iam.gserviceaccount.com`
4. **Give it "Editor" access**
5. **Click "Send"** (no need to send notification)

### Step 7: Configure Environment Variables

Create or update your `.env` file:

```env
# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEET_ID=your_actual_sheet_id_here
```

**To find your Sheet ID:**
- Open your Google Sheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`
- Copy the ID part

## 🔧 Testing the Setup

### Test 1: Check Credentials
```bash
python google_sheets_sync.py --summary
```

### Test 2: Full Sync
```bash
python google_sheets_sync.py
```

## 📋 Troubleshooting

### Error: "Invalid credentials"
- Make sure `credentials.json` is in your project folder
- Check that the file is not corrupted
- Verify the service account has the correct permissions

### Error: "Access denied"
- Make sure you've shared the Google Sheet with the service account email
- Check that the service account has "Editor" access to the sheet

### Error: "Sheet not found"
- Verify your `GOOGLE_SHEET_ID` is correct
- Make sure the sheet exists and is accessible

## 🔄 Usage

### Manual Sync
```bash
# Sync all data to Google Sheets
python google_sheets_sync.py

# Check what will be synced
python google_sheets_sync.py --summary
```

### Automatic Sync
Add to your `.env` file:
```env
SYNC_ON_STARTUP=true
```

### Scheduled Sync
The system already includes a job scheduler that can run sync every 15 minutes.

## 📊 What Gets Synced

- **Roles**: User roles and permissions
- **Users**: System users and their details
- **MAWBs**: Master Air Waybills
- **Cargo**: Cargo shipments and details
- **Bills**: Billing records
- **Email Templates**: Email templates
- **External Contacts**: External partner contacts

## 🔒 Security Notes

- **Keep `credentials.json` secure** - don't commit it to Git
- **Add to `.gitignore`**: `credentials.json`
- **Service account has limited access** - only to your specific sheet
- **You can revoke access anytime** from Google Cloud Console

## 🎯 Benefits

✅ **Real-time collaboration** - Both you and your partner see updates instantly
✅ **No database conflicts** - Single source of truth in Google Sheets
✅ **Free hosting** - No database hosting costs
✅ **Easy backup** - Google Sheets automatically backs up your data
✅ **Version history** - Google Sheets tracks all changes
✅ **Mobile access** - View data on any device

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Google Cloud project settings
3. Ensure the service account has proper permissions
4. Check that your Google Sheet is shared correctly 