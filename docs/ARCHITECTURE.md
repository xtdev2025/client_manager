# 🏗️ Arquitetura do Client Manager

## Visão Geral

O Client Manager segue uma arquitetura **MVC (Model-View-Controller)** aprimorada com camadas adicionais para separação de responsabilidades, incluindo Services para lógica de negócio e Schemas para validação de dados.

### Princípios Arquiteturais

- **Separação de Responsabilidades**: Cada camada tem um propósito específico
- **Reutilização**: Services podem ser usados por múltiplos controllers
- **Testabilidade**: Componentes isolados facilitam testes
- **Type Safety**: Type hints em todo o código Python
- **Validação Centralizada**: Schemas Pydantic para validação consistente
- **Segurança de Credenciais**: Uso de variáveis de ambiente para todas as credenciais

### Nota Importante sobre Credenciais

⚠️ **NUNCA** use credenciais hardcoded no código. Todos os exemplos neste documento usam `os.getenv()` para variáveis de ambiente. Configure suas credenciais em:

- Arquivo `.env` para desenvolvimento
- Variáveis de ambiente do sistema para produção
- Secrets do CI/CD para testes automatizados

## Camadas da Aplicação

### 1. Models (`app/models/`)

Responsável pela interação com o banco de dados MongoDB e lógica de dados.

**Modelos Disponíveis:**

- `user.py` - Classe base User
- `admin.py` - Modelo Admin (herda de User)
- `client.py` - Modelo Client (herda de User)
- `plan.py` - Modelo de planos de assinatura
- `template.py` - Modelo de templates personalizados
- `domain.py` - Modelo de domínios
- `info.py` - Modelo de informações bancárias
- `login_log.py` - Modelo de logs de login
- `click.py` - Modelo de rastreamento de cliques

**Características:**

- Definição das estruturas de dados
- Operações CRUD básicas
- Validações de negócio relacionadas aos dados
- Type hints em todos os métodos
- Métodos estáticos para operações no banco

**Exemplo:**

```python
from typing import Tuple, Optional, Dict, Any
from bson.objectid import ObjectId

class Plan:
    @staticmethod
    def create(name: str, description: str, price: float, 
               duration_days: int) -> Tuple[bool, str]:
        """Create a new plan"""
        try:
            new_plan = {
                'name': name,
                'description': description,
                'price': price,
                'duration_days': duration_days,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            result = mongo.db.plans.insert_one(new_plan)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        if isinstance(plan_id, str):
            plan_id = ObjectId(plan_id)
        return mongo.db.plans.find_one({'_id': plan_id})
```

### 2. Services (`app/services/`)

Camada de lógica de negócio, separada dos controllers.

**Serviços Disponíveis:**

#### AuthService

- Autenticação de usuários
- Validação de credenciais
- Registro de tentativas de login

```python
from app.services.auth_service import AuthService

# Autenticar usuário
success, user, error = AuthService.authenticate_user(username, password)

# Validar dados de registro
valid, error = AuthService.validate_registration_data(username, password)
```

#### ClientService

- Validação de dados de clientes
- Enriquecimento de dados (com planos, templates)
- Verificação de expiração de planos

```python
from app.services.client_service import ClientService

# Validar dados do cliente
valid, error = ClientService.validate_client_data(
    username, password, plan_id, status
)

# Obter cliente com detalhes
client = ClientService.get_client_with_details(client_id)
```

#### AuditService

- Registro de operações sensíveis
- Rastreabilidade de ações
- Logs de auditoria

```python
from app.services.audit_service import AuditService

# Registrar ação de admin
AuditService.log_admin_action('create', admin_id, {'username': os.getenv('ADMIN_USERNAME', 'admin_user')})

# Obter logs recentes
logs = AuditService.get_recent_logs(limit=50, entity_type='admin')
```

### 3. Schemas (`app/schemas/`)

Validação de dados usando Pydantic.

**Schemas Disponíveis:**

- `UserCreateSchema` - Criação de usuários
- `AdminCreateSchema` - Criação de admins
- `ClientCreateSchema` - Criação de clientes
- `PlanCreateSchema` - Criação de planos
- `DomainCreateSchema` - Criação de domínios

