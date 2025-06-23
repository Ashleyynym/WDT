import os
import random
from datetime import datetime, timedelta
from faker import Faker
from models import db, User, Role, Cargo, Bill, Attachment
from app import app
import json

UPLOADS_DIR = 'uploads'

fake = Faker()

# --- Utility functions ---
def get_random_file():
    files = [f for f in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
    return random.choice(files) if files else None

def get_random_file_type():
    return random.choice(Attachment.get_file_types())

# --- Main data generation ---
def create_roles():
    roles = [
        ('Admin', ['manage_users', 'manage_roles', 'manage_templates', 'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails', 'sign_do_pod', 'view_archives', 'archive_records', 'modify_status', 'log_inspection', 'log_destruction']),
        ('US Operations Staff', ['view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails', 'view_archives', 'archive_records', 'modify_status']),
        ('Warehouse Staff', ['view_cargo', 'edit_cargo', 'upload_attachments', 'sign_do_pod', 'view_archives']),
    ]
    role_objs = []
    for name, perms in roles:
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, permissions=json.dumps(perms))
            db.session.add(role)
        role_objs.append(role)
    db.session.commit()
    return role_objs

def create_users(roles):
    users = []
    for i, role in enumerate(roles):
        user = User.query.filter_by(username=f"user{i+1}").first()
        if not user:
            user = User(
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                role=role,
                is_active=True
            )
            user.set_password('password')
            db.session.add(user)
        users.append(user)
    db.session.commit()
    return users

def create_cargos(users, n=5):
    cargos = []
    statuses = ['In Progress', 'Completed']
    for i in range(n):
        status = statuses[i % 2]  # Alternate for variety
        cargo = Cargo(
            main_awb=fake.unique.bothify(text='###-########'),
            flight_no=fake.bothify(text='??####'),
            eta=datetime.now() + timedelta(days=random.randint(1, 10)),
            lfd_date=datetime.now() + timedelta(days=random.randint(5, 15)),
            status=status,
            customer_name=fake.company(),
            origin=fake.city(),
            destination=fake.city(),
            weight=round(random.uniform(100, 1000), 2),
            pieces=random.randint(1, 20),
            description=fake.text(50),
            special_handling=fake.sentence(),
            is_archived=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        # Assign a random user as responsible
        cargo.responsibles.append(random.choice(users))
        db.session.add(cargo)
        cargos.append(cargo)
    db.session.commit()
    return cargos

def create_bills(cargos, users, n=10):
    for _ in range(n):
        cargo = random.choice(cargos)
        user = random.choice(users)
        bill = Bill(
            cargo_id=cargo.id,
            supplier_name=fake.company(),
            category=random.choice(Bill.get_categories()),
            amount=round(random.uniform(100, 5000), 2),
            currency='USD',
            payment_status=random.choice(['Paid', 'Pending', 'Unpaid']),
            due_date=datetime.now() + timedelta(days=random.randint(1, 30)),
            payment_date=None,
            invoice_number=fake.unique.bothify(text='INV####'),
            uploaded_at=datetime.now(),
            uploaded_by_id=user.id,
            notes=fake.sentence(),
            is_archived=False
        )
        db.session.add(bill)
    db.session.commit()

def create_attachments(cargos, users, n=6):
    files = [f for f in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
    for i in range(n):
        cargo = random.choice(cargos)
        user = random.choice(users)
        filename = random.choice(files)
        file_path = os.path.join(UPLOADS_DIR, filename)
        att = Attachment(
            cargo_id=cargo.id,
            filename=filename,
            original_filename=filename,
            file_type=get_random_file_type(),
            file_size=os.path.getsize(file_path),
            mime_type='application/pdf' if filename.endswith('.pdf') else 'text/plain',
            uploader_id=user.id,
            uploaded_at=datetime.now(),
            notes=fake.sentence(),
            is_archived=False
        )
        db.session.add(att)
    db.session.commit()

def main():
    with app.app_context():
        print('Creating roles...')
        roles = create_roles()
        print('Creating users...')
        users = create_users(roles)
        print('Creating cargos...')
        cargos = create_cargos(users)
        print('Creating bills...')
        create_bills(cargos, users)
        print('Creating attachments...')
        create_attachments(cargos, users)
        print('Sample data created!')

if __name__ == '__main__':
    main() 