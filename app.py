from flask import Flask, request, session, redirect, url_for, jsonify
from flask_login import current_user
from flask_babel import refresh
from datetime import datetime
import pytz
import json

from config import Config
from extensions import db, migrate, login_manager, babel

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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"  # type: ignore
    login_manager.login_message_category = "info"
    babel.init_app(app)

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

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard_home"))
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
        detected_timezone = data.get('timezone', 'America/Los_Angeles')
        
        # Validate and map common timezones to our supported ones
        timezone_mapping = {
            'America/Los_Angeles': 'America/Los_Angeles',
            'America/New_York': 'America/New_York',
            'America/Chicago': 'America/Chicago',
            'America/Denver': 'America/Denver',
            'UTC': 'UTC',
            'Asia/Shanghai': 'Asia/Shanghai',
            'Asia/Tokyo': 'Asia/Tokyo',
            'Europe/London': 'Europe/London',
            'Europe/Paris': 'Europe/Paris'
        }
        
        # If detected timezone is not in our mapping, default to Los Angeles
        mapped_timezone = timezone_mapping.get(detected_timezone, 'America/Los_Angeles')
        session['timezone'] = mapped_timezone
        
        return jsonify({
            'success': True, 
            'timezone': mapped_timezone,
            'original_timezone': detected_timezone
        })

    return app

# Create the app instance
app = create_app()

# Make get_locale available to all templates
# app.jinja_env.globals['get_locale'] = get_locale

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



