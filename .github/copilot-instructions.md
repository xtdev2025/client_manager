# Instruções para o GitHub Copilot

Este arquivo contém instruções específicas para o GitHub Copilot ajudar no desenvolvimento do projeto Client Manager, uma aplicação Flask com MongoDB que implementa um sistema MVC + Services para gerenciamento de clientes com múltiplas funcionalidades empresariais.

## 🏗️ Arquitetura do Projeto

### Estrutura MVC + Services

O projeto segue uma arquitetura em camadas:

1. **Models** (`/app/models/`) - Interação com MongoDB, definição de estruturas de dados
2. **Services** (`/app/services/`) - Lógica de negócio reutilizável e complexa
3. **Controllers** (`/app/controllers/`) - Processamento de requisições HTTP, orquestração
4. **Views** (`/app/views/`) - Renderização de templates, preparação de dados para UI
5. **Schemas** (`/app/schemas/`) - Validação de dados com Pydantic
6. **Templates** (`/app/templates/`) - HTML Jinja2 com Bootstrap

### Fluxo de Dados

```
Request → Controller → Service → Model → MongoDB
                ↓         ↓
             Schema    Business Logic
                ↓
             View → Template → Response
```

## 📋 Convenções de Código

### 1. Estrutura MVC + Services

**Models** (`/app/models/`):
- Classes que interagem com MongoDB
- Métodos estáticos para operações CRUD
- Validações básicas de dados
- Type hints obrigatórios
- Retorno padrão: `Tuple[bool, str]` para operações de escrita

**Services** (`/app/services/`):
- Lógica de negócio complexa
- Validações avançadas
- Integração entre múltiplos models
- Enriquecimento de dados
- Reutilizáveis entre controllers

**Controllers** (`/app/controllers/`):
- Definição de rotas Flask
- Processamento de requisições HTTP
- Orquestração de Services e Models
- Tratamento de erros e exceções
- Retorno de responses (JSON ou redirect)

**Views** (`/app/views/`):
- Preparação de dados para templates
- Lógica de apresentação
- Formatação de dados
- Métodos que retornam `render_template()`

**Schemas** (`/app/schemas/`):
- Validação de dados com Pydantic
- Serialização/deserialização
- Type safety em APIs

### 2. Formatação Python

- **Seguir PEP 8 estritamente**
- Indentação: 4 espaços
- Linhas: máximo 100 caracteres
- **Docstrings obrigatórias** para todas as funções e classes públicas
- Type hints em todos os parâmetros e retornos
- Imports organizados: stdlib → third-party → local

**Exemplo de Docstring:**
```python
def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Autentica um usuário verificando credenciais.
    
    Args:
        username: Nome de usuário ou email
        password: Senha em texto plano
        
    Returns:
        Tuple contendo:
        - bool: Sucesso da autenticação
        - Optional[Dict]: Dados do usuário se autenticado
        - Optional[str]: Mensagem de erro se falhou
        
    Raises:
        ValueError: Se username ou password estiverem vazios
    """
```

### 3. MongoDB

- Usar PyMongo para todas as operações
- Validação de ObjectId antes de queries
- Índices definidos para campos de busca frequente
- Timestamps: `createdAt` e `updatedAt` em UTC
- Soft delete quando aplicável (campo `deletedAt`)

**Padrão de Model:**
```python
from typing import Tuple, Optional, Dict, Any
from bson.objectid import ObjectId
from datetime import datetime

class ModelName:
    collection_name = 'collection_name'
    
    @staticmethod
    def create(param1: str, param2: int) -> Tuple[bool, str]:
        """Cria novo documento"""
        try:
            new_doc = {
                'field1': param1,
                'field2': param2,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            result = mongo.db[ModelName.collection_name].insert_one(new_doc)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, f"Erro ao criar: {str(e)}"
    
    @staticmethod
    def get_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
        """Busca documento por ID"""
        try:
            if isinstance(doc_id, str):
                doc_id = ObjectId(doc_id)
            return mongo.db[ModelName.collection_name].find_one({'_id': doc_id})
        except Exception:
            return None
```

### 4. Segurança

**Autenticação:**
- Flask-Login para gerenciamento de sessões
- Bcrypt para hashing de senhas (nunca senhas em plaintext)
- Decorators: `@login_required`, `@admin_required`, `@super_admin_required`

**Autorização RBAC:**
- Roles: `super_admin`, `admin`, `client`
- Verificação em cada endpoint sensível
- Auditoria de ações administrativas

**Proteções:**
- CSRF tokens em todos os formulários
- Rate limiting com Flask-Limiter
- Validação de entrada com Pydantic
- Sanitização de dados de usuário
- Headers de segurança configurados

