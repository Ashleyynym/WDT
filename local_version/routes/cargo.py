# routes/cargo.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime
from models_new import Cargo, db, EventLog, StatusMilestone
from flask_login import current_user
from flask_babel import _
from functools import wraps
import pytz

bp = Blueprint('cargo', __name__, url_prefix='/cargo')

def permission_required(permission):
    """Decorator to check if user has required permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                flash(_('You do not have permission to perform this action.'), 'error')
                return redirect(url_for('dashboard.dashboard_home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route("/")
@login_required
@permission_required('view_cargo')
def cargo_list():
    # Get filter parameters
    status_filter = request.args.get('status')
    mawb_filter = request.args.get('mawb')
    flight_filter = request.args.get('flight')
    customer_filter = request.args.get('customer')
    
    # Build query
    query = Cargo.query.filter_by(is_archived=False)
    
    if status_filter:
        query = query.filter(Cargo.status == status_filter)
    if mawb_filter:
        query = query.filter(Cargo.main_awb.contains(mawb_filter))
    if flight_filter:
        query = query.filter(Cargo.flight_no.contains(flight_filter))
    if customer_filter:
        query = query.filter(Cargo.customer_name.contains(customer_filter))
    
    cargos = query.order_by(Cargo.created_at.desc()).all()
    
    return render_template("cargo_list.html", cargos=cargos)

@bp.route('/<int:cargo_id>')
@login_required
def cargo_detail(cargo_id):
    """
    Shows detailed view for a single cargo entry.
    """
    cargo = Cargo.query.get_or_404(cargo_id)
    return render_template('cargo_detail.html', cargo=cargo)

@bp.route('/create', methods=['POST'])
@login_required
def cargo_create():
    """
    Handles creation of a new cargo entry from the dashboard modal form.

    Main AWB is required; other fields are optional and can be filled later.
    """
    # Main AWB (required)
    main_awb = request.form.get('main_awb')
    if not main_awb:
        flash("Main AWB is required.", "error")
        return redirect(url_for('dashboard.dashboard_home'))

    # Check if MAWB already exists
    existing_cargo = Cargo.query.filter_by(main_awb=main_awb).first()
    if existing_cargo:
        # Store form data in session for potential editing
        session['pending_cargo_data'] = {
            'main_awb': main_awb,
            'flight_no': request.form.get('flight_no') or None,
            'customer_name': request.form.get('customer_name') or None,
            'eta': request.form.get('eta'),
            'eta_timezone': request.form.get('eta_timezone'),
            'lfd_date': request.form.get('lfd_date'),
            'lfd_timezone': request.form.get('lfd_timezone'),
            'status': request.form.get('status') or None
        }
        return redirect(url_for('cargo.duplicate_mawb_warning', existing_cargo_id=existing_cargo.id))

    # Optional fields
    flight_no     = request.form.get('flight_no') or None
    customer_name = request.form.get('customer_name') or None
    eta_str       = request.form.get('eta')
    eta_timezone  = request.form.get('eta_timezone', 'America/Los_Angeles')
    lfd_str       = request.form.get('lfd_date')
    lfd_timezone  = request.form.get('lfd_timezone', 'America/Los_Angeles')
    status        = request.form.get('status') or None

    # Parse dates with timezone conversion (if provided)
    eta      = None
    lfd_date = None
    try:
        if eta_str:
            # Parse the date in the specified timezone
            tz = pytz.timezone(eta_timezone)
            naive_date = datetime.strptime(eta_str, '%Y-%m-%d')
            local_date = tz.localize(naive_date)
            # Convert to UTC for storage
            eta = local_date.astimezone(pytz.UTC)
            
        if lfd_str:
            # Parse the date in the specified timezone
            tz = pytz.timezone(lfd_timezone)
            naive_date = datetime.strptime(lfd_str, '%Y-%m-%d')
            local_date = tz.localize(naive_date)
            # Convert to UTC for storage
            lfd_date = local_date.astimezone(pytz.UTC)
    except ValueError as e:
        flash(f"Invalid date format: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard_home'))
    except Exception as e:
        flash(f"Error processing dates: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard_home'))

    # Create and commit new cargo
    new_cargo = Cargo(
        main_awb=main_awb,
        flight_no=flight_no,
        customer_name=customer_name,
        eta=eta,
        lfd_date=lfd_date,
        status=status
    )
    db.session.add(new_cargo)
    db.session.commit()

    flash("Cargo added successfully.", "success")
    return redirect(url_for('dashboard.dashboard_home'))

@bp.route('/duplicate-warning/<int:existing_cargo_id>')
@login_required
def duplicate_mawb_warning(existing_cargo_id):
    """
    Shows warning when user tries to create cargo with existing MAWB.
    """
    existing_cargo = Cargo.query.get_or_404(existing_cargo_id)
    pending_data = session.get('pending_cargo_data', {})
    return render_template('duplicate_mawb_warning.html', 
                         existing_cargo=existing_cargo, 
                         pending_data=pending_data)

@bp.route('/handle-duplicate/<int:existing_cargo_id>', methods=['POST'])
@login_required
def handle_duplicate_mawb(existing_cargo_id):
    """
    Handles user choice when duplicate MAWB is detected.
    """
    action = request.form.get('action')
    
    if action == 'ok':
        # User chose to cancel, clear session data and redirect to dashboard
        session.pop('pending_cargo_data', None)
        flash("Cargo creation cancelled.", "info")
        return redirect(url_for('dashboard.dashboard_home'))
    
    elif action == 'edit':
        # User chose to update the existing MAWB with new information
        cargo = Cargo.query.get_or_404(existing_cargo_id)
        pending_data = session.get('pending_cargo_data', {})
        
        # Update cargo with new form data
        cargo.flight_no = pending_data.get('flight_no') or None
        cargo.customer_name = pending_data.get('customer_name') or None
        cargo.status = pending_data.get('status') or None
        
        # Parse dates with timezone conversion
        eta_str = pending_data.get('eta')
        eta_timezone = pending_data.get('eta_timezone', 'America/Los_Angeles')
        lfd_str = pending_data.get('lfd_date')
        lfd_timezone = pending_data.get('lfd_timezone', 'America/Los_Angeles')
        
        try:
            if eta_str:
                # Parse the date in the specified timezone
                tz = pytz.timezone(eta_timezone)
                naive_date = datetime.strptime(eta_str, '%Y-%m-%d')
                local_date = tz.localize(naive_date)
                # Convert to UTC for storage
                cargo.eta = local_date.astimezone(pytz.UTC)
            else:
                cargo.eta = None
                
            if lfd_str:
                # Parse the date in the specified timezone
                tz = pytz.timezone(lfd_timezone)
                naive_date = datetime.strptime(lfd_str, '%Y-%m-%d')
                local_date = tz.localize(naive_date)
                # Convert to UTC for storage
                cargo.lfd_date = local_date.astimezone(pytz.UTC)
            else:
                cargo.lfd_date = None
        except ValueError as e:
            flash(f"Invalid date format: {str(e)}", "error")
            session.pop('pending_cargo_data', None)
            return redirect(url_for('dashboard.dashboard_home'))
        except Exception as e:
            flash(f"Error processing dates: {str(e)}", "error")
            session.pop('pending_cargo_data', None)
            return redirect(url_for('dashboard.dashboard_home'))
        
        db.session.commit()
        session.pop('pending_cargo_data', None)
        flash("MAWB updated successfully with new information.", "success")
        return redirect(url_for('dashboard.dashboard_home'))
    
    # Default fallback
    return redirect(url_for('dashboard.dashboard_home'))

@bp.route('/edit/<int:cargo_id>', methods=['GET', 'POST'])
@login_required
def edit_cargo(cargo_id):
    """
    Edit an existing cargo entry.
    """
    cargo = Cargo.query.get_or_404(cargo_id)
    
    if request.method == 'POST':
        # Update cargo with form data
        cargo.flight_no = request.form.get('flight_no') or None
        cargo.customer_name = request.form.get('customer_name') or None
        cargo.status = request.form.get('status') or None
        
        # Parse dates
        eta_str = request.form.get('eta')
        lfd_str = request.form.get('lfd_date')
        
        try:
            if eta_str:
                cargo.eta = datetime.strptime(eta_str, '%Y-%m-%d')
            else:
                cargo.eta = None
                
            if lfd_str:
                cargo.lfd_date = datetime.strptime(lfd_str, '%Y-%m-%d')
            else:
                cargo.lfd_date = None
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for('cargo.edit_cargo', cargo_id=cargo_id))
        
        # Set last changed by
        cargo.last_changed_by = current_user
        db.session.commit()
        flash("Cargo updated successfully.", "success")
        return redirect(url_for('cargo.cargo_detail', cargo_id=cargo.id))
    
    return render_template('edit_cargo.html', cargo=cargo)

@bp.route('/<int:cargo_id>/edit', methods=['GET', 'POST'])
def edit_cargo_alt(cargo_id):
    """
    Redirect /cargo/<cargo_id>/edit to /cargo/edit/<cargo_id> for compatibility.
    """
    return redirect(url_for('cargo.edit_cargo', cargo_id=cargo_id))

@bp.route('/batch-edit', methods=['POST'])
@login_required
def batch_edit():
    """
    Handle batch editing of multiple cargo entries - returns changes summary.
    """
    changes = []
    
    # Get all cargo entries
    all_cargos = Cargo.query.all()
    
    for cargo in all_cargos:
        cargo_id = str(cargo.id)
        
        # Get form values for this cargo
        flight_no = request.form.get(f'flight_no_{cargo_id}')
        customer_name = request.form.get(f'customer_name_{cargo_id}')
        eta_str = request.form.get(f'eta_{cargo_id}')
        lfd_str = request.form.get(f'lfd_date_{cargo_id}')
        status = request.form.get(f'status_{cargo_id}')
        
        # Check if any changes were made
        changes_made = []
        
        if flight_no != (cargo.flight_no or ''):
            changes_made.append(f"Flight No: {cargo.flight_no or 'None'} → {flight_no or 'None'}")
            
        if customer_name != (cargo.customer_name or ''):
            changes_made.append(f"Customer: {cargo.customer_name or 'None'} → {customer_name or 'None'}")
            
        if status != (cargo.status or ''):
            changes_made.append(f"Status: {cargo.status or 'None'} → {status or 'None'}")
            
        # Handle date changes
        try:
            new_eta = None
            if eta_str:
                new_eta = datetime.strptime(eta_str, '%Y-%m-%d')
            
            if new_eta != cargo.eta:
                old_eta_str = cargo.eta.strftime('%Y-%m-%d') if cargo.eta else 'None'
                new_eta_str = new_eta.strftime('%Y-%m-%d') if new_eta else 'None'
                changes_made.append(f"ETA: {old_eta_str} → {new_eta_str}")
                
            new_lfd = None
            if lfd_str:
                new_lfd = datetime.strptime(lfd_str, '%Y-%m-%d')
                
            if new_lfd != cargo.lfd_date:
                old_lfd_str = cargo.lfd_date.strftime('%Y-%m-%d') if cargo.lfd_date else 'None'
                new_lfd_str = new_lfd.strftime('%Y-%m-%d') if new_lfd else 'None'
                changes_made.append(f"LFD: {old_lfd_str} → {new_lfd_str}")
                
        except ValueError:
            return jsonify({'success': False, 'message': f"Invalid date format for cargo {cargo.main_awb}"})
        
        # If changes were made, add to changes list
        if changes_made:
            changes.append({
                'mawb': cargo.main_awb,
                'changes': changes_made
            })
    
    # If no changes, return message
    if not changes:
        return jsonify({'success': False, 'message': 'No changes were made.'})
    
    # Store changes in session for confirmation
    session['batch_changes'] = changes
    
    return jsonify({'success': True, 'changes': changes})

@bp.route('/batch-edit-confirm', methods=['POST'])
@login_required
def batch_edit_confirm():
    """
    Apply the confirmed batch changes to the database.
    """
    changes = session.get('batch_changes', [])
    
    if not changes:
        return jsonify({'success': False, 'message': 'No changes to apply.'})
    
    # Get all cargo entries
    all_cargos = Cargo.query.all()
    
    try:
        for cargo in all_cargos:
            cargo_id = str(cargo.id)
            
            # Get form values for this cargo
            flight_no = request.form.get(f'flight_no_{cargo_id}')
            customer_name = request.form.get(f'customer_name_{cargo_id}')
            eta_str = request.form.get(f'eta_{cargo_id}')
            lfd_str = request.form.get(f'lfd_date_{cargo_id}')
            status = request.form.get(f'status_{cargo_id}')
            
            # Apply changes
            cargo.flight_no = flight_no if flight_no else None
            cargo.customer_name = customer_name if customer_name else None
            cargo.status = status if status else None
            
            # Handle dates
            if eta_str:
                cargo.eta = datetime.strptime(eta_str, '%Y-%m-%d')
            else:
                cargo.eta = None
                
            if lfd_str:
                cargo.lfd_date = datetime.strptime(lfd_str, '%Y-%m-%d')
            else:
                cargo.lfd_date = None
        
        # Commit all changes
        db.session.commit()
        
        # Clear session data
        session.pop('batch_changes', None)
        
        return jsonify({'success': True, 'message': f'Successfully updated {len(changes)} cargo entries.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error applying changes: {str(e)}'})

@bp.route("/cargo/<int:cargo_id>/record_event", methods=["GET", "POST"])
@login_required
def record_event(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    
    if request.method == "POST":
        description = request.form.get("description")
        if description:
            event = EventLog(
                cargo_id=cargo_id,
                description=description,
                performed_by_id=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash(_("Event recorded successfully!"), "success")
            return redirect(url_for("cargo.cargo_detail", cargo_id=cargo_id))
    
    return render_template("record_event.html", cargo=cargo)

@bp.route("/cargo/<int:cargo_id>/add_milestone", methods=["POST"])
@login_required
def add_milestone(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    
    milestone_type = request.form.get("milestone_type")
    notes = request.form.get("notes")
    
    if milestone_type:
        milestone = StatusMilestone(
            cargo_id=cargo_id,
            milestone_type=milestone_type,
            notes=notes,
            completed_by_id=current_user.id
        )
        db.session.add(milestone)
        db.session.commit()
        flash(_("Milestone added successfully!"), "success")
    
    return redirect(url_for("cargo.cargo_detail", cargo_id=cargo_id))

@bp.route("/export/excel")
@login_required
@permission_required('view_cargo')
def export_excel():
    """Export cargo list to Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        # Get all cargo data
        cargos = Cargo.query.filter_by(is_archived=False).all()
        
        # Prepare data for export
        data = []
        for cargo in cargos:
            responsibles = ', '.join([u.username for u in cargo.responsibles]) if cargo.responsibles else ''
            data.append({
                'MAWB': cargo.main_awb,
                'Flight No.': cargo.flight_no or '',
                'Customer': cargo.customer_name or '',
                'Origin': cargo.origin or '',
                'Destination': cargo.destination or '',
                'ETA': cargo.eta.strftime('%Y-%m-%d') if cargo.eta else '',
                'LFD': cargo.lfd_date.strftime('%Y-%m-%d') if cargo.lfd_date else '',
                'Status': cargo.status or '',
                'Weight': cargo.weight or '',
                'Pieces': cargo.pieces or '',
                'Responsibles': responsibles,
                'Created': cargo.created_at.strftime('%Y-%m-%d %H:%M'),
                'Updated': cargo.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Cargo List', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'cargo_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except ImportError:
        flash(_('Excel export requires pandas and openpyxl packages.'), 'error')
        return redirect(url_for('cargo.cargo_list'))
    except Exception as e:
        flash(_('Error exporting to Excel: ') + str(e), 'error')
        return redirect(url_for('cargo.cargo_list'))

@bp.route("/export/csv")
@login_required
@permission_required('view_cargo')
def export_csv():
    """Export cargo list to CSV"""
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        # Get all cargo data
        cargos = Cargo.query.filter_by(is_archived=False).all()
        
        # Create CSV data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'MAWB', 'Flight No.', 'Customer', 'Origin', 'Destination', 
            'ETA', 'LFD', 'Status', 'Weight', 'Pieces', 'Responsibles', 
            'Created', 'Updated'
        ])
        
        # Write data
        for cargo in cargos:
            responsibles = ', '.join([u.username for u in cargo.responsibles]) if cargo.responsibles else ''
            writer.writerow([
                cargo.main_awb,
                cargo.flight_no or '',
                cargo.customer_name or '',
                cargo.origin or '',
                cargo.destination or '',
                cargo.eta.strftime('%Y-%m-%d') if cargo.eta else '',
                cargo.lfd_date.strftime('%Y-%m-%d') if cargo.lfd_date else '',
                cargo.status or '',
                cargo.weight or '',
                cargo.pieces or '',
                responsibles,
                cargo.created_at.strftime('%Y-%m-%d %H:%M'),
                cargo.updated_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=cargo_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
    except Exception as e:
        flash(_('Error exporting to CSV: ') + str(e), 'error')
        return redirect(url_for('cargo.cargo_list'))

@bp.route('/delete/<int:cargo_id>')
@login_required
@permission_required('edit_cargo')
def cargo_delete(cargo_id):
    """
    Delete a cargo entry and all related records (attachments, bills, events, etc.).
    """
    cargo = Cargo.query.get_or_404(cargo_id)
    try:
        # Delete all related records first to avoid foreign key constraint violations
        
        # Delete attachments
        for attachment in cargo.attachments:
            db.session.delete(attachment)
        
        # Delete bills
        for bill in cargo.bills:
            db.session.delete(bill)
        
        # Delete events
        for event in cargo.events:
            db.session.delete(event)
        
        # Delete emails
        for email in cargo.emails:
            db.session.delete(email)
        
        # Delete status milestones
        for milestone in cargo.milestones:
            db.session.delete(milestone)
        
        # Now delete the cargo
        db.session.delete(cargo)
        db.session.commit()
        flash(_('Cargo deleted successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting cargo: ') + str(e), 'error')
    return redirect(url_for('dashboard.dashboard_home'))