```python
from app.schemas.user_schemas import ClientCreateSchema
from pydantic import ValidationError

try:
    validated = ClientCreateSchema(
        username='testuser',
        password=os.getenv('DEFAULT_PASSWORD', 'secure_password'),
        plan_id='507f1f77bcf86cd799439011',
        status='active'
    )
    # Dados válidos, prosseguir
except ValidationError as e:
    # Tratar erros de validação
    print(e.errors())
```

### 4. Controllers (`app/controllers/`)

Processamento de requisições HTTP e orquestração entre services/models.

**Controllers Disponíveis (Blueprints):**

- `auth.py` - Autenticação (login/logout/register)
- `admin.py` - Gestão de administradores
- `client.py` - Gestão de clientes
- `plan.py` - Gestão de planos
- `template.py` - Gestão de templates
- `domain.py` - Gestão de domínios
- `info.py` - Gestão de informações bancárias
- `main.py` - Rotas principais (index, dashboard)
- `public_template.py` - Renderização pública de templates

**Responsabilidades:**

- Receber requisições HTTP
- Validar entrada usando schemas
- Chamar services para lógica de negócio
- Chamar models para persistência
- Registrar ações de auditoria
- Retornar respostas HTTP ou renderizar templates

**Exemplo:**

```python
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from app.decorators import admin_required
from app.services.audit_service import AuditService
from app.models.plan import Plan

plan_bp = Blueprint('plan', __name__, url_prefix='/plans')

@plan_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create_plan():
    """Create a new plan"""
    data = request.form.to_dict()
    
    # Validar com pydantic (opcional)
    # valid, validated_data, error = validate_plan_create(data)
    
    # Criar usando model
    success, result = Plan.create(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        duration_days=int(data['duration_days'])
    )
    
    # Auditar ação
    if success:
        AuditService.log_action(
            action='plan_create',
            target_type='plan',
            target_id=result,
            details=data
        )
        flash('Plano criado com sucesso!', 'success')
    else:
        flash(f'Erro ao criar plano: {result}', 'danger')
    
    return redirect(url_for('plan.list_plans'))
```

### 5. Views (`app/views/`)

Renderização de templates HTML com dados preparados.

**Views Disponíveis:**

- `base_view.py` - Classe base para todas as views
- `auth_view.py` - Views de autenticação
- `admin_view.py` - Views de administradores
- `client_view.py` - Views de clientes
- `plan_view.py` - Views de planos
- `template_view.py` - Views de templates
- `domain_view.py` - Views de domínios
- `info_view.py` - Views de informações bancárias
- `main_view.py` - Views principais (dashboard)
- `client_domain_view.py` - Views de domínios de clientes

**Responsabilidades:**

- Preparar dados para templates
- Renderizar templates Jinja2
- Aplicar formatações e transformações
- Encapsular lógica de apresentação

### 6. Templates (`app/templates/`)

Interface visual HTML com Jinja2.

**Estrutura de Templates:**

```
templates/
├── layout.html              # Layout base
├── navbar.html              # Navegação
├── index.html               # Página inicial
├── dashboard.html           # Dashboard base
├── client_layout.html       # Layout para clientes
├── auth/                    # Templates de autenticação
│   ├── login.html
│   ├── register.html
│   └── register_admin.html
├── dashboard/               # Dashboards específicos
│   ├── admin.html
│   └── client.html
├── admins/                  # CRUD de admins
├── clients/                 # CRUD de clientes
├── plans/                   # CRUD de planos
├── templates/               # CRUD de templates
├── domains/                 # CRUD de domínios
├── infos/                   # CRUD de informações
└── public/                  # Templates públicos
    ├── template_page.html
    ├── template_page_simple.html
    └── submit_success.html
```

### 7. Utils (`app/utils/`)

Utilitários e helpers da aplicação.

**Disponíveis:**

- `user_loader.py` - Flask-Login user loader
- `validators.py` - Validadores customizados

### 8. Scripts (`scripts/`)

Scripts utilitários para administração do sistema.

**Scripts Disponíveis:**

- `create_superadmin.py` - Criar super admin manualmente via CLI
- `setup.py` - Setup automatizado do projeto (instala dependências, configura ambiente)