**Exemplo de Controller Seguro:**
```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.validators import admin_required
from app.services.audit_service import AuditService

bp = Blueprint('example', __name__)

@bp.route('/admin/action', methods=['POST'])
@login_required
@admin_required
def admin_action():
    """Ação administrativa com auditoria"""
    try:
        # Validar dados
        data = request.get_json()
        
        # Processar
        success, result = SomeService.perform_action(data)
        
        # Auditar
        if success:
            AuditService.log_action(
                admin_id=str(current_user.id),
                action='admin_action',
                details=data
            )
        
        return jsonify({'success': success, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
```

## 🎯 Tarefas Comuns

### Criar Novo Endpoint

Fluxo completo para adicionar um novo endpoint:

1. **Definir rota no Controller** (`/app/controllers/`)
   ```python
   @bp.route('/resource/action', methods=['GET', 'POST'])
   @login_required
   def action_handler():
       pass
   ```

2. **Criar Service se necessário** (`/app/services/`)
   ```python
   class ResourceService:
       @staticmethod
       def perform_action(data: Dict) -> Tuple[bool, Any]:
           pass
   ```

3. **Adicionar método no Model** (`/app/models/`)
   ```python
   @staticmethod
   def create(params) -> Tuple[bool, str]:
       pass
   ```

4. **Criar View** (`/app/views/`)
   ```python
   def render_action_page(data: Dict) -> str:
       return render_template('action.html', data=data)
   ```

5. **Implementar Template** (`/app/templates/`)
   ```html
   {% extends "layout.html" %}
   {% block content %}
   <!-- conteúdo -->
   {% endblock %}
   ```

6. **Adicionar à navegação** (`/app/templates/navbar.html`)

7. **Documentar no Swagger** (`/app/api/swagger.py`)
   - Adicionar especificação OpenAPI
   - Definir schemas de request/response
   - Incluir exemplos

### Adicionar Nova Funcionalidade

Checklist para novas features:

1. ✅ **Controle de acesso** - Definir roles necessárias
2. ✅ **Validações** - Criar schemas Pydantic se necessário
3. ✅ **Mensagens flash** - Feedback visual ao usuário
4. ✅ **Auditoria** - Log de ações importantes via AuditService
5. ✅ **Testes** - Criar testes unitários e de integração
6. ✅ **Documentação** - Atualizar Swagger/OpenAPI
7. ✅ **Navegação** - Atualizar navbar se aplicável

### Implementar Documentação Swagger

Para cada endpoint, adicionar em `/app/api/swagger.py`:

```python
@bp.route('/resource/<resource_id>', methods=['GET'])
@login_required
def get_resource(resource_id):
    """
    Obter recurso por ID
    ---
    tags:
      - Resources
    parameters:
      - name: resource_id
        in: path
        type: string
        required: true
        description: ID do recurso
    responses:
      200:
        description: Recurso encontrado
        schema:
          $ref: '#/definitions/Resource'
      404:
        description: Recurso não encontrado
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Não autenticado
    security:
      - Bearer: []
    """
    pass
```

## 📚 Bibliotecas Principais

### Core
- **Flask 2.3.3** - Framework web

### Core
- **Flask 2.3.3** - Framework web
- **PyMongo** - Driver MongoDB
- **Flask-Login** - Gerenciamento de sessões e autenticação
- **python-dotenv** - Variáveis de ambiente

### Validação e API
- **Pydantic 2.5.0** - Validação de dados e schemas
- **apispec 6.3.0** - Geração de especificação OpenAPI
- **flask-swagger-ui 4.11.1** - Interface Swagger UI
- **apispec-webframeworks 0.5.2** - Integração Flask + APISpec

### Segurança
- **Flask-Limiter 3.5.0** - Rate limiting
- **Bcrypt** - Hashing de senhas
- **Flask-WTF** - Proteção CSRF

### Testes
- **pytest 7.4.3** - Framework de testes
- **pytest-cov 4.1.0** - Coverage de testes

Ao usar estas bibliotecas, **sempre siga os padrões existentes** no projeto.

## 🎨 Estrutura de Templates

Templates HTML seguem este padrão consistente:

1. **Extensão de layout base**: `{% extends "layout.html" %}`
2. **Blocos Jinja2**: 
   - `{% block title %}{% endblock %}` - Título da página
   - `{% block content %}{% endblock %}` - Conteúdo principal
3. **Navegação**: Incluir via `{% include 'navbar.html' %}`
4. **Estilização**: Classes Bootstrap 5
5. **Formulários**: CSRF token obrigatório
6. **Flash messages**: Exibir com Bootstrap alerts

**Exemplo de Template:**
```html
{% extends "layout.html" %}

{% block title %}Título da Página{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Título</h1>
    
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <!-- Conteúdo -->
    <form method="POST">
        {{ form.hidden_tag() }}  <!-- CSRF token -->
        <!-- campos do formulário -->
    </form>
</div>
{% endblock %}
```

## 🧪 Testes e Qualidade de Código

