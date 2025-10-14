# 🌐 Routes Documentation

## Overview

O **Client Manager** é uma aplicação web Flask que utiliza **Server-Side Rendering (SSR)** com templates Jinja2.

**Não é uma API REST/JSON** - todas as rotas retornam HTML renderizado no servidor.

## Arquitetura

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────┐
│  Flask Application  │
│  (Server-Side)      │
├─────────────────────┤
│  • Controllers      │
│  • Services         │
│  • Models           │
│  • Templates        │
└──────┬──────────────┘
       │ MongoDB
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

## Tecnologias

- **Flask**: Framework web
- **Jinja2**: Template engine (SSR)
- **Flask-Login**: Autenticação de sessão
- **PyMongo**: MongoDB ODM
- **Flask-Bcrypt**: Hash de senhas
- **Flask-Limiter**: Rate limiting

## Estrutura de Rotas

### 🏠 Main (`/`)

**Blueprint:** `main`  
**Arquivo:** `app/controllers/main.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/` | GET | Página inicial | Público |
| `/dashboard` | GET | Dashboard principal | Autenticado |

---

### 🔐 Auth (`/auth`)

**Blueprint:** `auth`  
**Arquivo:** `app/controllers/auth.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/auth/login` | GET, POST | Login de usuários | Público |
| `/auth/logout` | GET | Logout | Autenticado |
| `/auth/register` | GET, POST | Registro de clientes | Público |
| `/auth/register_admin` | GET, POST | Registro de admins | Admin |
| `/auth/switch-role` | POST | Trocar entre Admin/Cliente | Autenticado |

---

### 👥 Clients (`/clients`)

**Blueprint:** `client`  
**Arquivo:** `app/controllers/client.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/clients/` | GET | Listar todos os clientes | Admin |
| `/clients/create` | GET, POST | Criar novo cliente | Admin |
| `/clients/edit/<id>` | GET, POST | Editar cliente | Admin |
| `/clients/delete/<id>` | POST | Deletar cliente | Admin |
| `/clients/view/<id>` | GET | Visualizar detalhes | Admin |
| `/clients/<id>/domains` | GET | Domínios do cliente | Admin |
| `/clients/<id>/domains/add` | POST | Adicionar domínio | Admin |
| `/clients/<id>/domains/<domain_id>/delete` | POST | Remover domínio | Admin |
| `/clients/<id>/domains/check` | POST | Verificar disponibilidade | Admin |

---

### 🧑‍💼 Client Portal (`/client`)

**Blueprint:** `client_domain_bp`  
**Arquivo:** `app/views/client_domain_view.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/client/my-domains` | GET | Meus domínios | Cliente |
| `/client/my-click-stats` | GET | Estatísticas de cliques | Cliente |
| `/client/my-infos` | GET | Informações bancárias | Cliente |
| `/client/my-change-password` | GET, POST | Alterar senha | Cliente |

---

### 👨‍💼 Admins (`/admins`)

**Blueprint:** `admin`  
**Arquivo:** `app/controllers/admin.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/admins/` | GET | Listar admins | Superadmin |
| `/admins/create` | GET, POST | Criar admin | Superadmin |
| `/admins/edit/<id>` | GET, POST | Editar admin | Superadmin |
| `/admins/delete/<id>` | POST | Deletar admin | Superadmin |
| `/admins/view/<id>` | GET | Visualizar admin | Superadmin |
| `/admins/logs` | GET | Logs de auditoria | Superadmin |
| `/admins/client-clicks/<client_id>` | GET | Clicks do cliente | Admin |
| `/admins/toggle-active/<id>` | POST | Ativar/Desativar | Superadmin |

---

### 📋 Plans (`/plans`)

**Blueprint:** `plan`  
**Arquivo:** `app/controllers/plan.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/plans/` | GET | Listar planos | Admin |
| `/plans/create` | GET, POST | Criar plano | Admin |
| `/plans/edit/<id>` | GET, POST | Editar plano | Admin |
| `/plans/delete/<id>` | POST | Deletar plano | Admin |
| `/plans/view/<id>` | GET | Visualizar plano | Admin |

---

### 📄 Templates (`/templates`)

**Blueprint:** `template`  
**Arquivo:** `app/controllers/template.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/templates/` | GET | Listar templates | Admin |
| `/templates/create` | GET, POST | Criar template | Admin |
| `/templates/edit/<id>` | GET, POST | Editar template | Admin |
| `/templates/delete/<id>` | POST | Deletar template | Admin |
| `/templates/view/<id>` | GET | Visualizar template | Admin |

---

### 🌍 Domains (`/domains`)

**Blueprint:** `domain`  
**Arquivo:** `app/controllers/domain.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/domains/` | GET | Listar domínios | Admin |
| `/domains/create` | GET, POST | Criar domínio | Admin |
| `/domains/edit/<id>` | GET, POST | Editar domínio | Admin |
| `/domains/delete/<id>` | POST | Deletar domínio | Admin |
| `/domains/view/<id>` | GET | Visualizar domínio | Admin |

---

### 📊 Infos (`/infos`)

**Blueprint:** `info`  
**Arquivo:** `app/controllers/info.py`

