import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models_new import EmailLog, Cargo, EmailTemplate, db
from flask_babel import _

bp = Blueprint('email_center', __name__, url_prefix='/email')

@bp.route('/', methods=['GET'])
@login_required
def email_center():
    """
    Main Email Center - Shows email logs and templates
    """
    # Get all email logs
    email_logs = EmailLog.query.order_by(EmailLog.sent_at.desc()).limit(50).all()
    
    # Get all email templates
    email_templates = EmailTemplate.query.all()
    
    return render_template('email_center_main.html', 
                         email_logs=email_logs, 
                         email_templates=email_templates)

@bp.route('/templates', methods=['GET', 'POST'])
@login_required
def manage_templates():
    """
    Email template management
    """
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        if name and subject and body:
            template = EmailTemplate(
                name=name,
                subject=subject,
                body=body
            )
            db.session.add(template)
            db.session.commit()
            flash(_("Email template created successfully."), "success")
            return redirect(url_for('email_center.manage_templates'))
    
    templates = EmailTemplate.query.all()
    return render_template('email_templates.html', templates=templates)

@bp.route('/send/<int:cargo_id>', methods=['GET', 'POST'])
@login_required
def send_business_email(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    if request.method == 'POST':
        template_name = request.form.get('template_name')
        to_emails = request.form.get('to_emails')
        subject = request.form.get('subject')
        body = request.form.get('body')

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = 'no-reply@wdtsupplychain.com'
        msg['To'] = to_emails

        try:
            smtp = smtplib.SMTP('localhost')
            smtp.sendmail(msg['From'], to_emails.split(','), msg.as_string())
            smtp.quit()

            log = EmailLog(
                cargo_id=cargo_id,
                template_name=template_name,
                recipients=to_emails,
                subject=subject,
                body=body,
                sent_by_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
            flash(_("Email sent and logged."), "success")
        except Exception as e:
            flash(_("Failed to send email: %(err)s", err=str(e)), "danger")

        return redirect(url_for('email_center.send_business_email', cargo_id=cargo_id))

    return render_template('email_center.html', cargo=cargo)
