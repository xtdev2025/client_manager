# 🏗️ Arquitetura do Client Manager

## Visão Geral

O Client Manager segue uma arquitetura MVC (Model-View-Controller) com camadas adicionais para separação de responsabilidades.

## Camadas da Aplicação

### 1. Models (`app/models/`)

Responsável pela interação com o banco de dados MongoDB e lógica de dados.

**Características:**
- Definição das estruturas de dados
- Operações CRUD básicas
- Validações de negócio relacionadas aos dados
- Type hints em todos os métodos

**Exemplo:**
```python
from typing import Tuple, Optional, Dict, Any

class Plan:
    @staticmethod
    def create(name: str, description: str, price: float, 
               duration_days: int) -> Tuple[bool, str]:
        """Create a new plan"""
        # Implementation
        pass
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
AuditService.log_admin_action('create', admin_id, {'username': 'newadmin'})

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
        password='securepass123',
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

**Responsabilidades:**
- Receber requisições
- Validar entrada usando schemas
- Chamar services para lógica de negócio
- Retornar respostas HTTP

```python
@plan.route('/create', methods=['POST'])
@login_required
@admin_required
def create_plan():
    data = request.form.to_dict()
    
    # Validar com pydantic
    valid, validated_data, error = validate_plan_create(data)
    if not valid:
        flash(error, 'danger')
        return redirect(url_for('plan.create'))
    
    # Criar usando model
    success, plan_id = Plan.create(**validated_data)
    
    # Auditar ação
    if success:
        AuditService.log_plan_action('create', plan_id, validated_data)
    
    return redirect(url_for('plan.list_plans'))
```

### 5. Views (`app/views/`)

Renderização de templates HTML com dados preparados.

### 6. Templates (`app/templates/`)

Interface visual HTML com Jinja2.

## Fluxo de uma Requisição

```
1. Usuário faz requisição HTTP
   ↓
2. Controller recebe a requisição
   ↓
3. Controller valida dados (schemas/pydantic)
   ↓
4. Controller chama Service para lógica de negócio
   ↓
5. Service chama Model para operações de dados
   ↓
6. Model interage com MongoDB
   ↓
7. Service/Controller registra auditoria (se necessário)
   ↓
8. Controller prepara resposta e chama View
   ↓
9. View renderiza template
   ↓
10. Resposta HTTP retorna ao usuário
```

## Segurança

### Rate Limiting

Proteção contra força bruta e abuso:

```python
from app import limiter

@auth.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    # Máximo 10 tentativas de login por minuto
    pass
```

### Auditoria

Todas as operações sensíveis são registradas:

```python
# Criação de admin
AuditService.log_admin_action('create', admin_id, details)

# Atualização de plano
AuditService.log_plan_action('update', plan_id, details)

# Exclusão de domínio
AuditService.log_domain_action('delete', domain_id, details)
```

### Type Safety

Type hints em todo o código para segurança de tipos:

```python
def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    # Implementation
    pass
```

## Testes

### Estrutura

```
tests/
├── conftest.py              # Fixtures e configuração
├── unit/                    # Testes unitários
│   ├── test_auth_service.py
│   ├── test_client_service.py
│   └── test_audit_service.py
└── integration/             # Testes de integração
    ├── test_auth_routes.py
    └── test_plan_routes.py
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Verboso
pytest -v
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

1. Criar schema de validação em `app/schemas/`
2. Implementar service em `app/services/` (se necessário)
3. Criar método no model em `app/models/`
4. Implementar route no controller em `app/controllers/`
5. Criar template em `app/templates/`
6. Adicionar testes em `tests/`

### Exemplo Completo

```python
# 1. Schema (app/schemas/user_schemas.py)
class FeatureCreateSchema(BaseModel):
    name: str = Field(..., min_length=1)
    enabled: bool = Field(default=True)

# 2. Service (app/services/feature_service.py)
class FeatureService:
    @staticmethod
    def validate_feature(name: str) -> Tuple[bool, Optional[str]]:
        # Validação
        pass

# 3. Model (app/models/feature.py)
class Feature:
    @staticmethod
    def create(name: str, enabled: bool) -> Tuple[bool, str]:
        # Criação
        pass

# 4. Controller (app/controllers/feature.py)
@feature.route('/create', methods=['POST'])
@login_required
@admin_required
def create_feature():
    # Implementação
    pass

# 5. Template (app/templates/feature/create.html)
# HTML com formulário

# 6. Testes (tests/unit/test_feature_service.py)
def test_validate_feature():
    # Teste
    pass
```

## Referências

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
