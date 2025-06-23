from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from models import Cargo
from flask_babel import _
from datetime import datetime
import pytz

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def dashboard_home():
    """
    Displays:
      - 当前业务列表 (正在处理/已完成)
      - 今日提醒统计 (LFD 截止、未付费、查验/放行/提货)
      - 业务状态分布图 (饼图/条形图)
    """
    # Get sort parameter from request
    sort_by = request.args.get('sort', 'date_added')
    
    # Get all cargos (only unarchived)
    all_cargos = Cargo.query.filter_by(is_archived=False).all()
    
    # Get user's timezone from session
    user_timezone = session.get('timezone', 'America/Los_Angeles')
    tz = pytz.timezone(user_timezone)
    now = datetime.now(tz)
    
    # Apply sorting based on the sort parameter
    if sort_by == 'date_added':
        # Date added (default) with newest on top
        all_cargos.sort(key=lambda x: x.created_at or datetime.min.replace(tzinfo=pytz.UTC), reverse=True)
    elif sort_by == 'eta_soonest':
        # ETA with soonest upcoming on top, already arrived at bottom
        def eta_sort_key(x):
            if x.status == 'Completed':
                return (1, datetime.max.replace(tzinfo=pytz.UTC))  # Completed at bottom
            
            if not x.eta:
                return (0, datetime.max.replace(tzinfo=pytz.UTC))  # No ETA at bottom
            
            # Make ETA timezone-aware if it isn't
            eta = x.eta
            if eta.tzinfo is None:
                # Treat naive dates as being in the user's timezone
                eta = tz.localize(eta)
            
            # Convert to user timezone for comparison
            eta_user_tz = eta.astimezone(tz)
            
            # Past ETAs go to bottom, future ETAs to top
            if eta_user_tz < now:
                return (1, eta_user_tz)  # Past ETAs at bottom
            else:
                return (0, eta_user_tz)  # Future ETAs at top
        
        all_cargos.sort(key=eta_sort_key)
    elif sort_by == 'eta_latest':
        # ETA purely by date latest on top
        def eta_latest_sort_key(x):
            if not x.eta:
                return datetime.min.replace(tzinfo=pytz.UTC)
            
            eta = x.eta
            if eta.tzinfo is None:
                # Treat naive dates as being in the user's timezone
                eta = tz.localize(eta)
            return eta
        
        all_cargos.sort(key=eta_latest_sort_key, reverse=True)
    elif sort_by == 'lfd_overdue':
        # Date until LFD with most overdue on top, soonest due, completed oldest at bottom
        def lfd_sort_key(x):
            if x.status == 'Completed':
                # For completed, oldest LFD at bottom
                if not x.lfd_date:
                    return (1, datetime.max.replace(tzinfo=pytz.UTC))
                lfd = x.lfd_date
                if lfd.tzinfo is None:
                    # Treat naive dates as being in the user's timezone
                    lfd = tz.localize(lfd)
                return (1, lfd.astimezone(tz))
            
            if not x.lfd_date:
                return (0, datetime.max.replace(tzinfo=pytz.UTC))  # No LFD at bottom
            
            # Make LFD timezone-aware if it isn't
            lfd = x.lfd_date
            if lfd.tzinfo is None:
                # Treat naive dates as being in the user's timezone
                lfd = tz.localize(lfd)
            
            # Convert to user timezone for comparison
            lfd_user_tz = lfd.astimezone(tz)
            
            # Calculate days until LFD (negative = overdue)
            days_until_lfd = (lfd_user_tz - now).days
            
            # Most overdue (negative days) should be at top
            # Soonest due (positive days) should be next
            return (0, -days_until_lfd)  # Negative so overdue appears first
        
        all_cargos.sort(key=lfd_sort_key)
    
    return render_template('dashboard.html', cargos=all_cargos, current_sort=sort_by)
