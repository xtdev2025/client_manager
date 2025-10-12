# Instruções para o GitHub Copilot

Este arquivo contém instruções específicas para o GitHub Copilot ajudar no desenvolvimento do projeto **Client Manager**, uma aplicação Flask com MongoDB que implementa um sistema MVC + Services para gerenciamento de clientes com múltiplas funcionalidades empresariais.

## � Contexto do Projeto Atual

### Sistema xPages
O Client Manager faz parte de um ecossistema maior chamado **xPages** que consiste em:

1. **client_manager** (porta 5000) - Sistema administrativo de gerenciamento
   - Gestão de clientes, planos, templates, domínios
   - Dashboard empresarial com estatísticas
   - Sistema de autenticação e RBAC
   - API documentada com Swagger/OpenAPI

2. **landpage** (porta 5001) - Sistema de renderização de páginas públicas
   - Renderiza templates para subdomínios (*.dev.7f000101.nip.io)
   - Captura de dados via formulários multipágina
   - Auto-navegação baseada em ordem de páginas
   - API de salvamento de campos (`/save-fields`)

### Infraestrutura Atual

- **MongoDB**: `localhost` (database: `clientmanager`)
- **Nginx**: Proxy reverso para `*.dev.7f000101.nip.io` → `localhost:5001`
- **nip.io**: DNS wildcard (qualquer.dev.7f000101.nip.io → 127.0.0.1)
- **Templates**: 3 templates BB (Banco do Brasil) com 19 páginas total
- **Subdomínios ativos**: wwbb01, wwbb02, wwbb03

### Estado Atual da Base de Dados

```javascript
// Collections MongoDB
admins: 3 documentos (superadmin, admin1, admin2)
plans: 3 documentos (Basic R$29.90, Standard R$79.90, Premium R$199.90)
templates: 3 documentos (BB Fluxo Completo 7pg, BB Sem CPF 6pg, BB CPF e Senha 6pg)
field_types: 8 documentos (text, email, cpf, phone, etc)
domains: 1 documento (dev.7f000101.nip.io)
clients: 3 documentos (cliente1, cliente2, cliente3)
client_domains: 3 documentos (wwbb01, wwbb02, wwbb03)
```

### Arquivos Importantes

- **`app/db_init.py`** - Inicialização do banco (criado via heredoc para evitar corrupção)
- **`app/templates_data.py`** - Definições de templates separadas (23,792 linhas de HTML)
- **`landpage/app/routes/main.py`** - Renderização de páginas com auto-detecção da primeira página
- **`docs/INDEX.md`** - Índice completo da documentação
- **`SISTEMA_COMPLETO.md`** - Documentação detalhada do sistema xPages

## �🏗️ Arquitetura do Projeto

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

### Padrões de Template Externos

O sistema usa **templates separados em arquivo Python** (`templates_data.py`) para:
- Evitar poluição de código
- Facilitar manutenção de HTML
- Permitir versionamento separado
- Melhorar organização do projeto

```python
# app/templates_data.py
BB_FLUXO_COMPLETO_PAGES = [
    {
        "id": "page_cpf",
        "name": "Validação de CPF",
        "title": "🏦 Banco do Brasil",
        "type": "capture",
        "order": 1,
        "field_type": "cpf",
        "content": "<!-- HTML da página -->"
    },
    # ... mais páginas
]

def get_all_templates():
    return [
        {"name": "BB - Fluxo Completo", "pages": BB_FLUXO_COMPLETO_PAGES},
        # ... mais templates
    ]
```

## 📋 Convenções de Código

### 🚨 Problemas Comuns e Soluções

#### 1. Erro com `@lru_cache` em funções sem parâmetros
**Problema**: `@lru_cache` não funciona corretamente em funções sem argumentos, pois o cache não consegue diferenciar chamadas.

```python
# ❌ EVITAR
@lru_cache(maxsize=32)
def get_stats():
    return {"total": 100}

# ✅ CORRETO
def get_stats():
    """Stats sem cache ou usar cache manual"""
    return {"total": 100}
```

