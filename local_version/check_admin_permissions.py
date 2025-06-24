from app import app
from models_new import db, User, Role

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    print('Admin:', admin)
    if admin:
        print('Role:', admin.role.name if admin.role else None)
        print('Permissions:', admin.role.permissions if admin.role else None)
    else:
        print('No admin user found')
