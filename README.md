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

**One command to run the application:**
```bash
python run.py
```

That's it! The setup script will:
- ✅ Create virtual environment automatically
- ✅ Install all dependencies
- ✅ Create activation scripts for you
- ✅ Handle all platform differences

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

2. **Using the activation script:**
   ```bash
   # Windows
   activate.bat
   
   # macOS/Linux
   ./activate.sh
   ```

3. **Manual activation:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   # Then run
   python app.py
   ```

4. **Access the system at** `http://localhost:5000`

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

## ⚠️ Important: Do NOT Commit venv

- Never commit your `venv/` folder (or any virtual environment) to Git. Virtual environments are platform-specific and will not work across Windows, macOS, and Linux.
- Always use the provided `python setup.py` script to create a fresh virtual environment and install dependencies on your own machine.
- The setup script will warn you if your venv was created on a different OS, and will prompt you to recreate it if needed.

