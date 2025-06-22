import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Bill, Cargo, db
from werkzeug.utils import secure_filename
from flask_babel import _

bp = Blueprint('bills', __name__, url_prefix='/bills')
BILL_UPLOAD_FOLDER = 'uploads/bills/'

@bp.route('/')
@login_required
def bills_list():
    """General bills list - show all bills for the current user"""
    # Get all bills, optionally filtered by user permissions
    if current_user.has_permission('manage_users'):
        # Admin can see all bills
        bills = Bill.query.all()
    else:
        # Regular users see bills for cargos they're responsible for
        bills = Bill.query.join(Cargo).filter(
            Cargo.responsibles.any(id=current_user.id)
        ).all()
    
    return render_template('bills_list.html', bills=bills)

@bp.route('/<int:cargo_id>')
@login_required
def list_bills(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    bills = Bill.query.filter_by(cargo_id=cargo_id).all()
    return render_template('bills.html', cargo=cargo, bills=bills)

@bp.route('/add/<int:cargo_id>', methods=['GET', 'POST'])
@login_required
def add_bill(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name')
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        currency = request.form.get('currency')
        payment_status = request.form.get('payment_status')
        notes = request.form.get('notes')

        file = request.files.get('bill_file')
        filename = None
        if file:
            filename = secure_filename(file.filename)
            save_dir = os.path.join(current_app.root_path, BILL_UPLOAD_FOLDER)
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            file.save(save_path)

        new_bill = Bill(
            cargo_id=cargo_id,
            supplier_name=supplier_name,
            category=category,
            amount=amount,
            currency=currency,
            payment_status=payment_status,
            uploaded_by_id=current_user.id,
            notes=notes
        )
        db.session.add(new_bill)
        db.session.commit()
        flash(_("Bill added successfully."), "success")
        return redirect(url_for('bills.list_bills', cargo_id=cargo_id))

    return render_template('bills.html', cargo=cargo, bills=cargo.bills)
