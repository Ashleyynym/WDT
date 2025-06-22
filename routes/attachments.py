import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from models import Attachment, Cargo, db
from werkzeug.utils import secure_filename
from flask_babel import _
from datetime import datetime
import pytz

bp = Blueprint('attachments', __name__, url_prefix='/attachments')
UPLOAD_FOLDER = 'uploads/'

@bp.route('/')
@login_required
def attachments_list():
    """General attachments list - show all attachments for the current user"""
    timezone = session.get('timezone', 'America/Los_Angeles')
    file_types = Attachment.get_file_types()
    
    # Get all attachments, optionally filtered by user permissions
    if current_user.has_permission('manage_users'):
        # Admin can see all attachments
        attachments = Attachment.query.all()
    else:
        # Regular users see attachments for cargos they're responsible for
        attachments = Attachment.query.join(Cargo).filter(
            Cargo.responsibles.any(id=current_user.id)
        ).all()
    
    # Convert times to selected timezone
    tz = pytz.timezone(timezone)
    for attachment in attachments:
        if attachment.uploaded_at:
            # Convert UTC to selected timezone
            utc_time = pytz.utc.localize(attachment.uploaded_at)
            attachment.local_time = utc_time.astimezone(tz)
    
    return render_template('attachments_list.html', 
                         attachments=attachments, 
                         file_types=file_types)

@bp.route('/<int:cargo_id>')
@login_required
def list_attachments(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    file_type = request.args.get('file_type', None)
    timezone = session.get('timezone', 'America/Los_Angeles')
    file_types = Attachment.get_file_types()
    
    if file_type and file_type != 'All':
        attachments = Attachment.query.filter_by(cargo_id=cargo_id, file_type=file_type).all()
    else:
        attachments = Attachment.query.filter_by(cargo_id=cargo_id).all()
    
    # Convert times to selected timezone
    tz = pytz.timezone(timezone)
    for attachment in attachments:
        if attachment.uploaded_at:
            # Convert UTC to selected timezone
            utc_time = pytz.utc.localize(attachment.uploaded_at)
            attachment.local_time = utc_time.astimezone(tz)
    
    return render_template('attachments.html', 
                         cargo=cargo, 
                         attachments=attachments, 
                         file_types=file_types, 
                         selected_file_type=file_type or 'All')

@bp.route('/upload/<int:cargo_id>', methods=['GET', 'POST'])
@login_required
def upload_attachment(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    if request.method == 'POST':
        files = request.files.getlist('files')
        file_type = request.form.get('file_type')
        notes = request.form.get('notes')
        for f in files:
            if f.filename:
                original_filename = f.filename
                filename = secure_filename(f.filename)
                save_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, filename)
                f.save(save_path)
                
                # Get file size
                file_size = os.path.getsize(save_path)
                
                # Get MIME type
                mime_type = f.content_type or 'application/octet-stream'

                att = Attachment(
                    cargo_id=cargo_id,
                    filename=filename,
                    original_filename=original_filename,
                    file_type=file_type,
                    file_size=file_size,
                    mime_type=mime_type,
                    uploader_id=current_user.id,
                    notes=notes
                )
                db.session.add(att)
        db.session.commit()
        flash(_("Attachments uploaded."), "success")
        return redirect(url_for('attachments.list_attachments', cargo_id=cargo_id))

    return render_template('attachments.html', cargo=cargo, attachments=cargo.attachments)
