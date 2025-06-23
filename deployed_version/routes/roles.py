from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Role, db
from flask_babel import _
bp = Blueprint('roles', __name__, url_prefix='/roles')

@bp.route('/')
@login_required
def list_roles():
    """
    列出所有角色
    """
    roles = Role.query.all()
    return render_template('user_management.html', roles=roles)

@bp.route('/add', methods=['POST'])
@login_required
def add_role():
    name = request.form.get('name')
    description = request.form.get('description')
    if Role.query.filter_by(name=name).first():
        flash(_("Role already exists."), "danger")
    else:
        new = Role(name=name, description=description)
        db.session.add(new)
        db.session.commit()
        flash(_("Role added."), "success")
    return redirect(url_for('roles.list_roles'))

@bp.route('/delete/<int:role_id>', methods=['GET'])
@login_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash(_("Role deleted."), "info")
    return redirect(url_for('roles.list_roles'))