| Rota | Método | Descrição | Auth |
|------|--------|-----------|------|
| `/infos/` | GET | Listar infos bancárias | Admin |
| `/infos/create` | GET, POST | Criar info | Admin |
| `/infos/edit/<id>` | GET, POST | Editar info | Admin |
| `/infos/delete/<id>` | POST | Deletar info | Admin |
| `/infos/view/<id>` | GET | Visualizar info | Admin |

---

### 📢 Public Templates (`/template/*`)

> ⚠️ **Funcionalidade descontinuada:** As rotas públicas de template foram removidas.
> Documentação anterior foi mantida apenas para referência histórica.

---

## Autenticação

### Session-Based Authentication

A aplicação usa **Flask-Login** para gerenciar sessões de usuários.

```python
from flask_login import login_user, logout_user, login_required, current_user

# Login
login_user(user, remember=True)

# Logout
logout_user()

# Proteger rota
@login_required
def protected_route():
    return render_template('page.html')

# Usuário atual
current_user.username
current_user.is_admin
```

### Tipos de Usuário

1. **Cliente** - Acesso limitado ao portal do cliente
2. **Admin** - Gerenciamento completo
3. **Superadmin** - Gerenciamento de admins + tudo do Admin

### Decoradores

```python
from app.utils.decorators import admin_required, superadmin_required

@admin_required
def admin_only():
    pass

@superadmin_required
def superadmin_only():
    pass
```

---

## Rate Limiting

**Flask-Limiter** protege rotas sensíveis:

```python
from app import limiter

# Global: 200/dia, 50/hora
# Login: 5 tentativas/minuto
@limiter.limit("5 per minute")
@auth.route('/login', methods=['POST'])
def login():
    pass
```

---

## Templates (Jinja2)

### Estrutura

```
app/templates/
├── layout.html           # Base template
├── navbar.html           # Navigation
├── index.html            # Home
├── dashboard.html        # Dashboard
├── auth/
│   ├── login.html
│   └── register.html
├── clients/
│   ├── list.html
│   ├── create.html
│   └── edit.html
└── ...
```

### Exemplo de Renderização

**Controller:**

```python
from flask import render_template

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                         user=current_user,
                         stats=get_stats())
```

**Template:**

```jinja2
{% extends "layout.html" %}

{% block content %}
<h1>Bem-vindo, {{ user.username }}!</h1>
<p>Total de clientes: {{ stats.total_clients }}</p>
{% endblock %}
```

---

## Formulários

### Server-Side Validation

```python
from flask import request, flash, redirect

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Preencha todos os campos', 'error')
        return redirect('/auth/login')
    
    # Autenticar...
```

### CSRF Protection

```html
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- campos do formulário -->
</form>
```

---

## Serviços

### Camada de Negócios

```python
# app/services/client_service.py
from app.models.client import Client

class ClientService:
    @staticmethod
    def get_client_with_details(client_id):
        client = Client.find_by_id(client_id)
        plan = Plan.find_by_id(client.plan_id)
        domains = Domain.find_by_client(client_id)
        
        return {
            'client': client,
            'plan': plan,
            'domains': domains
        }
```

---

## Modelos (MongoDB)

### Estrutura

```python
# app/models/client.py
class Client:
    collection = mongo.db.clients
    
    @classmethod
    def find_by_username(cls, username):
        return cls.collection.find_one({'username': username})
    
    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)
```

---

## Boas Práticas

### 1. Controllers Limpos

✅ **Bom:**

```python
@client.route('/clients/')
@admin_required
def list_clients():
    clients = ClientService.get_all_with_plans()
    return render_template('clients/list.html', clients=clients)
```

❌ **Ruim:**

```python
@client.route('/clients/')
@admin_required
def list_clients():
    # Muita lógica no controller
    clients = mongo.db.clients.find()
    # ... processamento complexo ...
    return render_template('clients/list.html', clients=clients)
```

### 2. Sempre use flash messages

```python
flash('Cliente criado com sucesso!', 'success')
flash('Erro ao salvar dados', 'error')
flash('Atenção: senha fraca', 'warning')
```

### 3. Redirect após POST

```python
@client.route('/clients/create', methods=['POST'])
def create_client_post():
    # Processar dados...
    return redirect(url_for('client.list_clients'))  # PRG Pattern
```

---

## Testando Localmente

```bash
# Iniciar aplicação
python run.py

# Acessar
http://localhost:5000

# Rotas principais
http://localhost:5000/              # Home
http://localhost:5000/auth/login    # Login
http://localhost:5000/dashboard     # Dashboard
```

---

## Próximos Passos

Se no futuro você precisar de uma **API REST/JSON**:

1. Criar novo blueprint `api_v1`
2. Usar `jsonify()` para retornar JSON
3. Implementar autenticação JWT ou API keys
4. Adicionar versionamento (`/api/v1/...`)
5. Documentar com OpenAPI/Swagger

Por enquanto, **SSR com Flask templates** é a abordagem ideal para este projeto! ✅

---

## Links Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [PyMongo](https://pymongo.readthedocs.io/)

---

**Última atualização:** 11 de outubro de 2025  
**Versão:** 1.0 (Server-Side Rendering)
