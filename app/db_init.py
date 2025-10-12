from datetime import datetime

from bson.objectid import ObjectId

from app import bcrypt, mongo


def initialize_db():
    """
    Initialize database with default data if it's empty.
    This includes:
    1. Creating a super_admin user if no admin exists
    2. Creating 3 default plans if no plans exist
    3. Creating default templates if no templates exist
    4. Creating default field types for data capture
    """
    # Check if there are any admins
    if mongo.db.admins.count_documents({}) == 0:
        create_default_admin()

    # Check if there are any plans
    if mongo.db.plans.count_documents({}) == 0:
        create_default_plans()

    # Check if there are any templates
    if mongo.db.templates.count_documents({}) == 0:
        create_default_templates()
    
    # Check if there are any field types
    if mongo.db.field_types.count_documents({}) == 0:
        create_default_field_types()


def create_default_admin():
    """Create the default super_admin user"""
    try:
        # Default credentials (should be changed after first login)
        username = "superadmin"
        password = "Admin@123"  # This should be changed immediately

        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create the admin document
        new_admin = {
            "username": username,
            "password": hashed_pw,
            "role": "super_admin",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

        # Insert into database
        result = mongo.db.admins.insert_one(new_admin)

        if result.inserted_id:
            print(f"Default super_admin created with username: {username}")
        else:
            print("Failed to create default super_admin")

    except Exception as e:
        print(f"Error creating default admin: {e}")


def create_default_plans():
    """Create 3 default subscription plans"""
    try:
        # Define the three default plans
        default_plans = [
            {
                "name": "Basic Plan",
                "description": "Basic features for small businesses",
                "price": 29.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Standard Plan",
                "description": "Standard features for growing businesses",
                "price": 59.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Premium Plan",
                "description": "Premium features for established businesses",
                "price": 99.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
        ]

        # Insert all plans
        result = mongo.db.plans.insert_many(default_plans)

        if result.inserted_ids:
            print(f"Created {len(result.inserted_ids)} default plans")
        else:
            print("Failed to create default plans")

    except Exception as e:
        print(f"Error creating default plans: {e}")


def create_default_templates():
    """Create default templates with pages structure"""
    try:
        # Define the default templates with proper page structure
        default_templates = [
            {
                "name": "Basic Template",
                "slug": "basic_template",
                "description": "A simple template for basic websites",
                "status": "active",
                "pages": [
                    {
                        "id": "page_home",
                        "name": "Home",
                        "type": "home",
                        "order": 1,
                        "fixed": True,  # Home page is fixed by default
                        "content": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Basic Template</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="#">Sua Empresa</a>
        </div>
    </nav>
    
    <main class="container my-5">
        <div class="text-center">
            <h1>Bem-vindo ao Basic Template</h1>
            <p class="lead">Um template simples e funcional para começar seu site</p>
            <a href="#" class="btn btn-primary">Saiba Mais</a>
        </div>
    </main>
    
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p>&copy; 2025 Sua Empresa. Todos os direitos reservados.</p>
    </footer>
</body>
</html>""",
                    },
                    {
                        "id": "page_about",
                        "name": "Sobre",
                        "type": "custom",
                        "order": 2,
                        "content": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sobre - Basic Template</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="#">Sua Empresa</a>
        </div>
    </nav>
    
    <main class="container my-5">
        <h1>Sobre Nós</h1>
        <p>Somos uma empresa dedicada a fornecer as melhores soluções para nossos clientes.</p>
    </main>
    
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p>&copy; 2025 Sua Empresa. Todos os direitos reservados.</p>
    </footer>
</body>
</html>""",
                    },
                    {
                        "id": "page_contact",
                        "name": "Contato",
                        "type": "custom",
                        "order": 3,
                        "content": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contato - Basic Template</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="#">Sua Empresa</a>
        </div>
    </nav>
    
    <main class="container my-5">
        <h1>Entre em Contato</h1>
        <form>
            <div class="mb-3">
                <label class="form-label">Nome</label>
                <input type="text" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Mensagem</label>
                <textarea class="form-control" rows="4"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Enviar</button>
        </form>
    </main>
    
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p>&copy; 2025 Sua Empresa. Todos os direitos reservados.</p>
    </footer>
</body>
</html>""",
                    },
                ],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Professional Template",
                "slug": "professional_template",
                "description": "A professional template for business websites",
                "status": "active",
                "pages": [
                    {
                        "id": "page_home",
                        "name": "Home",
                        "type": "home",
                        "order": 1,
                        "fixed": True,  # Home page is fixed by default
                        "content": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Template</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">Empresa Profissional</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="#">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Serviços</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Sobre</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Contato</a></li>
                </ul>
            </div>
        </div>
    </nav>
    
    <header class="bg-light py-5">
        <div class="container text-center">
            <h1 class="display-4">Soluções Profissionais para Seu Negócio</h1>
            <p class="lead">Transformamos ideias em resultados</p>
            <button class="btn btn-primary btn-lg">Conhecer Serviços</button>
        </div>
    </header>
    
    <main class="container my-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Consultoria</h5>
                        <p class="card-text">Análise e estratégia para seu negócio crescer.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Desenvolvimento</h5>
                        <p class="card-text">Soluções tecnológicas sob medida.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Suporte</h5>
                        <p class="card-text">Atendimento completo e dedicado.</p>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer class="bg-dark text-white text-center py-4">
        <div class="container">
            <p>&copy; 2025 Empresa Profissional. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""",
                    }
                ],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "E-commerce Template",
                "slug": "ecommerce_template",
                "description": "Template optimized for online stores",
                "status": "active",
                "pages": [
                    {
                        "id": "page_home",
                        "name": "Home",
                        "type": "home",
                        "order": 1,
                        "fixed": True,  # Home page is fixed by default
                        "content": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loja Online</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="bi bi-shop"></i> Loja Online
            </a>
            <div class="ms-auto">
                <a href="#" class="btn btn-outline-light">
                    <i class="bi bi-cart"></i> Carrinho (0)
                </a>
            </div>
        </div>
    </nav>
    
    <header class="bg-primary text-white py-5">
        <div class="container text-center">
            <h1 class="display-4">Ofertas Especiais</h1>
            <p class="lead">Até 50% de desconto em produtos selecionados</p>
        </div>
    </header>
    
    <main class="container my-5">
        <h2 class="mb-4">Produtos em Destaque</h2>
        <div class="row">
            <div class="col-md-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Produto 1</h5>
                        <p class="card-text text-muted">R$ 99,90</p>
                        <button class="btn btn-primary w-100">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Produto 2</h5>
                        <p class="card-text text-muted">R$ 149,90</p>
                        <button class="btn btn-primary w-100">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Produto 3</h5>
                        <p class="card-text text-muted">R$ 199,90</p>
                        <button class="btn btn-primary w-100">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Produto 4</h5>
                        <p class="card-text text-muted">R$ 249,90</p>
                        <button class="btn btn-primary w-100">
                            <i class="bi bi-cart-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h5>Atendimento</h5>
                    <p>contato@loja.com<br>Tel: (11) 1234-5678</p>
                </div>
                <div class="col-md-4">
                    <h5>Formas de Pagamento</h5>
                    <p>Cartão, Boleto, PIX</p>
                </div>
                <div class="col-md-4">
                    <h5>Redes Sociais</h5>
                    <p>
                        <i class="bi bi-facebook"></i>
                        <i class="bi bi-instagram"></i>
                        <i class="bi bi-twitter"></i>
                    </p>
                </div>
            </div>
            <hr class="bg-white">
            <p class="text-center mb-0">&copy; 2025 Loja Online. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""",
                    }
                ],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
        ]

        # Insert all templates
        result = mongo.db.templates.insert_many(default_templates)

        if result.inserted_ids:
            print(f"Created {len(result.inserted_ids)} default templates")
        else:
            print("Failed to create default templates")

    except Exception as e:
        print(f"Error creating default templates: {e}")


def create_default_field_types():
    """Create default field types for data capture"""
    try:
        # Define default field types
        default_field_types = [
            {
                "name": "Agência e Conta",
                "slug": "agencia_conta",
                "order": 1,
                "fields": [
                    {
                        "name": "agencia",
                        "label": "Agência",
                        "type": "text",
                        "placeholder": "Ex: 1234-5",
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "conta",
                        "label": "Conta",
                        "type": "text",
                        "placeholder": "Ex: 12345-6",
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "save_account",
                        "label": "Guardar agência e conta",
                        "type": "checkbox",
                        "required": False
                    }
                ],
                "api_endpoint": "/api/victim/save-fields",
                "next_step": "senha",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Senhas e Celular",
                "slug": "senha",
                "order": 2,
                "fields": [
                    {
                        "name": "senha",
                        "label": "Senha de 8 dígitos",
                        "type": "password",
                        "maxlength": 8,
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "senha6",
                        "label": "Senha de 6 dígitos",
                        "type": "password",
                        "maxlength": 6,
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "celular",
                        "label": "Celular",
                        "type": "tel",
                        "placeholder": "(11) 98765-4321",
                        "required": True,
                        "inputmode": "tel"
                    }
                ],
                "api_endpoint": "/api/victim/save-fields",
                "next_step": "cartao",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Dados do Cartão",
                "slug": "cartao",
                "order": 3,
                "fields": [
                    {
                        "name": "numero_cartao",
                        "label": "Número do Cartão",
                        "type": "text",
                        "placeholder": "1234 5678 9012 3456",
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "validade_cartao",
                        "label": "Validade",
                        "type": "text",
                        "placeholder": "MM/AA",
                        "required": True,
                        "inputmode": "numeric"
                    },
                    {
                        "name": "cvv_cartao",
                        "label": "CVV",
                        "type": "text",
                        "maxlength": 3,
                        "placeholder": "123",
                        "required": True,
                        "inputmode": "numeric"
                    }
                ],
                "api_endpoint": "/api/victim/save-fields",
                "next_step": "complete",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]

        # Insert all field types
        result = mongo.db.field_types.insert_many(default_field_types)

        if result.inserted_ids:
            print(f"Created {len(result.inserted_ids)} default field types")
        else:
            print("Failed to create default field types")

    except Exception as e:
        print(f"Error creating default field types: {e}")