## Fluxo de uma Requisição

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Usuário faz requisição HTTP (GET/POST)                  │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Controller recebe a requisição (Blueprint)              │
│    - Verifica autenticação (@login_required)                │
│    - Verifica permissões (@admin_required, etc)             │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Controller valida dados de entrada                      │
│    - Schemas Pydantic (opcional)                            │
│    - Validações customizadas                                │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Controller chama Service (se necessário)                │
│    - Lógica de negócio                                      │
│    - Validações complexas                                   │
│    - Enriquecimento de dados                                │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Service/Controller chama Model                          │
│    - Operações CRUD                                         │
│    - Interação com MongoDB                                  │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Model interage com MongoDB                              │
│    - PyMongo operations                                     │
│    - Queries, inserts, updates, deletes                     │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Controller registra auditoria (operações sensíveis)     │
│    - AuditService.log_action()                              │
│    - Logs de segurança                                      │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Controller prepara resposta                             │
│    - Chama View (se renderização HTML)                      │
│    - Ou retorna JSON (APIs)                                 │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. View renderiza template Jinja2 (se HTML)                │
│    - Passa dados para template                              │
│    - Template herda de layout base                          │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Resposta HTTP retorna ao usuário                       │
│     - HTML renderizado ou JSON                              │
│     - Status code apropriado                                │
│     - Headers e cookies                                     │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo Prático: Criar um Cliente

1. **Usuário** acessa `/clients/create` (GET) → visualiza formulário
2. **Usuário** preenche e submete formulário (POST)
3. **Controller** (`client.py`) recebe requisição
4. **Controller** valida permissões (`@admin_required`)
5. **Controller** valida dados (schema ou manualmente)
6. **Service** (`ClientService`) valida regras de negócio
7. **Model** (`Client`) cria registro no MongoDB
8. **Service** retorna sucesso/erro
9. **Controller** registra log de auditoria
10. **Controller** redireciona com mensagem flash
11. **View** renderiza página de listagem
12. **Template** mostra lista atualizada com novo cliente

## Segurança

### Autenticação e Autorização

**Flask-Login:**

- Gerenciamento de sessões de usuário
- User loader para recuperar usuário da sessão
- Proteção de rotas com `@login_required`

**Decoradores de Permissão:**

```python
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Require admin or super_admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role not in ['admin', 'super_admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Require super_admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != 'super_admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

### Hashing de Senhas

**Flask-Bcrypt:**

- Hash seguro de senhas
- Verificação de senhas
- Salt automático

```python
from app import bcrypt

# Criar hash
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

# Verificar senha
is_valid = bcrypt.check_password_hash(hashed_password, password)
```

### Rate Limiting

Proteção contra força bruta e abuso (Flask-Limiter):

```python
from app import limiter

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Máximo 10 tentativas de login por minuto por IP"""
    pass
```

### Auditoria

Todas as operações sensíveis são registradas:

```python
from app.services.audit_service import AuditService

# Registrar ação
AuditService.log_action(
    action='admin_create',
    target_type='admin',
    target_id=admin_id,
    details={'username': 'newadmin', 'role': 'admin'},
    user_id=current_user.id  # opcional
)

# Obter logs recentes
logs = AuditService.get_recent_logs(limit=50)

# Filtrar por tipo
logs = AuditService.get_logs_by_type('admin', limit=100)
```

### CSRF Protection

**Flask-WTF:**

- Proteção automática contra CSRF
- Tokens em formulários
- Validação automática

### Type Safety

Type hints em todo o código para segurança de tipos:

```python
from typing import Tuple, Optional, Dict, Any, List

def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    # Implementation with type safety
    pass

def list_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List all items with optional filters"""
    # Implementation
    pass
```

## Testes

### Estrutura

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures e configuração pytest
├── unit/                          # Testes unitários
│   ├── __init__.py
│   ├── test_auth_service.py      # Testes do AuthService
│   ├── test_client_service.py    # Testes do ClientService
│   └── test_audit_service.py     # Testes do AuditService
└── integration/                   # Testes de integração
    ├── __init__.py
    ├── test_auth_routes.py       # Testes de rotas de autenticação
    └── test_plan_routes.py       # Testes de rotas de planos
```

### Configuração (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Fixtures (conftest.py)

```python
import pytest
from app import create_app, mongo

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Login and return headers
    pass
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Teste específico
pytest tests/unit/test_auth_service.py

# Verboso com detalhes
pytest -v -s

# Parar no primeiro erro
pytest -x
```

### Exemplo de Teste Unitário