### Padrões de Testes

**Estrutura:**
- `tests/unit/` - Testes unitários (Services, Models)
- `tests/integration/` - Testes de integração (Routes, Controllers)
- `tests/conftest.py` - Fixtures compartilhadas

**Convenções:**
- Arquivos: `test_*.py` ou `*_test.py`
- Classes: `TestNomeDaClasse`
- Métodos: `test_descricao_do_teste`
- Fixtures: Use `@pytest.fixture`
- Mocks: Use `unittest.mock` ou `pytest-mock`

**Exemplo de Teste:**
```python
import pytest
from app.services.auth_service import AuthService

class TestAuthService:
    """Testes para AuthService"""
    
    def test_authenticate_user_valid_credentials(self, app, sample_user):
        """Deve autenticar usuário com credenciais válidas"""
        success, user, error = AuthService.authenticate_user(
            username='testuser',
            password='validpass123'
        )
        
        assert success is True
        assert user is not None
        assert error is None
        assert user['username'] == 'testuser'
    
    def test_authenticate_user_invalid_password(self, app):
        """Deve falhar com senha inválida"""
        success, user, error = AuthService.authenticate_user(
            username='testuser',
            password='wrongpass'
        )
        
        assert success is False
        assert user is None
        assert error == 'Credenciais inválidas'
```

### Qualidade de Código

Ao sugerir implementações, garantir:

1. ✅ **Flake8** - Sem violações de PEP 8
2. ✅ **Type hints** - Em todos os parâmetros e retornos
3. ✅ **Docstrings** - Documentação clara
4. ✅ **SOLID** - Princípios de design orientado a objetos
5. ✅ **DRY** - Não repetir código
6. ✅ **Testabilidade** - Código fácil de testar
7. ✅ **Coverage** - Mínimo 80% de cobertura

### Pre-commit Hooks

O projeto usa pre-commit hooks que executam:
- Flake8 para linting
- Verificação de conflitos de merge
- Verificação de arquivos grandes
- Formatação de YAML/JSON

**Código deve sempre passar pelos hooks antes do commit.**

## 🔄 Fluxo Git

### Branches

Seguir este padrão de nomenclatura:

- `feature/nome-da-feature` - Novas funcionalidades
- `bugfix/descricao-do-bug` - Correções de bugs
- `hotfix/descricao-urgente` - Correções urgentes em produção
- `refactor/area-refatorada` - Refatorações
- `docs/descricao` - Atualizações de documentação
- `test/area-testada` - Adição/melhoria de testes

### Mensagens de Commit

Formato padrão: `[Área]: Descrição clara e concisa`

**Exemplos:**
- `[Auth]: Adiciona validação de força de senha`
- `[API]: Implementa documentação Swagger para clients endpoints`
- `[Tests]: Adiciona testes de integração para admin routes`
- `[Security]: Corrige vulnerabilidade CVE-2024-XXXX`
- `[Refactor]: Extrai lógica de validação para ClientService`
- `[Docs]: Atualiza ARCHITECTURE.md com novos padrões`

**Áreas comuns:**
- `[Auth]`, `[API]`, `[Models]`, `[Services]`, `[Controllers]`, `[Views]`
- `[Tests]`, `[Security]`, `[Docs]`, `[Config]`, `[DB]`, `[Refactor]`

### Pull Requests

Antes de criar PR, verificar:

1. ✅ Todos os testes passando (`pytest tests/`)
2. ✅ Flake8 sem erros
3. ✅ Coverage adequado (mínimo 80%)
4. ✅ Documentação atualizada
5. ✅ CHANGELOG.md atualizado (se aplicável)
6. ✅ Swagger/OpenAPI atualizado (novos endpoints)

## 📊 Swagger/OpenAPI

### Status da Implementação

O projeto está implementando documentação completa da API:

- **45+ endpoints** mapeados
- **10 tags** organizacionais definidas
- **OpenAPI 3.0** como especificação
- **Swagger UI** em `/api/docs`

### Tags Organizacionais

```python
SWAGGER_TAGS = [
    'Auth',           # Autenticação e autorização
    'Main',           # Rotas principais  
    'Clients',        # Gerenciamento de clientes (admin)
    'Client Portal',  # Área do cliente (my-*)
    'Admins',         # Gerenciamento de admins
    'Plans',          # Gerenciamento de planos
    'Domains',        # Gerenciamento de domínios
    'Templates',      # Gerenciamento de templates
    'Infos',          # Informações bancárias
    'Audit'           # Logs de auditoria
]
```

### Documentar Novo Endpoint

Ao criar um novo endpoint, **SEMPRE** adicionar documentação Swagger:

