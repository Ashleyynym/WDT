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

## 🗄️ Database Configuration

### Option A: Google Cloud SQL (Recommended - Production)

**Perfect for teams who want:**
- ✅ **Professional managed database** with automatic backups
- ✅ **Real-time collaboration** - multiple users can access simultaneously
- ✅ **Scalable infrastructure** - easy to upgrade as you grow
- ✅ **High availability** - 99.95% uptime SLA
- ✅ **Built-in security** - encryption, IAM, and network controls

**Setup:**
1. **Follow [GOOGLE_CLOUD_SQL_SETUP.md](GOOGLE_CLOUD_SQL_SETUP.md)** for detailed setup instructions
2. **Create Google Cloud SQL instance** (MySQL 8.0 recommended)
3. **Configure environment variables** in `.env`:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@IP_ADDRESS:3306/wdt_supplychain
   ```
4. **Run migrations**: `flask db upgrade`

**Benefits:**
- **No database conflicts** - Multiple users can work simultaneously
- **Automatic backups** - Google handles data protection
- **Professional monitoring** - Built-in logging and alerts
- **Cost-effective** - Pay only for what you use (~$8-25/month)

### Option B: Local SQLite (Development)

**For development and testing:**
```env
DATABASE_URL=sqlite:///wdt_supplychain.db
```

**Limitations:**
- ⚠️ **Single user only** - Database locks prevent concurrent access
- ⚠️ **No automatic backups** - Manual backup required
- ⚠️ **Limited scalability** - Not suitable for production

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

## 🚀 Deployment Options

### Google Cloud Run (Recommended)
```bash
# Deploy to Cloud Run
gcloud run deploy wdt-supplychain \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Google Compute Engine
```bash
# Deploy to GCE
gcloud compute instances create wdt-app \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=debian-11 \
  --image-project=debian-cloud
```

### App Engine
```yaml
# app.yaml
runtime: python39
env_variables:
  DATABASE_URL: "mysql+pymysql://..."
```

## System Requirements

- Python 3.8+
- Flask 2.3.3+
- MySQL 8.0+ (for production) or SQLite (for development)

## User Roles

- **Admin**: Full system access
- **US Operations Staff**: Cargo and document management
- **Domestic Operations Staff**: Similar to US Ops
- **Warehouse Staff**: Limited cargo access with DO/POD signing
- **External Partners**: Record-only access for specific functions

