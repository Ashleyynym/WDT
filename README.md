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

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the system at `http://localhost:5000`

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

