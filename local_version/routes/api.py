from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
from models_new import (
    db, MAWB, HAWB, MAWBEvent, HAWBEvent, Carrier, FileType, 
    WorkflowStep, MAWBWorkflow, ScheduledJob, AuditLog, User,
    Attachment, Bill
)

api = Blueprint('api', __name__, url_prefix='/api/v1')

# ============================================================================
# MAWB (Master Air Waybill) API Endpoints
# ============================================================================

@api.route('/mawbs', methods=['GET'])
@login_required
def get_mawbs():
    """Get all MAWBs with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    carrier_id = request.args.get('carrier_id', type=int)
    search = request.args.get('search')
    
    query = MAWB.query
    
    if status:
        query = query.filter(MAWB.status == status)
    if carrier_id:
        query = query.filter(MAWB.carrier_id == carrier_id)
    if search:
        query = query.filter(
            MAWB.mawb_number.ilike(f'%{search}%') |
            MAWB.consignee.ilike(f'%{search}%') |
            MAWB.shipper.ilike(f'%{search}%')
        )
    
    mawbs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'mawbs': [{
            'id': mawb.id,
            'mawb_number': mawb.mawb_number,
            'origin_port': mawb.origin_port,
            'dest_port': mawb.dest_port,
            'carrier': mawb.carrier.name if mawb.carrier else None,
            'eta': mawb.eta.isoformat() if mawb.eta else None,
            'etd': mawb.etd.isoformat() if mawb.etd else None,
            'lfd': mawb.lfd.isoformat() if mawb.lfd else None,
            'status': mawb.status,
            'progress': mawb.progress,
            'consignee': mawb.consignee,
            'shipper': mawb.shipper,
            'pieces': mawb.pieces,
            'weight': float(mawb.weight) if mawb.weight else None,
            'volume': float(mawb.volume) if mawb.volume else None,
            'created_at': mawb.created_at.isoformat(),
            'is_overdue': mawb.is_overdue,
            'time_until_lfd': mawb.time_until_lfd
        } for mawb in mawbs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': mawbs.total,
            'pages': mawbs.pages
        }
    })

@api.route('/mawbs', methods=['POST'])
@login_required
def create_mawb():
    """Create a new MAWB"""
    data = request.get_json()
    
    try:
        mawb = MAWB(
            mawb_number=data['mawb_number'],
            origin_port=data.get('origin_port'),
            dest_port=data.get('dest_port'),
            carrier_id=data.get('carrier_id'),
            eta=datetime.fromisoformat(data['eta']) if data.get('eta') else None,
            etd=datetime.fromisoformat(data['etd']) if data.get('etd') else None,
            lfd=datetime.fromisoformat(data['lfd']) if data.get('lfd') else None,
            consignee=data.get('consignee'),
            shipper=data.get('shipper'),
            pieces=data.get('pieces'),
            weight=data.get('weight'),
            volume=data.get('volume'),
            description=data.get('description'),
            notes=data.get('notes'),
            created_by=current_user.id
        )
        
        db.session.add(mawb)
        db.session.commit()
        
        # Create initial workflow
        if hasattr(current_app, 'workflow_engine'):
            current_app.workflow_engine.create_workflow(mawb.id)
        
        return jsonify({
            'success': True,
            'mawb_id': mawb.id,
            'message': 'MAWB created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api.route('/mawbs/<int:mawb_id>', methods=['GET'])
@login_required
def get_mawb(mawb_id):
    """Get a specific MAWB with details"""
    mawb = MAWB.query.get_or_404(mawb_id)
    
    return jsonify({
        'id': mawb.id,
        'mawb_number': mawb.mawb_number,
        'origin_port': mawb.origin_port,
        'dest_port': mawb.dest_port,
        'carrier': {
            'id': mawb.carrier.id,
            'name': mawb.carrier.name,
            'code': mawb.carrier.code
        } if mawb.carrier else None,
        'eta': mawb.eta.isoformat() if mawb.eta else None,
        'etd': mawb.etd.isoformat() if mawb.etd else None,
        'lfd': mawb.lfd.isoformat() if mawb.lfd else None,
        'status': mawb.status,
        'progress': mawb.progress,
        'consignee': mawb.consignee,
        'shipper': mawb.shipper,
        'pieces': mawb.pieces,
        'weight': float(mawb.weight) if mawb.weight else None,
        'volume': float(mawb.volume) if mawb.volume else None,
        'description': mawb.description,
        'notes': mawb.notes,
        'created_at': mawb.created_at.isoformat(),
        'updated_at': mawb.updated_at.isoformat(),
        'is_overdue': mawb.is_overdue,
        'time_until_lfd': mawb.time_until_lfd,
        'hawbs': [{
            'id': hawb.id,
            'hawb_number': hawb.hawb_number,
            'consignee': hawb.consignee,
            'shipper': hawb.shipper,
            'pieces': hawb.pieces,
            'weight': float(hawb.weight) if hawb.weight else None,
            'volume': float(hawb.volume) if hawb.volume else None,
            'status': hawb.status
        } for hawb in mawb.hawbs],
        'recent_events': [{
            'id': event.id,
            'event_type': event.event_type,
            'event_time': event.event_time.isoformat(),
            'details': event.details,
            'created_by': event.user.username if event.user else None
        } for event in mawb.events[:10]]  # Last 10 events
    })

@api.route('/mawbs/<int:mawb_id>', methods=['PUT'])
@login_required
def update_mawb(mawb_id):
    """Update a MAWB"""
    mawb = MAWB.query.get_or_404(mawb_id)
    data = request.get_json()
    
    try:
        for field, value in data.items():
            if hasattr(mawb, field):
                if field in ['eta', 'etd', 'lfd'] and value:
                    setattr(mawb, field, datetime.fromisoformat(value))
                else:
                    setattr(mawb, field, value)
        
        mawb.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'MAWB updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api.route('/mawbs/<int:mawb_id>/events', methods=['POST'])
@login_required
def add_mawb_event(mawb_id):
    """Add an event to a MAWB"""
    mawb = MAWB.query.get_or_404(mawb_id)
    data = request.get_json()
    
    try:
        event = MAWBEvent(
            mawb_id=mawb_id,
            event_type=data['event_type'],
            event_time=datetime.fromisoformat(data['event_time']) if data.get('event_time') else datetime.utcnow(),
            details=data.get('details'),
            created_by=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'event_id': event.id,
            'message': 'Event added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================================================
# HAWB (House Air Waybill) API Endpoints
# ============================================================================

@api.route('/hawbs', methods=['GET'])
@login_required
def get_hawbs():
    """Get all HAWBs with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    mawb_id = request.args.get('mawb_id', type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = HAWB.query
    
    if mawb_id:
        query = query.filter(HAWB.mawb_id == mawb_id)
    if status:
        query = query.filter(HAWB.status == status)
    if search:
        query = query.filter(
            HAWB.hawb_number.ilike(f'%{search}%') |
            HAWB.consignee.ilike(f'%{search}%') |
            HAWB.shipper.ilike(f'%{search}%')
        )
    
    hawbs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'hawbs': [{
            'id': hawb.id,
            'hawb_number': hawb.hawb_number,
            'mawb_number': hawb.mawb.mawb_number,
            'consignee': hawb.consignee,
            'shipper': hawb.shipper,
            'pieces': hawb.pieces,
            'weight': float(hawb.weight) if hawb.weight else None,
            'volume': float(hawb.volume) if hawb.volume else None,
            'description': hawb.description,
            'status': hawb.status,
            'created_at': hawb.created_at.isoformat()
        } for hawb in hawbs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': hawbs.total,
            'pages': hawbs.pages
        }
    })

