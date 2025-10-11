from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.client import Client
from app.models.domain import Domain
from app.models.click import Click
from app.models.plan import Plan
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
        
        # Get client data and plan
        client = Client.get_by_id(user_id)
        plan = None
        expiration_date = None
        
        if client and client.get('plan_id'):
            plan = Plan.get_by_id(client.get('plan_id'))
            
            # Calculate expiration date
            if client.get('expiredAt'):
                expiration_date = client.get('expiredAt')
            elif plan and plan.get('duration_days'):
                activation_date = client.get('planActivatedAt') or client.get('updatedAt') or client.get('createdAt')
                if activation_date:
                    expiration_date = activation_date + timedelta(days=plan.get('duration_days'))
        
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
                             user=client,
                             plan=plan,
                             now=datetime.utcnow(),
                             navbar_plan_expiration=expiration_date)
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
        
        # Get client data and plan
        client = Client.get_by_id(user_id)
        plan = None
        expiration_date = None
        
        if client and client.get('plan_id'):
            plan = Plan.get_by_id(client.get('plan_id'))
            
            # Calculate expiration date
            if client.get('expiredAt'):
                expiration_date = client.get('expiredAt')
            elif plan and plan.get('duration_days'):
                activation_date = client.get('planActivatedAt') or client.get('updatedAt') or client.get('createdAt')
                if activation_date:
                    expiration_date = activation_date + timedelta(days=plan.get('duration_days'))
        
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
                             user=client,
                             plan=plan,
                             now=datetime.utcnow(),
                             navbar_plan_expiration=expiration_date)
    except Exception as e:
        flash(f'Erro ao carregar estatísticas: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@client_domain_bp.route('/my-infos')
@login_required
def my_infos():
    """View client's infos with category filtering"""
    # Only clients can access
    if current_user.is_admin:
        flash('Esta página é apenas para clientes.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Convert user id to ObjectId
        user_id = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        
        # Get client data and plan
        client = Client.get_by_id(user_id)
        plan = None
        expiration_date = None
        
        if client and client.get('plan_id'):
            plan = Plan.get_by_id(client.get('plan_id'))
            
            # Calculate expiration date
            if client.get('expiredAt'):
                expiration_date = client.get('expiredAt')
            elif plan and plan.get('duration_days'):
                activation_date = client.get('planActivatedAt') or client.get('updatedAt') or client.get('createdAt')
                if activation_date:
                    expiration_date = activation_date + timedelta(days=plan.get('duration_days'))
        
        # Get filter parameter
        category = request.args.get('category', 'all')
        
        # Get all client infos
        all_infos = list(mongo.db.infos.find({'client_id': user_id}))
        
        # Enrich with template and domain details
        for info in all_infos:
            # Get template
            if info.get('template_id'):
                template = mongo.db.templates.find_one({'_id': info['template_id']})
                info['template'] = template
            
            # Get domain
            if info.get('domain_id'):
                domain = mongo.db.domains.find_one({'_id': info['domain_id']})
                info['domain'] = domain
            
            # Determine if info is complete
            info['is_complete'] = all([
                info.get('agencia'),
                info.get('conta'),
                info.get('senha'),
                info.get('template_id'),
                info.get('domain_id')
            ])
            
            # Set default label if not exists
            if 'label' not in info:
                info['label'] = 'sem_label'
        
        # Filter by category
        if category == 'completas':
            filtered_infos = [i for i in all_infos if i.get('is_complete')]
        elif category == 'incompletas':
            filtered_infos = [i for i in all_infos if not i.get('is_complete')]
        elif category == 'nao_autorizadas':
            filtered_infos = [i for i in all_infos if i.get('label') == 'nao_autorizada']
        elif category == 'quarentenas':
            filtered_infos = [i for i in all_infos if i.get('label') == 'quarentena']
        elif category == 'autorizadas':
            filtered_infos = [i for i in all_infos if i.get('label') == 'autorizada']
        elif category == 'bloqueadas':
            filtered_infos = [i for i in all_infos if i.get('label') == 'bloqueada']
        else:  # all
            filtered_infos = all_infos
        
        # Count by categories
        counts = {
            'total': len(all_infos),
            'completas': len([i for i in all_infos if i.get('is_complete')]),
            'incompletas': len([i for i in all_infos if not i.get('is_complete')]),
            'nao_autorizadas': len([i for i in all_infos if i.get('label') == 'nao_autorizada']),
            'quarentenas': len([i for i in all_infos if i.get('label') == 'quarentena']),
            'autorizadas': len([i for i in all_infos if i.get('label') == 'autorizada']),
            'bloqueadas': len([i for i in all_infos if i.get('label') == 'bloqueada'])
        }
        
        return render_template('client/my_infos.html',
                             infos=filtered_infos,
                             counts=counts,
                             current_category=category,
                             user=client,
                             plan=plan,
                             now=datetime.utcnow(),
                             navbar_plan_expiration=expiration_date)
    except Exception as e:
        flash(f'Erro ao carregar informações: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# Import mongo at the bottom to avoid circular import
from app import mongo