```python
from flask import Blueprint
from flask_login import login_required

bp = Blueprint('example', __name__)

@bp.route('/api/resource', methods=['GET'])
@login_required
def get_resource():
    """
    Obter lista de recursos
    ---
    tags:
      - Resources
    summary: Lista todos os recursos disponíveis
    description: Retorna uma lista paginada de recursos com filtros opcionais
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Número da página
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Itens por página
    responses:
      200:
        description: Lista de recursos retornada com sucesso
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                $ref: '#/definitions/Resource'
            pagination:
              $ref: '#/definitions/Pagination'
      401:
        description: Não autenticado
        schema:
          $ref: '#/definitions/Error'
      403:
        description: Sem permissão
        schema:
          $ref: '#/definitions/Error'
    security:
      - Bearer: []
    """
    pass
```

### Schemas Comuns

Definir schemas reutilizáveis em `/app/schemas/`:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class UserSchema(BaseModel):
    """Schema base de usuário"""
    id: str = Field(..., description="ID único do usuário")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern="^(super_admin|admin|client)$")
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "john@example.com",
                "role": "client",
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-01T00:00:00Z"
            }
        }

class ErrorSchema(BaseModel):
    """Schema padrão de erro"""
    success: bool = Field(default=False)
    error: str = Field(..., description="Mensagem de erro")
    code: Optional[int] = Field(None, description="Código de erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Recurso não encontrado",
                "code": 404
            }
        }
```

## 🔐 Controle de Acesso (RBAC)

### Roles Disponíveis

1. **super_admin** - Acesso total ao sistema
   - Gerenciar admins
   - Gerenciar clientes
   - Acessar logs de auditoria
   - Configurações do sistema

2. **admin** - Gestão operacional
   - Gerenciar clientes
   - Gerenciar planos, domínios, templates
   - Ver informações bancárias

3. **client** - Acesso limitado
   - Ver próprios domínios
   - Ver próprias estatísticas
   - Ver próprias informações
   - Alterar própria senha

### Decorators de Autorização

```python
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Requer que usuário seja admin ou super_admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role not in ['admin', 'super_admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Requer que usuário seja super_admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != 'super_admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """Requer que usuário seja client"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != 'client':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

### Uso nos Controllers

```python
@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Apenas admins podem acessar"""
    pass

@bp.route('/client/my-domains')
@login_required
@client_required
def my_domains():
    """Apenas clients podem acessar"""
    pass

@bp.route('/admin/settings')
@login_required
@super_admin_required
def system_settings():
    """Apenas super_admins podem acessar"""
    pass
```

## 📝 Sistema de Auditoria

### AuditService

O sistema possui auditoria completa de ações administrativas:

```python
from app.services.audit_service import AuditService

# Registrar ação
AuditService.log_action(
    admin_id=str(current_user.id),
    action='delete_client',
    entity_type='Client',
    entity_id=client_id,
    details={
        'client_name': client_name,
        'reason': 'Solicitação do cliente'
    }
)

# Buscar logs
logs = AuditService.get_logs(
    filters={'admin_id': admin_id},
    limit=50
)

# Limpar logs antigos
AuditService.clear_old_logs(days=90)
```

### Ações Auditadas

Sempre auditar:
- Criação/edição/exclusão de usuários
- Mudanças de permissões
- Acesso a dados sensíveis
- Alterações em configurações
- Falhas de autenticação
- Ações administrativas críticas

## 🚀 Padrões de Performance

### MongoDB Queries

```python
# ❌ Evitar: Query sem projeção
all_data = mongo.db.users.find({})

# ✅ Preferir: Query com projeção
needed_data = mongo.db.users.find(
    {},
    {'username': 1, 'email': 1, 'role': 1}
)

# ❌ Evitar: Loop com queries individuais
for user_id in user_ids:
    user = mongo.db.users.find_one({'_id': user_id})

# ✅ Preferir: Query única com $in
users = mongo.db.users.find({
    '_id': {'$in': user_ids}
})

# Usar índices para queries frequentes
mongo.db.users.create_index('username')
mongo.db.users.create_index('email', unique=True)
```

### Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache de dados estáticos
@lru_cache(maxsize=128)
def get_all_plans():
    """Cache de planos (raramente mudam)"""
    return list(mongo.db.plans.find())

# Cache com expiração
_cache = {}
_cache_time = {}

def get_cached_stats(client_id: str, ttl: int = 300):
    """Cache com TTL de 5 minutos"""
    cache_key = f"stats_{client_id}"
    
    if cache_key in _cache:
        if datetime.now() - _cache_time[cache_key] < timedelta(seconds=ttl):
            return _cache[cache_key]
    
    # Buscar dados
    stats = calculate_stats(client_id)
    _cache[cache_key] = stats
    _cache_time[cache_key] = datetime.now()
    
    return stats
```

## 📚 Recursos e Documentação

### Documentação Interna

- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) - Arquitetura completa
- [`docs/SWAGGER_IMPLEMENTATION.md`](../docs/SWAGGER_IMPLEMENTATION.md) - Implementação API
- [`docs/TEMPLATE_FIELDS_SYSTEM.md`](../docs/TEMPLATE_FIELDS_SYSTEM.md) - Sistema de templates
- [`docs/README.md`](../docs/README.md) - Índice de documentação

