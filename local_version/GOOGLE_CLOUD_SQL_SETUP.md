# Google Cloud SQL Setup Guide for WDT Supply Chain

This guide will help you set up Google Cloud SQL as your production database for the WDT Supply Chain system.

## 🚀 Quick Setup (Step-by-Step)

### Step 1: Create Google Cloud SQL Instance

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Navigate to SQL** in the left sidebar
3. **Click "Create Instance"**
4. **Choose MySQL** (recommended for Flask-SQLAlchemy)
5. **Configure your instance:**

#### Basic Settings:
- **Instance ID**: `wdt-supplychain-db`
- **Password**: Create a strong password (save it!)
- **Database version**: MySQL 8.0 (latest)

#### Machine Configuration:
- **Machine type**: `db-f1-micro` (for development) or `db-n1-standard-1` (for production)
- **Storage**: 10 GB (minimum)
- **Storage type**: SSD

#### Connectivity:
- **Public IP**: ✅ Enable
- **Private IP**: Optional (for VPC)
- **Authorized networks**: Add your IP address

### Step 2: Create Database

1. **Go to your SQL instance**
2. **Click "Databases" tab**
3. **Click "Create Database"**
4. **Database name**: `wdt_supplychain`
5. **Click "Create"**

### Step 3: Create User (Optional)

1. **Go to "Users" tab**
2. **Click "Add User Account"**
3. **Username**: `wdt_app_user`
4. **Password**: Create a strong password
5. **Host**: `%` (allows connections from anywhere)
6. **Click "Add"**

### Step 4: Get Connection Information

1. **Go to "Overview" tab**
2. **Note the connection details:**
   - **Public IP address**
   - **Instance connection name**
   - **Database name**: `wdt_supplychain`

### Step 5: Configure Environment Variables

Create or update your `.env` file:

```env
# Google Cloud SQL Configuration
DATABASE_URL=mysql+pymysql://username:password@IP_ADDRESS:3306/wdt_supplychain

# Example:
# DATABASE_URL=mysql+pymysql://root:your_password@34.123.45.67:3306/wdt_supplychain

# Database Pool Settings (Optional)
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=20
DB_POOL_RECYCLE=300
DB_MAX_OVERFLOW=20

# Other Settings
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### Step 6: Install Dependencies

```bash
pip install PyMySQL cryptography
```

### Step 7: Initialize Database

```bash
# Create tables
flask db upgrade

# Initialize with sample data (optional)
python init_data.py
```

## 🔧 Testing the Connection

### Test 1: Check Connection
```bash
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✅ Database connection successful!')
    except Exception as e:
        print(f'❌ Connection failed: {e}')
"
```

### Test 2: Run Migrations
```bash
flask db upgrade
```

### Test 3: Start Application
```bash
python app.py
```

## 📋 Environment Configuration

### Development vs Production

#### Development (.env):
```env
DATABASE_URL=sqlite:///wdt_supplychain.db
FLASK_ENV=development
DEBUG=true
```

#### Production (.env):
```env
DATABASE_URL=mysql+pymysql://username:password@IP_ADDRESS:3306/wdt_supplychain
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-production-secret-key
```

## 🔒 Security Best Practices

### 1. Network Security
- **Use authorized networks** to limit access
- **Consider private IP** for VPC deployments
- **Use SSL connections** (enabled by default)

### 2. User Management
- **Create dedicated users** for your application
- **Use strong passwords**
- **Limit user privileges** to only what's needed

### 3. Backup Strategy
- **Enable automated backups**
- **Set retention period** (7-30 days recommended)
- **Test restore procedures** regularly

### 4. Monitoring
- **Enable Cloud Logging**
- **Set up alerts** for high CPU/memory usage
- **Monitor connection count**

## 🚀 Deployment Options

### Option 1: Google Cloud Run (Recommended)
```bash
# Deploy to Cloud Run
gcloud run deploy wdt-supplychain \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Google Compute Engine
```bash
# Deploy to GCE
gcloud compute instances create wdt-app \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=debian-11 \
  --image-project=debian-cloud
```

### Option 3: App Engine
```yaml
# app.yaml
runtime: python39
env_variables:
  DATABASE_URL: "mysql+pymysql://..."
```

## 📊 Performance Optimization

### Connection Pooling
```env
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=600
DB_MAX_OVERFLOW=30
```

### Query Optimization
- **Use indexes** on frequently queried columns
- **Monitor slow queries** in Cloud SQL logs
- **Consider read replicas** for high read loads

## 🔄 Migration from SQLite

### Step 1: Export Data
```bash
# Export current SQLite data
python export_data.py
```

### Step 2: Import to Cloud SQL
```bash
# Import to MySQL
python import_data.py
```

### Step 3: Update Configuration
```env
# Switch to Cloud SQL
DATABASE_URL=mysql+pymysql://...
```

## 📞 Troubleshooting

### Common Issues:

#### Connection Timeout
- **Check firewall rules**
- **Verify IP is authorized**
- **Check instance is running**

#### Authentication Failed
- **Verify username/password**
- **Check user permissions**
- **Ensure SSL is configured correctly**

#### Performance Issues
- **Increase machine size**
- **Optimize queries**
- **Add read replicas**

## 💰 Cost Optimization

### Development:
- **Machine type**: `db-f1-micro` (~$7/month)
- **Storage**: 10 GB SSD (~$1.70/month)

### Production:
- **Machine type**: `db-n1-standard-1` (~$25/month)
- **Storage**: 50 GB SSD (~$8.50/month)
- **Backups**: Included

## 🎯 Benefits

✅ **Scalable** - Easy to upgrade machine size
✅ **Managed** - Google handles backups, updates, security
✅ **Reliable** - 99.95% uptime SLA
✅ **Secure** - Built-in encryption and IAM
✅ **Integrated** - Works seamlessly with other Google Cloud services
✅ **Cost-effective** - Pay only for what you use

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Google Cloud SQL documentation
3. Check Cloud SQL logs in Google Cloud Console
4. Contact Google Cloud support if needed 