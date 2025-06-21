from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Role, db, PERMISSIONS
from werkzeug.security import generate_password_hash
from flask_babel import _
import re
import dns.resolver
import json

bp = Blueprint('users', __name__, url_prefix='/users')

# A fixed list of role names to show in the dropdown (based on Appendix D: User Permissions Matrix)
STATIC_ROLES = [
    "Admin",
    "US Operations Staff",
    "Domestic Operations Staff", 
    "Warehouse Staff",
    "Customs Brokers (log only)",
    "Airline Representatives (log only)",
    "Inspection Centers (CES) (log only)",
    "Destruction Companies (log only)"
]

# Define permissions for user management
PERMISSIONS = {
    'view_users': 'View Users',
    'manage_users': 'Manage Users',
    'view_roles': 'View Roles',
    'manage_roles': 'Manage Roles',
    'view_permissions': 'View Permissions',
    'manage_permissions': 'Manage Permissions'
}

@bp.route('/check_email_domain', methods=['POST'])
def check_email_domain():
    """
    Check if an email address is valid using basic validation and DNS check
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email or '@' not in email:
            return jsonify({'valid': False, 'message': 'Invalid email format'})
        
        # Split email into parts
        parts = email.split('@')
        if len(parts) != 2:
            return jsonify({'valid': False, 'message': 'Invalid email format'})
        
        username, domain = parts
        
        # Check username
        if len(username) == 0 or len(username) > 64:
            return jsonify({'valid': False, 'message': 'Invalid username length'})
        
        # Check domain
        if len(domain) == 0 or len(domain) > 253:
            return jsonify({'valid': False, 'message': 'Domain name too long'})
        
        # Split domain into parts
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            return jsonify({'valid': False, 'message': 'Invalid domain format'})
        
        # Check each domain part
        for part in domain_parts:
            if len(part) == 0 or len(part) > 63:
                return jsonify({'valid': False, 'message': 'Invalid domain part length'})
            
            # Check for valid characters in domain parts
            if not part.replace('-', '').isalnum():
                return jsonify({'valid': False, 'message': 'Invalid characters in domain'})
            
            # Check for invalid patterns
            if part.startswith('-') or part.endswith('-'):
                return jsonify({'valid': False, 'message': 'Domain part cannot start or end with hyphen'})
        
        # Check TLD (last part) - must be letters only
        tld = domain_parts[-1]
        if not tld.isalpha():
            return jsonify({'valid': False, 'message': 'Domain extension must contain only letters'})
        
        if len(tld) < 2 or len(tld) > 6:
            return jsonify({'valid': False, 'message': 'Invalid domain extension length'})
        
        # Check for common invalid patterns
        invalid_patterns = [
            '..',  # Double dots
            '.-',  # Dot followed by hyphen
            '-.',  # Hyphen followed by dot
            '--',  # Double hyphens
        ]
        
        for pattern in invalid_patterns:
            if pattern in domain:
                return jsonify({'valid': False, 'message': 'Invalid domain format'})
        
        # Check DNS MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                return jsonify({'valid': True, 'message': 'Email format is valid and domain has mail servers'})
            else:
                return jsonify({'valid': False, 'message': 'Domain does not have mail servers'})
        except dns.resolver.NXDOMAIN:
            return jsonify({'valid': False, 'message': 'Domain does not exist'})
        except dns.resolver.NoAnswer:
            return jsonify({'valid': False, 'message': 'Domain does not have mail servers'})
        except Exception as dns_error:
            return jsonify({'valid': False, 'message': 'Unable to verify domain'})
            
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Error validating email address'})

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册新用户 (username, email, password, static role list)
    """
    if request.method == 'POST':
        username    = request.form.get('username')
        email       = request.form.get('email')
        password    = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role_name   = request.form.get('role_name')  # now a role name string

        # Basic form validation
        if not username or not email or not password or not confirm_password or not role_name:
            flash(_("All fields are required."), "danger")
            return redirect(url_for('users.register'))

        # Check if passwords match
        if password != confirm_password:
            flash(_("Passwords do not match. Please try again."), "danger")
            return redirect(url_for('users.register'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash(_("Username already exists."), "danger")
            return redirect(url_for('users.register'))

        # Find or create the Role by its name
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name} (auto-created)")
            db.session.add(role)
            db.session.commit()

        # Create the new user and assign the role's ID
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.role_id = role.id
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(_("Registration successful. Please log in."), "success")
        return redirect(url_for('users.login'))

    # GET: show the form with a static list of roles
    return render_template('register.html', static_roles=STATIC_ROLES)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            flash(_("Username does not exist. Please check your username or register for a new account."), "warning")
            return render_template("login.html", username=username)
        
        if user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            
            # Detect and set user's timezone if not already set
            if not session.get('timezone'):
                # Get timezone from request headers or default
                timezone = request.headers.get('X-Timezone', 'America/Los_Angeles')
                
                # Validate and map timezone
                valid_timezones = [
                    'America/Los_Angeles', 'America/New_York', 'America/Chicago', 
                    'America/Denver', 'UTC', 'Asia/Shanghai', 'Asia/Tokyo', 
                    'Europe/London', 'Europe/Paris'
                ]
                
                if timezone in valid_timezones:
                    session['timezone'] = timezone
                else:
                    session['timezone'] = 'America/Los_Angeles'
                
                # Show timezone alert
                timezone_names = {
                    'America/Los_Angeles': 'Los Angeles (PST/PDT)',
                    'America/New_York': 'New York (EST/EDT)',
                    'America/Chicago': 'Chicago (CST/CDT)',
                    'America/Denver': 'Denver (MST/MDT)',
                    'UTC': 'UTC',
                    'Asia/Shanghai': 'Shanghai (CST)',
                    'Asia/Tokyo': 'Tokyo (JST)',
                    'Europe/London': 'London (GMT/BST)',
                    'Europe/Paris': 'Paris (CET/CEST)'
                }
                
                display_name = timezone_names.get(session['timezone'], session['timezone'])
                flash(f"<div style='font-size: 16px; font-weight: bold;'>Welcome! Your timezone has been set to: <span style='color: #007bff;'>{display_name}</span></div><div style='font-size: 14px; margin-top: 5px;'>You can change this anytime using the timezone dropdown in the navigation bar.</div>", "info")
            
            if not next_page or not next_page.startswith('/'):
                next_page = url_for("dashboard.dashboard_home")
            return redirect(next_page)
        else:
            flash(_("Invalid password. Please try again."), "error")
    
    return render_template("login.html")

@bp.route('/logout')
@login_required
def logout():
    """
    注销
    """
    logout_user()
    flash(_("You have been logged out."), "info")
    return redirect(url_for('users.login'))

@bp.route('/user-management')
@login_required
def user_management():
    """
    Admin-only user and role management page.
    Shows roles and permissions table, and user management table.
    """
    # Check if user has admin permissions
    if not current_user.has_permission('manage_users'):
        flash(_('You do not have permission to access this page.'), 'error')
        return redirect(url_for('dashboard.dashboard_home'))
    
    # Get all roles with their permissions
    roles = Role.query.all()
    
    # Get all users with their roles
    users = User.query.all()
    
    # Get all possible permissions from models.py
    from models import PERMISSIONS
    all_permissions = list(PERMISSIONS.keys())
    
    return render_template('user_management.html', 
                         roles=roles, 
                         users=users, 
                         all_permissions=all_permissions,
                         permissions=PERMISSIONS)

@bp.route('/update-user-permissions', methods=['POST'])
@login_required
def update_user_permissions():
    """
    Update user permissions (admin only).
    """
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        permissions = data.get('permissions', [])
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Update user's role permissions
        if user.role:
            user.role.permissions = json.dumps(permissions)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Permissions updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'User has no role assigned'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating permissions: {str(e)}'})

@bp.route('/update-role-permissions', methods=['POST'])
@login_required
def update_role_permissions():
    """
    Update role permissions (admin only).
    """
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        data = request.get_json()
        role_id = data.get('role_id')
        permissions = data.get('permissions', [])
        
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'success': False, 'message': 'Role not found'})
        
        # Update role permissions
        role.permissions = json.dumps(permissions)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Role permissions updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating role permissions: {str(e)}'})