```python
import pytest
from app.services.auth_service import AuthService

def test_validate_registration_data_valid():
    """Test validation with valid data"""
    valid, error = AuthService.validate_registration_data(
        username=os.getenv('TEST_USERNAME', 'test_user'),
        password=os.getenv('TEST_SECURE_PASSWORD', 'SecurePass123!')
    )
    assert valid is True
    assert error is None

def test_validate_registration_data_short_password():
    """Test validation with short password"""
    valid, error = AuthService.validate_registration_data(
        username=os.getenv('TEST_USERNAME', 'test_user'),
        password='123'
    )
    assert valid is False
    assert 'Password must be at least' in error
```

### Exemplo de Teste de Integração

```python
def test_login_success(client):
    """Test successful login"""
    response = client.post('/auth/login', data={
        'username': os.getenv('TEST_USERNAME', 'test_user'),
        'password': os.getenv('TEST_PASSWORD', 'test_pass')
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', data={
        'username': os.getenv('TEST_USERNAME', 'test_user'),
        'password': 'invalid_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data
```

## Boas Práticas

### Controllers

✅ **Fazer:**

- Manter lógica mínima
- Delegar para services
- Validar entrada com schemas
- Registrar ações sensíveis

❌ **Evitar:**

- Lógica de negócio complexa
- Acesso direto ao banco
- Validações complexas inline

### Services

✅ **Fazer:**

- Implementar lógica de negócio
- Reutilizar entre controllers
- Retornar tuplas (success, result/error)
- Usar type hints

❌ **Evitar:**

- Acesso direto ao request
- Renderização de templates
- Lógica de apresentação

### Models

✅ **Fazer:**

- Operações CRUD básicas
- Validações de dados
- Conversões de tipos
- Type hints

❌ **Evitar:**

- Lógica de negócio complexa
- Validações de formulários
- Processamento de requisições

## Extensibilidade

### Adicionar Novo Endpoint

**Processo Passo a Passo:**

1. **Schema** (opcional) - Criar schema de validação em `app/schemas/`
2. **Service** (opcional) - Implementar service em `app/services/`
3. **Model** - Criar/atualizar método no model em `app/models/`
4. **Controller** - Implementar route no controller em `app/controllers/`
5. **View** - Criar view em `app/views/` (se necessário)
6. **Template** - Criar template em `app/templates/`
7. **Testes** - Adicionar testes em `tests/`

### Exemplo Completo: Feature de Notificações

**1. Schema (`app/schemas/notification_schemas.py`):**

```python
from pydantic import BaseModel, Field
from typing import Optional

class NotificationCreateSchema(BaseModel):
    """Schema for creating notifications"""
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)
    user_id: str = Field(...)
    type: str = Field(default='info')  # info, warning, error, success
    read: bool = Field(default=False)
```

**2. Service (`app/services/notification_service.py`):**

```python
from typing import Tuple, Optional, Dict, Any
from app.models.notification import Notification

class NotificationService:
    @staticmethod
    def validate_notification(title: str, message: str, 
                            user_id: str) -> Tuple[bool, Optional[str]]:
        """Validate notification data"""
        if not title or len(title) < 1:
            return False, "Title is required"
        if not message or len(message) < 1:
            return False, "Message is required"
        if not user_id:
            return False, "User ID is required"
        return True, None
    
    @staticmethod
    def get_unread_count(user_id: str) -> int:
        """Get count of unread notifications"""
        return Notification.count_unread(user_id)
```

**3. Model (`app/models/notification.py`):**

```python
from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
from app import mongo

class Notification:
    @staticmethod
    def create(title: str, message: str, user_id: str, 
              type: str = 'info') -> Tuple[bool, str]:
        """Create a new notification"""
        try:
            new_notification = {
                'title': title,
                'message': message,
                'user_id': ObjectId(user_id),
                'type': type,
                'read': False,
                'createdAt': datetime.utcnow()
            }
            result = mongo.db.notifications.insert_one(new_notification)
            return True, str(result.inserted_id)
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {e}")
            return False, str(e)
    
    @staticmethod
    def get_by_user(user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = {'user_id': ObjectId(user_id)}
        if unread_only:
            query['read'] = False
        return list(mongo.db.notifications.find(query).sort('createdAt', -1))
    
    @staticmethod
    def mark_as_read(notification_id: str) -> Tuple[bool, str]:
        """Mark notification as read"""
        try:
            result = mongo.db.notifications.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'read': True}}
            )
            return result.modified_count > 0, "Marked as read"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def count_unread(user_id: str) -> int:
        """Count unread notifications"""
        return mongo.db.notifications.count_documents({
            'user_id': ObjectId(user_id),
            'read': False
        })
```