### Links Externos Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [pytest Documentation](https://docs.pytest.org/)

## 🎯 Diretrizes de Implementação

### Ao Criar Código, Sempre:

1. ✅ **Adicionar type hints** em todos os parâmetros e retornos
2. ✅ **Escrever docstrings** descritivas
3. ✅ **Validar entradas** de usuários
4. ✅ **Tratar exceções** apropriadamente
5. ✅ **Usar logging** para debug
6. ✅ **Seguir princípios SOLID**
7. ✅ **Escrever testes** para novo código
8. ✅ **Documentar no Swagger** se for endpoint API
9. ✅ **Auditar ações** sensíveis
10. ✅ **Verificar permissões** (RBAC)

### Ao Revisar Código, Verificar:

1. ✅ Segue convenções do projeto
2. ✅ Tem testes adequados
3. ✅ Documentação está completa
4. ✅ Não introduz vulnerabilidades
5. ✅ Performance está otimizada
6. ✅ Não quebra funcionalidades existentes
7. ✅ Logs de auditoria apropriados
8. ✅ Tratamento de erros robusto

## 💡 Exemplos Práticos

### Exemplo Completo: CRUD de Resource

**1. Model (`/app/models/resource.py`):**
```python
from typing import Tuple, Optional, Dict, List, Any
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo

class Resource:
    """Model para gerenciamento de recursos"""
    
    collection_name = 'resources'
    
    @staticmethod
    def create(name: str, description: str, owner_id: str) -> Tuple[bool, str]:
        """
        Cria um novo recurso.
        
        Args:
            name: Nome do recurso
            description: Descrição do recurso
            owner_id: ID do proprietário
            
        Returns:
            Tuple[bool, str]: (sucesso, id_ou_erro)
        """
        try:
            new_resource = {
                'name': name,
                'description': description,
                'owner_id': ObjectId(owner_id),
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'deletedAt': None
            }
            
            result = mongo.db[Resource.collection_name].insert_one(new_resource)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, f"Erro ao criar recurso: {str(e)}"
    
    @staticmethod
    def get_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca recurso por ID.
        
        Args:
            resource_id: ID do recurso
            
        Returns:
            Optional[Dict]: Dados do recurso ou None
        """
        try:
            if isinstance(resource_id, str):
                resource_id = ObjectId(resource_id)
            
            return mongo.db[Resource.collection_name].find_one({
                '_id': resource_id,
                'deletedAt': None
            })
        except Exception:
            return None
    
    @staticmethod
    def list_all(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lista todos os recursos com filtros opcionais.
        
        Args:
            filters: Filtros de busca opcionais
            limit: Limite de resultados
            
        Returns:
            List[Dict]: Lista de recursos
        """
        query = {'deletedAt': None}
        if filters:
            query.update(filters)
        
        return list(
            mongo.db[Resource.collection_name]
            .find(query)
            .limit(limit)
            .sort('createdAt', -1)
        )
    
    @staticmethod
    def update(resource_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza um recurso.
        
        Args:
            resource_id: ID do recurso
            updates: Campos a atualizar
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if isinstance(resource_id, str):
                resource_id = ObjectId(resource_id)
            
            updates['updatedAt'] = datetime.utcnow()
            
            result = mongo.db[Resource.collection_name].update_one(
                {'_id': resource_id, 'deletedAt': None},
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                return True, "Recurso atualizado com sucesso"
            return False, "Recurso não encontrado ou não modificado"
        except Exception as e:
            return False, f"Erro ao atualizar recurso: {str(e)}"
    
    @staticmethod
    def delete(resource_id: str, soft: bool = True) -> Tuple[bool, str]:
        """
        Deleta um recurso (soft delete por padrão).
        
        Args:
            resource_id: ID do recurso
            soft: Se True, faz soft delete
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if isinstance(resource_id, str):
                resource_id = ObjectId(resource_id)
            
            if soft:
                result = mongo.db[Resource.collection_name].update_one(
                    {'_id': resource_id},
                    {'$set': {'deletedAt': datetime.utcnow()}}
                )
                msg = "Recurso removido com sucesso"
            else:
                result = mongo.db[Resource.collection_name].delete_one(
                    {'_id': resource_id}
                )
                msg = "Recurso deletado permanentemente"
            
            if result.modified_count > 0 or result.deleted_count > 0:
                return True, msg
            return False, "Recurso não encontrado"
        except Exception as e:
            return False, f"Erro ao deletar recurso: {str(e)}"
```

