import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import EmailLog, Cargo, db
from flask_babel import _

bp = Blueprint('email_center', __name__, url_prefix='/email')

@bp.route('/templates', methods=['GET', 'POST'])
@login_required
def manage_templates():
    """
    邮件模板管理 (TODO)
    """
    return render_template('email_center.html')

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
        msg['From'] = 'no-reply@wdt.com'
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