**4. Controller (`app/controllers/notification.py`):**

```python
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.schemas.notification_schemas import NotificationCreateSchema
from pydantic import ValidationError

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

@notification_bp.route('/', methods=['GET'])
@login_required
def list_notifications():
    """List user notifications"""
    notifications = Notification.get_by_user(str(current_user.id))
    return render_template('notifications/list.html', 
                         notifications=notifications)

@notification_bp.route('/create', methods=['POST'])
@login_required
def create_notification():
    """Create a notification"""
    try:
        # Validate with Pydantic
        validated = NotificationCreateSchema(**request.form.to_dict())
        
        # Create notification
        success, result = Notification.create(
            title=validated.title,
            message=validated.message,
            user_id=validated.user_id,
            type=validated.type
        )
        
        if success:
            flash('Notification created!', 'success')
        else:
            flash(f'Error: {result}', 'danger')
            
    except ValidationError as e:
        flash(f'Validation error: {e}', 'danger')
    
    return redirect(url_for('notification.list_notifications'))

@notification_bp.route('/<id>/read', methods=['POST'])
@login_required
def mark_read(id):
    """Mark notification as read"""
    success, message = Notification.mark_as_read(id)
    return jsonify({'success': success, 'message': message})

@notification_bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """Get unread notification count"""
    count = NotificationService.get_unread_count(str(current_user.id))
    return jsonify({'count': count})
```

**5. View (`app/views/notification_view.py`):**

```python
from flask import render_template
from app.models.notification import Notification

class NotificationView:
    @staticmethod
    def render_list(user_id: str):
        """Render notifications list"""
        notifications = Notification.get_by_user(user_id)
        return render_template('notifications/list.html',
                             notifications=notifications)
```

**6. Template (`app/templates/notifications/list.html`):**

```html
{% extends "layout.html" %}

{% block content %}
<div class="container mt-4">
    <h2>Notifications</h2>
    
    {% for notification in notifications %}
    <div class="alert alert-{{ notification.type }} {% if notification.read %}alert-secondary{% endif %}">
        <h5>{{ notification.title }}</h5>
        <p>{{ notification.message }}</p>
        <small>{{ notification.createdAt.strftime('%Y-%m-%d %H:%M') }}</small>
        
        {% if not notification.read %}
        <button class="btn btn-sm btn-primary mark-read" 
                data-id="{{ notification._id }}">
            Mark as Read
        </button>
        {% endif %}
    </div>
    {% endfor %}
</div>

<script>
document.querySelectorAll('.mark-read').forEach(btn => {
    btn.addEventListener('click', function() {
        const id = this.dataset.id;
        fetch(`/notifications/${id}/read`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    });
});
</script>
{% endblock %}
```

**7. Registrar Blueprint (`app/__init__.py`):**

```python
from app.controllers.notification import notification_bp
app.register_blueprint(notification_bp)
```

**8. Testes (`tests/unit/test_notification_service.py`):**

```python
import pytest
from app.services.notification_service import NotificationService

def test_validate_notification_valid():
    """Test notification validation with valid data"""
    valid, error = NotificationService.validate_notification(
        title='Test',
        message='Test message',
        user_id='507f1f77bcf86cd799439011'
    )
    assert valid is True
    assert error is None

def test_validate_notification_missing_title():
    """Test validation with missing title"""
    valid, error = NotificationService.validate_notification(
        title='',
        message='Test message',
        user_id='507f1f77bcf86cd799439011'
    )
    assert valid is False
    assert 'Title is required' in error
```

## Tecnologias e Dependências

### Backend Core

- **Flask 2.3.3** - Framework web
- **PyMongo 4.6.0** - Driver MongoDB
- **Flask-PyMongo 2.3.0** - Integração Flask + MongoDB
- **Python 3.9+** - Linguagem de programação

### Autenticação e Segurança

- **Flask-Login 0.6.2** - Gerenciamento de sessões
- **Flask-Bcrypt 1.0.1** - Hash de senhas
- **Flask-WTF 1.2.1** - CSRF protection
- **Flask-Limiter 3.5.0** - Rate limiting

### Validação

- **Pydantic 2.5.0** - Validação de dados e schemas
- **Email-validator 2.1.0** - Validação de emails

### Configuração

- **Python-dotenv 1.0.0** - Variáveis de ambiente

### Testes