@api.route('/hawbs', methods=['POST'])
@login_required
def create_hawb():
    """Create a new HAWB"""
    data = request.get_json()
    
    try:
        hawb = HAWB(
            hawb_number=data['hawb_number'],
            mawb_id=data['mawb_id'],
            consignee=data.get('consignee'),
            shipper=data.get('shipper'),
            pieces=data.get('pieces'),
            weight=data.get('weight'),
            volume=data.get('volume'),
            description=data.get('description')
        )
        
        db.session.add(hawb)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'hawb_id': hawb.id,
            'message': 'HAWB created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================================================
# Workflow API Endpoints
# ============================================================================

@api.route('/workflows/mawb/<int:mawb_id>', methods=['GET'])
@login_required
def get_mawb_workflow(mawb_id):
    """Get workflow for a MAWB"""
    workflow = MAWBWorkflow.query.filter_by(mawb_id=mawb_id, is_active=True).first()
    
    if not workflow:
        return jsonify({
            'success': False,
            'error': 'No active workflow found'
        }), 404
    
    # Get all workflow steps
    steps = WorkflowStep.query.filter_by(is_active=True).all()
    
    return jsonify({
        'workflow': {
            'id': workflow.id,
            'current_step': workflow.current_step,
            'started_at': workflow.started_at.isoformat(),
            'updated_at': workflow.updated_at.isoformat(),
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'is_completed': workflow.is_completed
        },
        'steps': [{
            'code': step.code,
            'name': step.name,
            'description': step.description,
            'next_step': step.next_step,
            'is_current': step.code == workflow.current_step,
            'is_completed': step.code in [s.code for s in steps[:steps.index(next(s for s in steps if s.code == workflow.current_step))]] if workflow.current_step in [s.code for s in steps] else False
        } for step in steps]
    })