#### 2. Variáveis Jinja2 Undefined
**Problema**: Template recebe `UndefinedError` quando variável não está no contexto.

```python
# ❌ EVITAR - Esquecer de passar variável
context = {
    "user": user,
    "stats": stats
    # recent_logins não está aqui!
}
return BaseView.render("template.html", **context)

# ✅ CORRETO - Passar todas as variáveis usadas no template
context = {
    "user": user,
    "stats": stats,
    "recent_logins": recent_logins,  # Incluir todas!
    "plan_distribution": plan_distribution,
}
return BaseView.render("template.html", **context)
```

**Checklist para Views**:
1. ✅ Ler o template e identificar todas as variáveis usadas
2. ✅ Garantir que todas estão no contexto
3. ✅ Usar valores padrão (lista vazia, dict vazio) para evitar None
4. ✅ Adicionar comentários sobre variáveis obrigatórias

#### 3. Corrupção de Arquivos com Docstrings Complexas
**Problema**: Criar arquivos Python com docstrings contendo caracteres especiais pode causar corrupção.

```bash
# ❌ EVITAR - create_file com docstrings complexas
create_file("file.py", content="def func():\n    '''Docstring com 'aspas' e \"mais aspas\"'''")

# ✅ CORRETO - Usar heredoc para arquivos complexos
cat > file.py << 'ENDFILE'
def func():
    """Docstring simples sem problemas"""
    pass
ENDFILE
```

#### 4. Inicialização do Banco de Dados
**Padrão Atual**: Usar módulo estruturado `db_init.py` com dados externos

```python
# app/db_init.py
from app.templates_data import get_all_templates

def initialize_db():
    """Inicializa banco com verificação de existência"""
    print("INICIANDO CONFIGURACAO DO BANCO DE DADOS")
    
    # Sempre verificar antes de criar
    if mongo.db.admins.count_documents({}) == 0:
        create_admins()
    else:
        print("Administradores ja existem")
    
    # ... outras inicializações
```

**Regras**:
- ✅ Verificar existência antes de criar (`count_documents`)
- ✅ Usar templates externos (`templates_data.py`)
- ✅ Sempre usar `datetime.utcnow()` para timestamps
- ✅ Bcrypt para senhas (nunca plaintext)
- ✅ Print de resumo ao final

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

### 🐛 Debugging: Passo a Passo

#### Problema: Dashboard com erro Jinja2 UndefinedError

**Fluxo de Debugging**:
1. **Ler o erro completo** - Identificar variável e template
   ```
   jinja2.exceptions.UndefinedError: 'stats' is undefined
   File: admin_enterprise.html, line 38: {{ stats.total_clients }}
   ```

2. **Verificar Controller** - Onde a variável é criada?
   ```python
   # dashboard.py linha 73
   stats = _get_admin_stats_cached()
   ```

3. **Verificar View** - Variável está no contexto?
   ```python
   # dashboard_view.py
   context = {
       "user": user,
       # "stats": stats,  ← FALTANDO!
   }
   ```

4. **Aplicar Fix** - Adicionar ao contexto
   ```python
   context = {
       "user": user,
       "stats": stats,  # ✅ CORRIGIDO
   }
   ```

5. **Verificar Template** - Quais outras variáveis são usadas?
   ```bash
   grep -E "\{\{.*\}\}" template.html | grep -v "url_for"
   ```

6. **Testar** - Reiniciar servidor (Flask debug mode faz auto-reload)

#### Problema: Servidor não Inicia ou Porta em Uso

**Diagnóstico**:
```bash
# 1. Verificar processos Python rodando
ps aux | grep "[p]ython.*run.py"

# 2. Verificar porta 5000
netstat -tlnp | grep 5000

# 3. Matar processos duplicados
pkill -9 -f "python.*run.py"

# 4. Limpar e reiniciar
cd /home/rootkit/Apps/xPages/client_manager
python run.py > /tmp/client_manager.log 2>&1 &

# 5. Verificar logs
tail -f /tmp/client_manager.log
```

