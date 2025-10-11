from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.client import Client
from app.models.domain import Domain
from app.models.click import Click
from bson.objectid import ObjectId
from datetime import datetime, timedelta

client_domain_bp = Blueprint('client_domain', __name__, url_prefix='/client')

@client_domain_bp.route('/my-domains')
@login_required
def my_domains():
    """View client's domains"""
    # Only clients can access
    if current_user.is_admin:
        flash('Esta página é apenas para clientes.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Convert user id to ObjectId
        user_id = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        
        # Get client domains
        client_domains = list(mongo.db.client_domains.find({'client_id': user_id}))
        
        # Enrich with domain details
        for cd in client_domains:
            if cd.get('domain_id'):
                domain = mongo.db.domains.find_one({'_id': cd['domain_id']})
                cd['domain'] = domain
                cd['full_domain'] = f"{cd['subdomain']}.{domain['name']}" if domain else cd['subdomain']
                
                # Get click count for this domain
                click_count = Click.get_domain_clicks(user_id, cd['domain_id'], days=30)
                cd['click_count'] = len(click_count)
        
        return render_template('client/my_domains.html', 
                             client_domains=client_domains,
                             user=current_user)
    except Exception as e:
        flash(f'Erro ao carregar domínios: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@client_domain_bp.route('/click-stats')
@login_required
def click_stats():
    """View click statistics"""
    # Only clients can access
    if current_user.is_admin:
        flash('Esta página é apenas para clientes.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Convert user id to ObjectId
        user_id = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        
        # Get filter parameters
        days = int(request.args.get('days', 30))
        domain_id = request.args.get('domain_id')
        
        # Get click statistics
        click_stats = Click.get_click_stats(user_id, days=days)
        total_clicks = Click.get_total_clicks(user_id, days=days)
        clicks_by_date = Click.get_clicks_by_date(user_id, days=days)
        
        # Enrich stats with domain information
        for stat in click_stats:
            if stat.get('domain_id'):
                domain = mongo.db.domains.find_one({'_id': stat['domain_id']})
                stat['domain_name'] = domain['name'] if domain else 'Desconhecido'
        
        # Get client domains for filter
        client_domains = list(mongo.db.client_domains.find({'client_id': user_id}))
        for cd in client_domains:
            if cd.get('domain_id'):
                domain = mongo.db.domains.find_one({'_id': cd['domain_id']})
                cd['domain'] = domain
        
        # If specific domain is selected, get detailed clicks
        detailed_clicks = []
        if domain_id:
            try:
                domain_id_obj = ObjectId(domain_id)
                detailed_clicks = Click.get_domain_clicks(user_id, domain_id_obj, days=days)
            except:
                pass
        
        return render_template('client/click_stats.html',
                             click_stats=click_stats,
                             total_clicks=total_clicks,
                             clicks_by_date=clicks_by_date,
                             client_domains=client_domains,
                             detailed_clicks=detailed_clicks,
                             selected_domain=domain_id,
                             days=days,
                             user=current_user)
    except Exception as e:
        flash(f'Erro ao carregar estatísticas: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# Import mongo at the bottom to avoid circular import
from app import mongo
