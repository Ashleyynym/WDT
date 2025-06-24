import os
import random
from datetime import datetime, timedelta
from faker import Faker
from models_new import db, User, Role, Cargo, Bill, Attachment, EventLog, StatusMilestone, EmailLog
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
        ("Admin", [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails',
            'view_archives', 'archive_records', 'modify_status', 'manage_users', 'manage_templates', 'manage_roles'
        ]),
        ("US Operations Staff", [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails',
            'view_archives', 'archive_records', 'modify_status'
        ]),
        ("Domestic Operations Staff", [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'create_bills', 'send_emails',
            'view_archives', 'archive_records', 'modify_status'
        ]),
        ("Warehouse Staff", [
            'view_cargo', 'edit_cargo', 'upload_attachments', 'sign_do_pod', 'view_archives'
        ]),
        ("Customs Brokers (log only)", [
            'archive_records'
        ]),
        ("Airline Representatives (log only)", [
            'archive_records'
        ]),
        ("Inspection Centers (CES) (log only)", [
            'archive_records'
        ]),
        ("Destruction Companies (log only)", [
            'archive_records'
        ]),
    ]
    role_objs = []
    for name, perms in roles:
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, permissions=json.dumps(perms))
            db.session.add(role)
        else:
            role.permissions = json.dumps(perms)
        role_objs.append(role)
    db.session.commit()
    return role_objs

def create_users(roles, n=10):
    users = []
    for i in range(n):
        role = random.choice(roles)
        user = User.query.filter_by(username=f"user{i+1}").first()
        if not user:
            user = User(
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=role,
                is_active=True
            )
            user.set_password('password')
            db.session.add(user)
        users.append(user)
    db.session.commit()
    return users

def create_admin(roles):
    admin_role = next((r for r in roles if r.name == 'Admin'), None)
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Alice',
            last_name='Admin',
            role=admin_role,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    return admin

def create_cargos(users, n=15):
    cargos = []
    statuses = ['In Progress', 'Completed', 'Processing', 'Awaiting Inspection', 'Released']
    for i in range(n):
        status = random.choice(statuses)
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
        # Assign 1-3 unique random users as responsible
        responsible_users = random.sample(users, k=random.randint(1, min(3, len(users))))
        for user in responsible_users:
            cargo.responsibles.append(user)
        db.session.add(cargo)
        cargos.append(cargo)
    db.session.commit()
    return cargos

def create_bills(cargos, users, n=30):
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

def create_attachments(cargos, users, n=20):
    files = [f for f in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
    for i in range(n):
        cargo = random.choice(cargos)
        user = random.choice(users)
        filename = random.choice(files) if files else f"file{i+1}.pdf"
        file_path = os.path.join(UPLOADS_DIR, filename) if files else None
        att = Attachment(
            cargo_id=cargo.id,
            filename=filename,
            original_filename=filename,
            file_type=get_random_file_type(),
            file_size=os.path.getsize(file_path) if file_path and os.path.exists(file_path) else random.randint(10000, 500000),
            mime_type='application/pdf' if filename.endswith('.pdf') else 'text/plain',
            uploader_id=user.id,
            uploaded_at=datetime.now(),
            notes=fake.sentence(),
            is_archived=False
        )
        db.session.add(att)
    db.session.commit()

def create_events_and_milestones(cargos, users, n=40):
    for _ in range(n):
        cargo = random.choice(cargos)
        user = random.choice(users)
        event = EventLog(
            cargo_id=cargo.id,
            timestamp=datetime.now(),
            description=fake.sentence(),
            performed_by_id=user.id
        )
        db.session.add(event)
        milestone = StatusMilestone(
            cargo_id=cargo.id,
            milestone_type=random.choice(['PRE-ALERT', 'Payment', 'Inspection', 'DO received', 'POD signed']),
            timestamp=datetime.now(),
            notes=fake.sentence(),
            completed_by_id=user.id
        )
        db.session.add(milestone)
    db.session.commit()

def create_emails(cargos, users, n=30):
    for _ in range(n):
        cargo = random.choice(cargos)
        user = random.choice(users)
        email = EmailLog(
            cargo_id=cargo.id,
            template_name=random.choice(['Pre-Alert', 'Invoice', 'Reminder']),
            recipients=fake.email(),
            subject=fake.sentence(),
            body=fake.text(100),
            sent_at=datetime.now(),
            sent_by_id=user.id
        )
        db.session.add(email)
    db.session.commit()

def main():
    with app.app_context():
        print('Creating roles...')
        roles = create_roles()
        print('Creating admin user...')
        admin = create_admin(roles)
        print('Creating users...')
        users = create_users(roles, n=15)
        users.append(admin)
        print('Creating cargos...')
        cargos = create_cargos(users, n=30)
        print('Creating bills...')
        create_bills(cargos, users, n=60)
        print('Creating attachments...')
        create_attachments(cargos, users, n=40)
        print('Creating events and milestones...')
        create_events_and_milestones(cargos, users, n=80)
        print('Creating emails...')
        create_emails(cargos, users, n=60)
        print('Sample data created! Admin login: admin/admin123')

if __name__ == '__main__':
    main()