**2. Service (`/app/services/resource_service.py`):**
```python
from typing import Tuple, Optional, Dict, List, Any
from app.models.resource import Resource
from app.models.user import User

class ResourceService:
    """Service para lógica de negócio de recursos"""
    
    @staticmethod
    def validate_resource_data(name: str, description: str) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de recurso.
        
        Args:
            name: Nome do recurso
            description: Descrição
            
        Returns:
            Tuple[bool, Optional[str]]: (válido, mensagem_erro)
        """
        if not name or len(name) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        if len(name) > 100:
            return False, "Nome deve ter no máximo 100 caracteres"
        
        if not description:
            return False, "Descrição é obrigatória"
        
        if len(description) > 500:
            return False, "Descrição deve ter no máximo 500 caracteres"
        
        return True, None
    
    @staticmethod
    def create_resource(name: str, description: str, owner_id: str) -> Tuple[bool, Any]:
        """
        Cria um novo recurso com validações.
        
        Args:
            name: Nome do recurso
            description: Descrição
            owner_id: ID do proprietário
            
        Returns:
            Tuple[bool, Any]: (sucesso, id_ou_erro)
        """
        # Validar dados
        valid, error = ResourceService.validate_resource_data(name, description)
        if not valid:
            return False, error
        
        # Verificar se owner existe
        owner = User.get_by_id(owner_id)
        if not owner:
            return False, "Proprietário não encontrado"
        
        # Criar recurso
        return Resource.create(name, description, owner_id)
    
    @staticmethod
    def get_resource_with_owner(resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca recurso enriquecido com dados do owner.
        
        Args:
            resource_id: ID do recurso
            
        Returns:
            Optional[Dict]: Recurso com dados do owner
        """
        resource = Resource.get_by_id(resource_id)
        if not resource:
            return None
        
        # Enriquecer com dados do owner
        owner = User.get_by_id(str(resource['owner_id']))
        if owner:
            resource['owner'] = {
                'id': str(owner['_id']),
                'username': owner['username'],
                'email': owner.get('email', '')
            }
        
        return resource
    
    @staticmethod
    def user_can_access_resource(user_id: str, resource_id: str, user_role: str) -> bool:
        """
        Verifica se usuário pode acessar recurso.
        
        Args:
            user_id: ID do usuário
            resource_id: ID do recurso
            user_role: Role do usuário
            
        Returns:
            bool: Se pode acessar
        """
        # Admins sempre podem acessar
        if user_role in ['admin', 'super_admin']:
            return True
        
        # Clients só podem acessar próprios recursos
        resource = Resource.get_by_id(resource_id)
        if not resource:
            return False
        
        return str(resource['owner_id']) == user_id
```