#### Problema: MongoDB Connection Error

**Checklist**:
1. ✅ MongoDB está rodando? `systemctl status mongod`
2. ✅ Porta 27017 acessível? `nc -zv localhost 27017`
3. ✅ Config correta? Verificar `config.py`:
   ```python
   MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/clientmanager')
   ```
4. ✅ Credenciais? Se usar auth, verificar `.env`

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

### 🚀 Comandos Úteis do Projeto

#### Inicialização do Sistema
```bash
# Client Manager
cd /home/rootkit/Apps/xPages/client_manager
python run.py > /tmp/client_manager.log 2>&1 &

# Landpage
cd /home/rootkit/Apps/xPages/landpage
python run.py > /tmp/landpage.log 2>&1 &

# Ver logs em tempo real
tail -f /tmp/client_manager.log
tail -f /tmp/landpage.log
```

#### MongoDB Management
```bash
# Entrar no MongoDB shell
mongosh clientmanager

# Queries úteis
db.admins.find({}, {username: 1, role: 1})
db.templates.countDocuments()
db.client_domains.find({}, {subdomain: 1, template_id: 1})

# Limpar coleção específica
db.infos.deleteMany({})

# Backup
mongodump --db=clientmanager --out=/tmp/backup

# Restore
mongorestore --db=clientmanager /tmp/backup/clientmanager
```

#### Teste de Subdomínios via Nginx
```bash
# Testar resposta HTTP
curl -I http://wwbb01.dev.7f000101.nip.io

# Testar conteúdo
curl -s http://wwbb01.dev.7f000101.nip.io | grep -E "(title|<h1)"

# Testar todos os subdomínios
for sub in wwbb01 wwbb02 wwbb03; do
    echo "=== $sub ==="
    curl -s http://$sub.dev.7f000101.nip.io | grep "<title>"
done
```

#### Desenvolvimento
```bash
# Rodar testes
cd /home/rootkit/Apps/xPages/client_manager
pytest tests/ -v

# Coverage
pytest tests/ --cov=app --cov-report=html

# Linting
flake8 app/ --max-line-length=100

# Criar migration (se usar Alembic)
flask db migrate -m "Descrição da mudança"
flask db upgrade
```

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
- **PyMongo** - Driver MongoDB
- **Flask-Login** - Gerenciamento de sessões e autenticação
- **python-dotenv** - Variáveis de ambiente
- **Bcrypt** - Hashing de senhas (NUNCA usar plaintext!)

### Validação e API
- **Pydantic 2.5.0** - Validação de dados e schemas
- **apispec 6.3.0** - Geração de especificação OpenAPI
- **flask-swagger-ui 4.11.1** - Interface Swagger UI
- **apispec-webframeworks 0.5.2** - Integração Flask + APISpec

### Segurança
- **Flask-Limiter 3.5.0** - Rate limiting
- **Flask-WTF** - Proteção CSRF

### Testes
- **pytest 7.4.3** - Framework de testes
- **pytest-cov 4.1.0** - Coverage de testes

### 🔧 Configuração Atual

```python
# config.py (exemplo)
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/clientmanager')
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
```

Ao usar estas bibliotecas, **sempre siga os padrões existentes** no projeto.

## 🎨 Estrutura de Templates

### Landpage: Sistema de Auto-Navegação

O sistema landpage tem um padrão especial para navegação automática:

```python
# landpage/app/routes/main.py
@main.route('/<subdomain>/', defaults={'page_id': None})
@main.route('/<subdomain>/<page_id>')
def render_page(subdomain, page_id=None):
    # Se page_id é None, encontra primeira página por order
    if page_id is None:
        pages = template_doc.get("pages", [])
        if pages:
            first_page = min(pages, key=lambda x: x.get("order", 999))
            page_id = first_page["id"]
    
    # Renderizar página específica
    return render_template('page.html', page_data=page_data)
```

**Características**:
- Auto-detecção da primeira página (menor `order`)
- `page_id` opcional na URL
- Redirect automático para primeira página
- `window.pageData.nextPage` populado no cliente