@api.route('/workflows/mawb/<int:mawb_id>/advance', methods=['POST'])
@login_required
def advance_workflow(mawb_id):
    """Advance workflow to next step"""
    if not hasattr(current_app, 'workflow_engine'):
        return jsonify({
            'success': False,
            'error': 'Workflow engine not available'
        }), 500
    
    try:
        workflow = current_app.workflow_engine.advance_workflow(
            mawb_id=mawb_id,
            user_id=current_user.id,
            event_details=request.get_json()
        )
        
        return jsonify({
            'success': True,
            'workflow_id': workflow.id,
            'current_step': workflow.current_step,
            'message': 'Workflow advanced successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================================================
# Scheduled Jobs API Endpoints
# ============================================================================

@api.route('/jobs', methods=['GET'])
@login_required
def get_scheduled_jobs():
    """Get scheduled jobs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    job_type = request.args.get('job_type')
    
    query = ScheduledJob.query
    
    if status:
        query = query.filter(ScheduledJob.status == status)
    if job_type:
        query = query.filter(ScheduledJob.job_type == job_type)
    
    jobs = query.order_by(ScheduledJob.run_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'jobs': [{
            'id': job.id,
            'job_type': job.job_type,
            'run_at': job.run_at.isoformat(),
            'status': job.status,
            'attempts': job.attempts,
            'max_attempts': job.max_attempts,
            'payload': job.payload,
            'created_at': job.created_at.isoformat(),
            'mawb_number': job.mawb.mawb_number if job.mawb else None,
            'hawb_number': job.hawb.hawb_number if job.hawb else None
        } for job in jobs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': jobs.total,
            'pages': jobs.pages
        }
    })

@api.route('/jobs/<int:job_id>/retry', methods=['POST'])
@login_required
def retry_job(job_id):
    """Retry a failed job"""
    job = ScheduledJob.query.get_or_404(job_id)
    
    if job.status != 'failed':
        return jsonify({
            'success': False,
            'error': 'Job is not in failed status'
        }), 400
    
    if not job.can_retry:
        return jsonify({
            'success': False,
            'error': 'Job has exceeded maximum retry attempts'
        }), 400
    
    try:
        job.status = 'pending'
        job.attempts = 0
        job.run_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job queued for retry'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================================================
# Utility API Endpoints
# ============================================================================

@api.route('/carriers', methods=['GET'])
@login_required
def get_carriers():
    """Get all carriers"""
    carriers = Carrier.query.filter_by(is_active=True).all()
    
    return jsonify({
        'carriers': [{
            'id': carrier.id,
            'name': carrier.name,
            'code': carrier.code
        } for carrier in carriers]
    })

@api.route('/file-types', methods=['GET'])
@login_required
def get_file_types():
    """Get all file types"""
    file_types = FileType.query.filter_by(is_active=True).all()
    
    return jsonify({
        'file_types': [{
            'id': file_type.id,
            'key': file_type.key,
            'description': file_type.description
        } for file_type in file_types]
    })

@api.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    total_mawbs = MAWB.query.count()
    active_mawbs = MAWB.query.filter(MAWB.status == 'in_progress').count()
    overdue_mawbs = MAWB.query.filter(MAWB.lfd < datetime.now().date()).count()
    completed_mawbs = MAWB.query.filter(MAWB.status == 'complete').count()
    
    # Recent events
    recent_events = MAWBEvent.query.order_by(MAWBEvent.event_time.desc()).limit(10).all()
    
    # Pending jobs
    pending_jobs = ScheduledJob.query.filter(ScheduledJob.status == 'pending').count()
    
    return jsonify({
        'stats': {
            'total_mawbs': total_mawbs,
            'active_mawbs': active_mawbs,
            'overdue_mawbs': overdue_mawbs,
            'completed_mawbs': completed_mawbs,
            'pending_jobs': pending_jobs
        },
        'recent_events': [{
            'id': event.id,
            'mawb_number': event.mawb.mawb_number,
            'event_type': event.event_type,
            'event_time': event.event_time.isoformat(),
            'details': event.details
        } for event in recent_events]
    })

@api.route('/audit-log', methods=['GET'])
@login_required
def get_audit_log():
    """Get audit log entries"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    table_name = request.args.get('table_name')
    action = request.args.get('action')
    
    query = AuditLog.query
    
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.changed_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'table_name': log.table_name,
            'record_id': log.record_id,
            'action': log.action,
            'old_values': log.old_values,
            'new_values': log.new_values,
            'changed_by': log.user.username if log.user else None,
            'changed_at': log.changed_at.isoformat()
        } for log in logs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': logs.total,
            'pages': logs.pages
        }
    })

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500 