- **Pytest 7.4.3** - Framework de testes
- **Pytest-Flask 1.3.0** - Testes Flask
- **Pytest-Cov 4.1.0** - Cobertura de código

### Frontend

- **Bootstrap 5** - Framework CSS
- **Jinja2** - Template engine (incluso no Flask)
- **JavaScript** - Scripts customizados

### Banco de Dados

- **MongoDB 4.6+** - Banco de dados NoSQL

### Ferramentas de Desenvolvimento

- **Husky 9.1.7** - Git hooks
- **Flake8** - Linter Python
- **Git** - Controle de versão

## Padrões de Código

### Convenções de Nomenclatura

**Python:**

- Classes: `PascalCase` (ex: `UserService`, `ClientModel`)
- Funções/métodos: `snake_case` (ex: `create_user`, `get_by_id`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `MAX_LOGIN_ATTEMPTS`)
- Variáveis: `snake_case` (ex: `user_id`, `total_count`)

**Arquivos:**

- Módulos Python: `snake_case.py` (ex: `auth_service.py`)
- Templates HTML: `snake_case.html` (ex: `client_list.html`)
- CSS/JS: `kebab-case` (ex: `main-style.css`)

### Estrutura de Métodos

**Models:**

```python
class Model:
    @staticmethod
    def create(...) -> Tuple[bool, str]:
        """Create new record"""
        pass
    
    @staticmethod
    def get_by_id(id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        pass
    
    @staticmethod
    def update(id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update record"""
        pass
    
    @staticmethod
    def delete(id: str) -> Tuple[bool, str]:
        """Delete record"""
        pass
    
    @staticmethod
    def list_all(filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """List all records"""
        pass
```

**Services:**

```python
class Service:
    @staticmethod
    def validate_data(...) -> Tuple[bool, Optional[str]]:
        """Validate data and return (is_valid, error_message)"""
        pass
    
    @staticmethod
    def process_business_logic(...) -> Tuple[bool, Any, Optional[str]]:
        """Process logic and return (success, result, error)"""
        pass
```

### Documentação

**Docstrings:**

```python
def function_name(param1: str, param2: int) -> Tuple[bool, str]:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Tuple containing (success: bool, message: str)
    
    Raises:
        ValueError: If param1 is invalid
    """
    pass
```

### Tratamento de Erros

```python
try:
    # Operation
    result = perform_operation()
    return True, result
except ValueError as e:
    current_app.logger.error(f"Validation error: {e}")
    return False, f"Invalid data: {e}"
except Exception as e:
    current_app.logger.error(f"Unexpected error: {e}")
    return False, "An unexpected error occurred"
```

## Performance e Otimização

### Database Indexes

Criar índices para queries frequentes:

```python
# Criar índice no username (único)
mongo.db.users.create_index([('username', 1)], unique=True)

# Criar índice no email
mongo.db.users.create_index([('email', 1)])

# Índice composto
mongo.db.login_logs.create_index([('user_id', 1), ('timestamp', -1)])
```

### Caching

Considerar implementar cache para dados frequentemente acessados:

```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_popular_templates():
    """Cache por 5 minutos"""
    return Template.list_all()
```

### Queries Eficientes

```python
# ❌ Evitar: Buscar tudo e filtrar em Python
all_users = mongo.db.users.find()
active_users = [u for u in all_users if u['status'] == 'active']

# ✅ Preferir: Filtrar no MongoDB
active_users = mongo.db.users.find({'status': 'active'})

# ❌ Evitar: Múltiplas queries em loop
for user_id in user_ids:
    user = mongo.db.users.find_one({'_id': user_id})

# ✅ Preferir: Query única
users = mongo.db.users.find({'_id': {'$in': user_ids}})
```

## Referências

### Documentação Oficial

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

### Recursos Adicionais

- [Flask Patterns](https://flask.palletsprojects.com/en/latest/patterns/)
- [MongoDB Best Practices](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)

## Suporte e Contribuição

Para questões, problemas ou contribuições:

1. Consulte o `README.md` para informações gerais
2. Verifique `TEMPLATE_FIELDS_SYSTEM.md` para sistema de templates
3. Leia `CODE_OF_CONDUCT.md` para diretrizes de contribuição
4. Verifique os logs da aplicação para debugging
5. Execute os testes antes de fazer commits

---

**Última Atualização:** Outubro 2025  
**Versão:** 1.1.0
