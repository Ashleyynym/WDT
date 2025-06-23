from flask import Flask, request, session, redirect, url_for, jsonify, render_template, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import refresh
from datetime import datetime, timedelta
import pytz
import json
import logging
import os

from config import Config
from extensions import db, migrate, login_manager, babel

# Import new backend components
from models_new import *
from routes.api import api
from services.audit_logger import audit_logger, init_audit_logger
from services.job_scheduler import job_scheduler
from services.workflow_engine import WorkflowEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure locale selector for Flask-Babel 4.x
# @babel.localeselector
# def get_locale():
#     if "lang" in session:
#         return session["lang"]
#     return request.accept_languages.best_match(["en"])

def get_current_time():
    """Get current time in user's timezone"""
    timezone_name = get_user_timezone()
    tz = pytz.timezone(timezone_name)
    return datetime.now(tz)

def get_user_timezone():
    """Get the user's current timezone from session"""
    return session.get('timezone', 'America/Los_Angeles')

def get_timezone_abbreviation(timezone_name):
    """Get timezone abbreviation for display"""
    timezone_abbrevs = {
        'America/Los_Angeles': 'PST/PDT',
        'America/New_York': 'EST/EDT',
        'America/Chicago': 'CST/CDT',
        'America/Denver': 'MST/MDT',
        'UTC': 'UTC',
        'Asia/Shanghai': 'CST',
        'Asia/Tokyo': 'JST',
        'Europe/London': 'GMT/BST',
        'Europe/Paris': 'CET/CEST'
    }
    return timezone_abbrevs.get(timezone_name, timezone_name)

def format_datetime_with_timezone(dt, timezone_name=None):
    """Format datetime with timezone abbreviation"""
    if not dt:
        return ""
    
    if timezone_name is None:
        timezone_name = get_user_timezone()
    
    try:
        tz = pytz.timezone(timezone_name)
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        local_dt = dt.astimezone(tz)
        abbrev = get_timezone_abbreviation(timezone_name)
        return f"{local_dt.strftime('%Y-%m-%d %H:%M')} {abbrev}"
    except:
        return dt.strftime('%Y-%m-%d %H:%M')

def format_date_with_timezone(dt, timezone_name=None):
    """Format date with timezone abbreviation"""
    if not dt:
        return ""
    
    if timezone_name is None:
        timezone_name = get_user_timezone()
    
    try:
        tz = pytz.timezone(timezone_name)
        if dt.tzinfo is None:
            # Treat naive dates as being in the user's timezone, not UTC
            dt = tz.localize(dt)
        local_dt = dt.astimezone(tz)
        abbrev = get_timezone_abbreviation(timezone_name)
        return f"{local_dt.strftime('%Y-%m-%d')} {abbrev}"
    except:
        return dt.strftime('%Y-%m-%d')

def sync_from_google_sheets():
    """Sync data from Google Sheets if enabled"""
    if os.getenv('SYNC_ON_STARTUP') == 'true':
        try:
            logger.info("Starting Google Sheets sync on startup...")
            from sync_from_sheet import sync_all
            sync_all()
            logger.info("Google Sheets sync completed successfully")
        except Exception as e:
            logger.error(f"Google Sheets sync failed: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"  # type: ignore
    login_manager.login_message_category = "info"
    babel.init_app(app)

    # Initialize new backend services
    with app.app_context():
        # Initialize audit logger
        init_audit_logger(app)
        
        # Initialize job scheduler
        job_scheduler.init_app(app)
        
        # Start job scheduler in background
        try:
            job_scheduler.start()
            logger.info("Job scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start job scheduler: {e}")

        # Initialize WorkflowEngine (don't assign to app)
        workflow_engine = WorkflowEngine()
        
        # Sync from Google Sheets if enabled
        sync_from_google_sheets()

    # Register context processors for timezone utilities
    @app.context_processor
    def inject_timezone_utils():
        return {
            'get_user_timezone': get_user_timezone,
            'get_timezone_abbreviation': get_timezone_abbreviation,
            'format_datetime_with_timezone': format_datetime_with_timezone,
            'format_date_with_timezone': format_date_with_timezone,
            'get_current_time': get_current_time,
            'abs': abs
        }

    # Register custom Jinja2 filters
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string to Python object"""
        if not value:
            return []
        try:
            import json
            return json.loads(value)
        except:
            return []

    from routes.dashboard import bp as dashboard_bp
    from routes.cargo import bp as cargo_bp
    from routes.attachments import bp as attachments_bp
    from routes.bills import bp as bills_bp
    from routes.email_center import bp as email_bp
    from routes.users import bp as users_bp
    from routes.roles import bp as roles_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cargo_bp)
    app.register_blueprint(attachments_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    
    # Register new API blueprint
    app.register_blueprint(api)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard_home"))
        return redirect(url_for("users.login"))

    @app.route("/clear_session")
    def clear_session():
        """Clear session and redirect to login"""
        session.clear()
        return redirect(url_for("users.login"))

    @app.route("/set_locale/<lang_code>")
    def set_locale(lang_code):
        if lang_code not in app.config.get("BABEL_SUPPORTED_LOCALES", []):
            lang_code = app.config.get("BABEL_DEFAULT_LOCALE", "en")
        session["lang"] = lang_code
        refresh()
        ref = request.referrer or url_for("dashboard.dashboard_home")
        return redirect(ref)

    @app.route("/set_timezone", methods=['POST'])
    def set_timezone():
        data = request.get_json()
        timezone = data.get('timezone', 'America/Los_Angeles')
        
        # Validate timezone
        valid_timezones = [
            'America/Los_Angeles', 'America/New_York', 'America/Chicago', 
            'America/Denver', 'UTC', 'Asia/Shanghai', 'Asia/Tokyo', 
            'Europe/London', 'Europe/Paris'
        ]
        
        if timezone in valid_timezones:
            session['timezone'] = timezone
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid timezone'})

    @app.route("/detect_timezone", methods=['POST'])
    def detect_timezone():
        data = request.get_json()
        timezone = data.get('timezone', 'America/Los_Angeles')
        
        # Validate timezone
        valid_timezones = [
            'America/Los_Angeles', 'America/New_York', 'America/Chicago', 
            'America/Denver', 'UTC', 'Asia/Shanghai', 'Asia/Tokyo', 
            'Europe/London', 'Europe/Paris'
        ]
        
        if timezone in valid_timezones:
            session['timezone'] = timezone
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid timezone'})

    @app.route("/mawb-management")
    def mawb_management():
        if not current_user.is_authenticated:
            return redirect(url_for("users.login"))
        return render_template("mawb_management.html")

    @app.route("/workflow-management")
    def workflow_management():
        if not current_user.is_authenticated:
            return redirect(url_for("users.login"))
        return render_template("workflow_management.html")

    @app.route("/audit-log")
    def audit_log():
        if not current_user.is_authenticated:
            return redirect(url_for("users.login"))
        return render_template("audit_log.html")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")