**3. Controller (`/app/controllers/resource.py`):**
```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.resource_service import ResourceService
from app.services.audit_service import AuditService
from app.utils.validators import admin_required
from app.views.resource_view import ResourceView

bp = Blueprint('resources', __name__, url_prefix='/resources')

@bp.route('/')
@login_required
def list_resources():
    """Lista recursos"""
    try:
        # Buscar recursos
        if current_user.role == 'client':
            filters = {'owner_id': current_user.id}
        else:
            filters = None
        
        resources = ResourceView.render_list(filters)
        return render_template('resources/list.html', resources=resources)
    except Exception as e:
        flash(f'Erro ao listar recursos: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    """Cria novo recurso"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            # Criar recurso
            success, result = ResourceService.create_resource(
                name=name,
                description=description,
                owner_id=str(current_user.id)
            )
            
            if success:
                # Auditar
                AuditService.log_action(
                    admin_id=str(current_user.id),
                    action='create_resource',
                    entity_type='Resource',
                    entity_id=result,
                    details={'name': name}
                )
                
                flash('Recurso criado com sucesso!', 'success')
                return redirect(url_for('resources.list_resources'))
            else:
                flash(f'Erro: {result}', 'danger')
        except Exception as e:
            flash(f'Erro ao criar recurso: {str(e)}', 'danger')
    
    return render_template('resources/create.html')

@bp.route('/view/<resource_id>')
@login_required
def view_resource(resource_id):
    """Visualiza recurso"""
    try:
        # Verificar permissão
        if not ResourceService.user_can_access_resource(
            user_id=str(current_user.id),
            resource_id=resource_id,
            user_role=current_user.role
        ):
            flash('Sem permissão para acessar este recurso', 'danger')
            return redirect(url_for('resources.list_resources'))
        
        # Buscar recurso
        resource = ResourceService.get_resource_with_owner(resource_id)
        if not resource:
            flash('Recurso não encontrado', 'danger')
            return redirect(url_for('resources.list_resources'))
        
        return render_template('resources/view.html', resource=resource)
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('resources.list_resources'))

@bp.route('/edit/<resource_id>', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    """Edita recurso"""
    try:
        # Verificar permissão
        if not ResourceService.user_can_access_resource(
            user_id=str(current_user.id),
            resource_id=resource_id,
            user_role=current_user.role
        ):
            flash('Sem permissão para editar este recurso', 'danger')
            return redirect(url_for('resources.list_resources'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            # Validar
            valid, error = ResourceService.validate_resource_data(name, description)
            if not valid:
                flash(error, 'danger')
            else:
                # Atualizar
                success, msg = Resource.update(resource_id, {
                    'name': name,
                    'description': description
                })
                
                if success:
                    # Auditar
                    AuditService.log_action(
                        admin_id=str(current_user.id),
                        action='update_resource',
                        entity_type='Resource',
                        entity_id=resource_id,
                        details={'name': name}
                    )
                    flash('Recurso atualizado com sucesso!', 'success')
                    return redirect(url_for('resources.view_resource', resource_id=resource_id))
                else:
                    flash(msg, 'danger')
        
        # Buscar recurso
        resource = ResourceService.get_resource_with_owner(resource_id)
        if not resource:
            flash('Recurso não encontrado', 'danger')
            return redirect(url_for('resources.list_resources'))
        
        return render_template('resources/edit.html', resource=resource)
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('resources.list_resources'))

@bp.route('/delete/<resource_id>', methods=['POST'])
@login_required
@admin_required
def delete_resource(resource_id):
    """Deleta recurso (apenas admins)"""
    try:
        # Buscar para auditoria
        resource = Resource.get_by_id(resource_id)
        if not resource:
            return jsonify({'success': False, 'error': 'Recurso não encontrado'}), 404
        
        # Deletar
        success, msg = Resource.delete(resource_id, soft=True)
        
        if success:
            # Auditar
            AuditService.log_action(
                admin_id=str(current_user.id),
                action='delete_resource',
                entity_type='Resource',
                entity_id=resource_id,
                details={'name': resource.get('name', '')}
            )
            
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API Endpoints com documentação Swagger

@bp.route('/api/resources', methods=['GET'])
@login_required
def api_list_resources():
    """
    Lista recursos via API
    ---
    tags:
      - Resources
    summary: Lista todos os recursos
    description: Retorna lista de recursos do usuário ou todos (se admin)
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Número da página
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Itens por página
    responses:
      200:
        description: Lista retornada com sucesso
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                $ref: '#/definitions/Resource'
      401:
        description: Não autenticado
    security:
      - Bearer: []
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if current_user.role == 'client':
            filters = {'owner_id': current_user.id}
        else:
            filters = None
        
        resources = Resource.list_all(filters=filters, limit=per_page)
        
        # Serializar
        resources_data = []
        for r in resources:
            resources_data.append({
                'id': str(r['_id']),
                'name': r['name'],
                'description': r['description'],
                'owner_id': str(r['owner_id']),
                'createdAt': r['createdAt'].isoformat(),
                'updatedAt': r['updatedAt'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': resources_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(resources_data)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**4. View (`/app/views/resource_view.py`):**
```python
from typing import List, Dict, Any, Optional
from app.models.resource import Resource
from app.models.user import User