### Client Manager: Templates Administrativos

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

### 📂 Documentação Interna (Reorganizada!)

**Raiz** (apenas essenciais):
- [`README.md`](../README.md) - Overview do projeto
- [`CHANGELOG.md`](../CHANGELOG.md) - Histórico de versões
- [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) - Código de conduta

**docs/** (toda documentação técnica):
- **[`INDEX.md`](../docs/INDEX.md)** - 🆕 Índice completo da documentação
- [`ARCHITECTURE.md`](../docs/ARCHITECTURE.md) - Arquitetura completa do sistema
- [`API_QUICK_REFERENCE.md`](../docs/API_QUICK_REFERENCE.md) - Referência rápida da API
- [`SWAGGER_IMPLEMENTATION.md`](../docs/SWAGGER_IMPLEMENTATION.md) - Implementação Swagger/OpenAPI
- [`ROUTES_DOCUMENTATION.md`](../docs/ROUTES_DOCUMENTATION.md) - Documentação de todas as rotas
- [`TEMPLATE_FIELDS_SYSTEM.md`](../docs/TEMPLATE_FIELDS_SYSTEM.md) - Sistema de templates e campos
- [`DASHBOARD_README.md`](../docs/DASHBOARD_README.md) - Guia do dashboard administrativo
- [`SCRIPTS_DOCUMENTATION.md`](../docs/SCRIPTS_DOCUMENTATION.md) - Documentação dos scripts
- [`AWS_DEPLOYMENT.md`](../docs/AWS_DEPLOYMENT.md) - Deploy completo na AWS
- [`AZURE_DEPLOYMENT.md`](../docs/AZURE_DEPLOYMENT.md) - Deploy completo no Azure
- [`MIGRATION_GUIDE.md`](../docs/MIGRATION_GUIDE.md) - Guia de migração
- [`MODERNIZATION_SUMMARY.md`](../docs/MODERNIZATION_SUMMARY.md) - Resumo da modernização

**Raiz do workspace xPages**:
- [`SISTEMA_COMPLETO.md`](../../SISTEMA_COMPLETO.md) - Documentação completa do sistema xPages

### 🔗 Acessos Rápidos

**Desenvolvimento Local**:
- Client Manager: http://localhost:5000
- Landpage: http://localhost:5001
- Swagger UI: http://localhost:5000/api/docs
- Dashboard Admin: http://localhost:5000/dashboard

**Subdomínios (via nginx)**:
- wwbb01: http://wwbb01.dev.7f000101.nip.io (BB Fluxo Completo - 7 páginas)
- wwbb02: http://wwbb02.dev.7f000101.nip.io (BB Sem CPF - 6 páginas)
- wwbb03: http://wwbb03.dev.7f000101.nip.io (BB CPF e Senha - 6 páginas)

### 📝 Credenciais de Desenvolvimento

**Admins**:
```
superadmin / SuperAdmin123!
admin1 / Admin123!
admin2 / Admin123!
```

**Clientes**:
```
cliente1 / Senha123!
cliente2 / Senha123!
cliente3 / Senha123!
```

### Links Externos Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [pytest Documentation](https://docs.pytest.org/)

## 🎯 Diretrizes de Implementação

### ⚠️ Erros Críticos a Evitar

1. **NUNCA usar `@lru_cache` em funções sem parâmetros**
   - Problema: Cache não consegue diferenciar chamadas
   - Solução: Remover decorator ou implementar cache manual

2. **SEMPRE verificar variáveis no contexto Jinja2**
   - Problema: `UndefinedError` quebra a página
   - Solução: Grep no template antes de renderizar
   ```bash
   grep -E "\{\{.*\}\}" template.html | grep -v "url_for\|csrf_token"
   ```

3. **NUNCA criar arquivos Python grandes com create_file**
   - Problema: Corrupção de arquivos com docstrings complexas
   - Solução: Usar heredoc para arquivos grandes
   ```bash
   cat > file.py << 'ENDFILE'
   # conteúdo aqui
   ENDFILE
   ```

4. **SEMPRE usar bcrypt para senhas**
   - Problema: Segurança comprometida
   - Solução: `bcrypt.hashpw(password.encode(), bcrypt.gensalt())`

5. **SEMPRE verificar existência antes de criar no MongoDB**
   - Problema: Duplicatas no banco
   - Solução: `if collection.count_documents({}) == 0: create()`

6. **SEMPRE passar TODAS as variáveis que o template usa**
   - Problema: Template quebra com UndefinedError
   - Solução: Fazer checklist de variáveis do template

### Ao Criar Código, Sempre:

1. ✅ **Adicionar type hints** em todos os parâmetros e retornos
2. ✅ **Escrever docstrings** descritivas
3. ✅ **Validar entradas** de usuários
4. ✅ **Tratar exceções** apropriadamente com try/except
5. ✅ **Usar logging** para debug (não apenas print)
6. ✅ **Seguir princípios SOLID**
7. ✅ **Escrever testes** para novo código
8. ✅ **Documentar no Swagger** se for endpoint API
9. ✅ **Auditar ações** sensíveis via AuditService
10. ✅ **Verificar permissões** (RBAC) com decorators
11. ✅ **Usar datetime.utcnow()** para timestamps (nunca now())
12. ✅ **Verificar None** antes de acessar propriedades

### Ao Revisar Código, Verificar:

1. ✅ Segue convenções do projeto
2. ✅ Tem testes adequados
3. ✅ Documentação está completa
4. ✅ Não introduz vulnerabilidades
5. ✅ Performance está otimizada
6. ✅ Não quebra funcionalidades existentes
7. ✅ Logs de auditoria apropriados
8. ✅ Tratamento de erros robusto
9. ✅ Todas as variáveis Jinja2 estão no contexto
10. ✅ Não usa `@lru_cache` incorretamente

### 🔍 Checklist de Debug

Quando encontrar um erro:

1. **Ler erro completo** - Não pular para conclusões
2. **Identificar o arquivo e linha** - Ir direto ao problema
3. **Verificar contexto** - Ler 10 linhas antes e depois
4. **Procurar padrões** - Já vimos este erro antes?
5. **Testar hipótese** - Fazer uma mudança de cada vez
6. **Verificar logs** - Sempre olhar `/tmp/*.log`
7. **Testar isoladamente** - Reproduzir em ambiente limpo
8. **Documentar solução** - Atualizar este arquivo se necessário

## 💡 Exemplos Práticos

### Exemplo 1: Controller com View Context Correto

```python
# app/controllers/dashboard.py
@dashboard.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    """Dashboard administrativo com todas as variáveis necessárias"""
    user = User.get_by_id(current_user.id)
    
    # Coletar todas as estatísticas
    stats = _get_admin_stats_cached()
    stats["inactive_clients"] = stats["total_clients"] - stats["active_clients"]
    
    # Coletar dados auxiliares
    recent_logins = LoginLog.get_recent_logins(limit=10)
    plan_distribution = _get_plan_distribution_cached()
    client_activity = Client.get_recent_activity()
    new_clients = Client.count_new_this_month()
    new_infos = Info.count_new_this_month()
    recent_clicks = Click.get_recent(limit=10)
    
    # ✅ IMPORTANTE: Passar TODAS as variáveis que o template usa
    return DashboardView.render_admin_dashboard(
        user=user,
        stats=stats,                      # Template usa {{ stats.total_clients }}
        recent_logins=recent_logins,      # Template usa {% for login in recent_logins %}
        plan_distribution=plan_distribution,
        client_activity=client_activity,
        new_clients=new_clients,          # Template usa {{ new_clients }}
        new_infos=new_infos,              # Template usa {{ new_infos }}
        recent_clicks=recent_clicks       # Template usa {{ recent_clicks|length }}
    )
```

```python
# app/views/dashboard_view.py
class DashboardView(BaseView):
    @staticmethod
    def render_admin_dashboard(user, stats, recent_logins, plan_distribution,
                               client_activity, new_clients, new_infos, recent_clicks=None):
        """Renderiza dashboard com TODAS as variáveis necessárias"""
        
        # ✅ Contexto completo incluindo todas as variáveis
        context = {
            "user": user,
            "user_type": "admin",
            "stats": stats,                    # Usado no template
            "recent_logins": recent_logins,    # Usado no template
            "plan_distribution": plan_distribution,
            "client_activity": client_activity,
            "new_clients": new_clients,
            "new_infos": new_infos,
            "recent_clicks": recent_clicks or [],
            # Variáveis legacy para compatibilidade
            "client_count": stats.get("total_clients", 0),
            "active_clients": stats.get("active_clients", 0),
        }
        
        return BaseView.render("dashboard/admin_enterprise.html", **context)
```

### Exemplo 2: Inicialização Segura do Banco

```python
# app/db_init.py
from datetime import datetime
import bcrypt
from app import mongo
from app.templates_data import get_all_templates

def initialize_db():
    """
    Inicializa banco de dados com verificação de existência.
    ✅ Segue padrão: verificar antes de criar
    """
    print("\n" + "="*80)
    print("INICIANDO CONFIGURACAO DO BANCO DE DADOS")
    print("="*80 + "\n")
    
    db = mongo.db
    
    # ✅ SEMPRE verificar existência
    if db.admins.count_documents({}) == 0:
        create_admins()
    else:
        print("Administradores ja existem")
    
    if db.plans.count_documents({}) == 0:
        create_plans()
    else:
        print("Planos ja existem")
    
    # Templates vem de arquivo externo
    if db.templates.count_documents({}) == 0:
        create_templates()
    else:
        print("Templates ja existem")
    
    print_summary()

def create_admins():
    """Cria administradores com senhas criptografadas"""
    db = mongo.db
    
    admins_data = [
        {
            "username": "superadmin",
            "password": "SuperAdmin123!",  # Será hashado
            "role": "super_admin",
            "email": "superadmin@example.com"
        },
        # ... mais admins
    ]
    
    for admin_data in admins_data:
        # ✅ SEMPRE usar bcrypt para senhas
        password_hash = bcrypt.hashpw(
            admin_data["password"].encode(),
            bcrypt.gensalt()
        )
        
        admin = {
            "username": admin_data["username"],
            "password": password_hash,
            "role": admin_data["role"],
            "email": admin_data["email"],
            "status": "active",
            "createdAt": datetime.utcnow(),  # ✅ UTC!
            "updatedAt": datetime.utcnow()
        }
        
        db.admins.insert_one(admin)
    
    print(f"✓ {len(admins_data)} administradores criados")

def create_templates():
    """Cria templates a partir de arquivo externo"""
    db = mongo.db
    
    # ✅ Templates em arquivo separado
    all_templates = get_all_templates()
    
    for template_data in all_templates:
        template = {
            "name": template_data["name"],
            "description": template_data.get("description", ""),
            "pages": template_data["pages"],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        db.templates.insert_one(template)
    
    print(f"✓ {len(all_templates)} templates criados")
```

### Exemplo 3: Tratamento de Erros Robusto

```python
# app/models/client.py
from typing import Tuple, Optional, Dict
from bson.objectid import ObjectId
from datetime import datetime

class Client:
    collection_name = 'clients'
    
    @staticmethod
    def create(username: str, email: str, plan_id: str) -> Tuple[bool, str]:
        """
        Cria novo cliente com validação e tratamento de erros.
        
        Returns:
            Tuple[bool, str]: (sucesso, id_ou_mensagem_erro)
        """
        try:
            # ✅ Validar entrada
            if not username or len(username) < 3:
                return False, "Username deve ter pelo menos 3 caracteres"
            
            if not email or '@' not in email:
                return False, "Email inválido"
            
            # ✅ Verificar duplicatas
            existing = mongo.db[Client.collection_name].find_one({
                "username": username
            })
            if existing:
                return False, "Username já existe"
            
            # ✅ Validar ObjectId
            try:
                plan_obj_id = ObjectId(plan_id)
            except Exception:
                return False, "Plan ID inválido"
            
            # Criar documento
            new_client = {
                "username": username,
                "email": email,
                "plan_id": plan_obj_id,
                "status": "active",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = mongo.db[Client.collection_name].insert_one(new_client)
            return True, str(result.inserted_id)
            
        except Exception as e:
            # ✅ Log do erro completo
            import traceback
            traceback.print_exc()
            return False, f"Erro ao criar cliente: {str(e)}"
```

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

### 🎯 Objetivo Principal
Ajudar no desenvolvimento do **Client Manager** (sistema xPages), fornecendo código que:
- ✅ Segue arquitetura MVC + Services
- ✅ É seguro (RBAC, validações, bcrypt)
- ✅ Tem tratamento de erros robusto
- ✅ Está documentado (docstrings, Swagger)
- ✅ É testável e mantível

### 🚨 Erros Críticos NUNCA Repetir

1. **`@lru_cache` em funções sem parâmetros** → Remover ou usar cache manual
2. **Variáveis Jinja2 faltando no contexto** → Grep template antes de renderizar
3. **Senhas em plaintext** → SEMPRE usar bcrypt
4. **Criar sem verificar existência** → `count_documents()` primeiro
5. **Arquivos grandes com create_file** → Usar heredoc
6. **Esquecer variáveis no View context** → Passar TODAS que o template usa

### 🔧 Estado Atual do Sistema

**Infraestrutura**:
- Client Manager: `localhost:5000` (Flask + MongoDB)
- Landpage: `localhost:5001` (Flask + Jinja2)
- MongoDB: `localhost:27017/clientmanager`
- Nginx: Proxy para `*.dev.7f000101.nip.io`

**Base de Dados**:
- 3 admins (superadmin, admin1, admin2)
- 3 planos (Basic, Standard, Premium)
- 3 templates BB (19 páginas total)
- 3 clientes e 3 subdomínios ativos

**Arquivos Importantes**:
- `app/db_init.py` - Inicialização estruturada
- `app/templates_data.py` - Definições de templates (23K linhas)
- `docs/INDEX.md` - Índice completo da documentação
- `SISTEMA_COMPLETO.md` - Documentação do ecossistema

### 🚀 Comandos Rápidos

```bash
# Iniciar servers
cd /home/rootkit/Apps/xPages/client_manager && python run.py &
cd /home/rootkit/Apps/xPages/landpage && python run.py &

# Ver logs
tail -f /tmp/client_manager.log
tail -f /tmp/landpage.log

# MongoDB
mongosh clientmanager
db.templates.find({}, {name: 1})

# Testes
pytest tests/ -v --cov=app

# Debug de subdomínios
curl -I http://wwbb01.dev.7f000101.nip.io
```

### 📚 Documentação Principal

1. **[docs/INDEX.md](../docs/INDEX.md)** - Início aqui!
2. **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - Arquitetura completa
3. **[API_QUICK_REFERENCE.md](../docs/API_QUICK_REFERENCE.md)** - Referência rápida
4. **[SISTEMA_COMPLETO.md](../../SISTEMA_COMPLETO.md)** - Sistema xPages completo

### 🎓 Princípios de Desenvolvimento

1. **Segurança primeiro** - RBAC, validações, bcrypt, auditoria
2. **Código limpo** - Type hints, docstrings, SOLID
3. **Testes sempre** - Coverage mínimo 80%
4. **Documentação completa** - Swagger, README, comentários
5. **Performance importa** - Cache inteligente, queries otimizadas
6. **Erros esperados** - Try/except robusto, mensagens claras

---

**O objetivo é código limpo, testável, seguro e bem documentado que se integre perfeitamente com a arquitetura existente do sistema xPages.**

---

*Última atualização: 12 de outubro de 2025*
*Estas instruções devem ajudar o GitHub Copilot a gerar sugestões mais alinhadas com a arquitetura, padrões de código, e práticas de desenvolvimento do projeto Client Manager.*