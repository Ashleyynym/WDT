# WDT Supply Chain - Air Cargo Management System

A comprehensive end-to-end air freight operation management system for WDT Supply Chain.

## Features

- **Dashboard**: Real-time cargo tracking with status overview and alerts
- **Cargo Management**: Complete shipment lifecycle management
- **Document Management**: Centralized file storage and organization
- **Billing System**: Cost tracking and payment management
- **Email Center**: Automated communication with templates
- **User Management**: Role-based access control
- **Multi-timezone Support**: Global operation capabilities

## Quick Start

### 🚀 Super Easy Setup (Recommended)

**One command setup - no manual copying needed!**
```bash
python setup.py
```

**Multiple ways to run with automatic activation:**

#### Option 1: Python Launcher (Cross-Platform)
```bash
python run.py
```

#### Option 2: One-Click Files
- **Windows**: Double-click `start.bat`
- **macOS/Linux**: Double-click `start.sh` or run `./start.sh`

#### Option 3: Command Line (Cross-Platform)
```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

**All methods automatically:**
- ✅ **Activate virtual environment**
- ✅ **Check and install dependencies**
- ✅ **Start the Flask application**
- ✅ **Open at http://localhost:5000**

## 🔄 Data Synchronization Options

### Option A: Google Sheets Sync (Recommended - Free & Collaborative)

**Perfect for teams who want:**
- ✅ **Free data sharing** (no database hosting costs)
- ✅ **Non-technical users** can edit data directly
- ✅ **Real-time collaboration** on data
- ✅ **Clean Git repository** (no binary files)

**Setup:**
1. **Create Google Sheets** following [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)
2. **Update URLs** in `sync_from_sheet.py`
3. **Sync data**: `python sync_from_sheet.py`

**Usage:**
- **Manual sync**: `python sync_from_sheet.py`
- **Auto sync on startup**: Set `SYNC_ON_STARTUP=true` in `.env`
- **Scheduled sync**: Every 15 minutes (already configured)

### Option B: Git Database Sharing (Current Setup)

**For teams who prefer:**
- ✅ **Simple setup** (database included in Git)
- ✅ **Offline access** (no internet required)
- ✅ **Version control** for database changes

**For Team Members:**
- The database (`wdt_supplychain.db`) is included in the repository
- **To get the latest database:** `git pull` will update both code and database
- **To share your changes:** `git add . && git commit -m "message" && git push`

**Database Updates:**
- When you add cargo, upload files, or make changes, commit them to share
- Your partner can pull the latest database with: `git pull origin main`
- The database includes all cargo records, attachments, billing, and user data

**Important Notes:**
- ⚠️ **Don't run the app simultaneously** - only one person should use it at a time
- 🔄 **Always pull before starting work** to get the latest data
- 💾 **Commit your changes regularly** to keep the database synchronized

### 🔧 Alternative Setup Options

#### Option 1: Standard Virtual Environment

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   
   **On Windows:**
   ```cmd
   venv\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

#### Option 2: One-Command Setup (Cross-Platform)

If you have `conda` installed:
```bash
conda create -n wdt-env python=3.9
conda activate wdt-env
pip install -r requirements.txt
```

#### Option 3: Using pipenv (Cross-Platform)

```bash
pip install pipenv
pipenv install
pipenv shell
```

### 🎯 Running the Application

**After setup, you have multiple ways to run the app:**

1. **One-click launcher (easiest):**
   ```bash
   python run.py
   ```

2. **One-click files:**
   - **Windows**: Double-click `start.bat`
   - **macOS/Linux**: Double-click `start.sh` or run `./start.sh`

3. **Using the activation script:**
   ```bash
   # Windows
   activate.bat
   
   # macOS/Linux
   ./activate.sh
   ```

4. **Manual activation:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   # Then run
   python app.py
   ```

5. **Access the system at** `http://localhost:5000`

## System Requirements

- Python 3.8+
- Flask 2.3.3+
- SQLite database (included)

## User Roles

- **Admin**: Full system access
- **US Operations Staff**: Cargo and document management
- **Domestic Operations Staff**: Similar to US Ops
- **Warehouse Staff**: Limited cargo access with DO/POD signing
- **External Partners**: Record-only access for specific functions