class ResourceView:
    """View para preparação de dados de recursos"""
    
    @staticmethod
    def render_list(filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Prepara lista de recursos para exibição.
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            List[Dict]: Recursos formatados para template
        """
        resources = Resource.list_all(filters=filters)
        
        result = []
        for resource in resources:
            # Buscar owner
            owner = User.get_by_id(str(resource['owner_id']))
            
            result.append({
                'id': str(resource['_id']),
                'name': resource['name'],
                'description': resource['description'],
                'owner': owner['username'] if owner else 'Desconhecido',
                'created_at': resource['createdAt'].strftime('%d/%m/%Y %H:%M'),
                'updated_at': resource['updatedAt'].strftime('%d/%m/%Y %H:%M')
            })
        
        return result
```

**5. Template (`/app/templates/resources/list.html`):**
```html
{% extends "layout.html" %}

{% block title %}Recursos{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Recursos</h1>
        <a href="{{ url_for('resources.create_resource') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Novo Recurso
        </a>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    {% if resources %}
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Descrição</th>
                        <th>Proprietário</th>
                        <th>Criado em</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for resource in resources %}
                    <tr>
                        <td>{{ resource.name }}</td>
                        <td>{{ resource.description[:50] }}{% if resource.description|length > 50 %}...{% endif %}</td>
                        <td>{{ resource.owner }}</td>
                        <td>{{ resource.created_at }}</td>
                        <td>
                            <a href="{{ url_for('resources.view_resource', resource_id=resource.id) }}" 
                               class="btn btn-sm btn-info">
                                <i class="bi bi-eye"></i> Ver
                            </a>
                            <a href="{{ url_for('resources.edit_resource', resource_id=resource.id) }}" 
                               class="btn btn-sm btn-warning">
                                <i class="bi bi-pencil"></i> Editar
                            </a>
                            {% if current_user.role in ['admin', 'super_admin'] %}
                            <button class="btn btn-sm btn-danger" 
                                    onclick="deleteResource('{{ resource.id }}')">
                                <i class="bi bi-trash"></i> Deletar
                            </button>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-info">
            Nenhum recurso encontrado. <a href="{{ url_for('resources.create_resource') }}">Criar primeiro recurso</a>
        </div>
    {% endif %}
</div>

<script>
function deleteResource(resourceId) {
    if (!confirm('Tem certeza que deseja deletar este recurso?')) {
        return;
    }
    
    fetch(`/resources/delete/${resourceId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        alert('Erro ao deletar recurso');
        console.error(error);
    });
}
</script>
{% endblock %}
```

**6. Teste (`/tests/unit/test_resource_service.py`):**
```python
import pytest
from app.services.resource_service import ResourceService
from app.models.resource import Resource
from app.models.user import User

class TestResourceService:
    """Testes para ResourceService"""
    
    def test_validate_resource_data_valid(self):
        """Deve validar dados válidos"""
        valid, error = ResourceService.validate_resource_data(
            name="Test Resource",
            description="A valid description"
        )
        assert valid is True
        assert error is None
    
    def test_validate_resource_data_short_name(self):
        """Deve rejeitar nome muito curto"""
        valid, error = ResourceService.validate_resource_data(
            name="ab",
            description="Valid description"
        )
        assert valid is False
        assert "pelo menos 3 caracteres" in error
    
    def test_validate_resource_data_long_name(self):
        """Deve rejeitar nome muito longo"""
        valid, error = ResourceService.validate_resource_data(
            name="a" * 101,
            description="Valid description"
        )
        assert valid is False
        assert "no máximo 100 caracteres" in error
    
    def test_validate_resource_data_no_description(self):
        """Deve rejeitar descrição vazia"""
        valid, error = ResourceService.validate_resource_data(
            name="Valid Name",
            description=""
        )
        assert valid is False
        assert "obrigatória" in error
    
    @pytest.mark.usefixtures("app")
    def test_create_resource_success(self, sample_user):
        """Deve criar recurso com sucesso"""
        success, result = ResourceService.create_resource(
            name="Test Resource",
            description="Test description",
            owner_id=str(sample_user['_id'])
        )
        
        assert success is True
        assert result is not None
        
        # Limpar
        Resource.delete(result, soft=False)
    
    @pytest.mark.usefixtures("app")
    def test_create_resource_invalid_owner(self):
        """Deve falhar com owner inválido"""
        success, error = ResourceService.create_resource(
            name="Test Resource",
            description="Test description",
            owner_id="507f1f77bcf86cd799439011"  # ID inexistente
        )
        
        assert success is False
        assert "não encontrado" in error
    
    @pytest.mark.usefixtures("app")
    def test_user_can_access_resource_admin(self, sample_admin, sample_resource):
        """Admin deve poder acessar qualquer recurso"""
        can_access = ResourceService.user_can_access_resource(
            user_id=str(sample_admin['_id']),
            resource_id=str(sample_resource['_id']),
            user_role='admin'
        )
        assert can_access is True
    
    @pytest.mark.usefixtures("app")
    def test_user_can_access_resource_owner(self, sample_user, sample_resource):
        """Owner deve poder acessar próprio recurso"""
        can_access = ResourceService.user_can_access_resource(
            user_id=str(sample_user['_id']),
            resource_id=str(sample_resource['_id']),
            user_role='client'
        )
        # Assumindo que sample_resource pertence a sample_user
        assert can_access is True
    
    @pytest.mark.usefixtures("app")
    def test_user_cannot_access_other_resource(self, sample_user, other_user_resource):
        """Client não deve poder acessar recurso de outro"""
        can_access = ResourceService.user_can_access_resource(
            user_id=str(sample_user['_id']),
            resource_id=str(other_user_resource['_id']),
            user_role='client'
        )
        assert can_access is False
```

---

## 📌 Resumo para o GitHub Copilot

Ao trabalhar neste projeto:

1. **Sempre siga a arquitetura MVC + Services** estabelecida
2. **Use type hints** em todo o código Python
3. **Escreva docstrings** descritivas para funções públicas
4. **Implemente testes** para todo código novo
5. **Documente endpoints** no Swagger/OpenAPI
6. **Valide entradas** de usuários com Pydantic
7. **Audite ações** sensíveis com AuditService
8. **Verifique permissões** com decorators RBAC
9. **Trate exceções** apropriadamente
10. **Siga convenções** de código estabelecidas

**O objetivo é código limpo, testável, seguro e bem documentado que se integre perfeitamente com a arquitetura existente.**

---

Estas instruções devem ajudar o GitHub Copilot a gerar sugestões mais alinhadas com a arquitetura, padrões de código, e práticas de desenvolvimento do projeto Client Manager.