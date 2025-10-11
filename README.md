# 🎯 Client Manager - Sistema de Gerenciamento de Clientes

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.6.0-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/license-ISC-blue.svg)](LICENSE)

Sistema completo de gerenciamento de clientes com autenticação robusta, controle de acesso baseado em funções (RBAC), gestão de planos de assinatura, templates personalizados, domínios e informações bancárias.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Modelos de Dados](#-modelos-de-dados)
- [Rotas da API](#-rotas-da-api)
- [Desenvolvimento](#-desenvolvimento)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

---

## 🎯 Visão Geral

O **Client Manager** é uma aplicação web desenvolvida em Flask que permite gerenciar clientes, administradores, planos de assinatura, templates e domínios de forma integrada. O sistema implementa autenticação segura, controle de permissões hierárquico e auditoria de acessos.

### Principais Características

- 🔐 **Autenticação Segura**: Sistema completo de login/logout com hash de senhas (bcrypt)
- 👥 **RBAC (Role-Based Access Control)**: Controle granular de permissões (super_admin, admin, client)
- 📊 **Dashboard Dinâmico**: Painéis específicos para cada tipo de usuário
- 📝 **Gestão de Clientes**: CRUD completo com status, planos e informações detalhadas
- 💳 **Informações Bancárias**: Gerenciamento seguro de dados bancários por cliente
- 🌐 **Gestão de Domínios**: Controle de domínios com integração Cloudflare e SSL
- 📋 **Templates Customizáveis**: Sistema de templates para personalização
- 💰 **Planos de Assinatura**: Gestão completa de planos com duração e preços
- 📅 **Controle de Expiração**: Monitoramento automático de vencimento de planos
- 📜 **Auditoria de Acessos**: Registro completo de logins (IP, user-agent, timestamp)

---

## ✨ Funcionalidades

### 🔑 Autenticação e Autorização

- ✅ Login seguro com validação de credenciais
- ✅ Logout com limpeza de sessão
- ✅ Decoradores de permissão (@admin_required, @super_admin_required)
- ✅ Registro de novos administradores (somente super_admin)
- ✅ Sistema de sessões persistentes

### 👤 Gestão de Usuários

#### Super Administradores
- Gerenciamento completo de administradores
- Criação, edição e exclusão de admins
- Proteção contra exclusão do último super_admin
- Acesso total ao sistema

#### Administradores
- Gestão de clientes e planos
- Visualização de informações
- Acesso restrito (não pode gerenciar outros admins)

#### Clientes
- Dashboard personalizado
- Visualização de informações próprias
- Controle de status de conta (active/inactive)
- Monitoramento de expiração de plano

### 📊 Gestão de Clientes

- ✅ CRUD completo de clientes
- ✅ Associação com planos de assinatura
- ✅ Controle de status (ativo/inativo)
- ✅ Gestão de templates por cliente
- ✅ Gerenciamento de domínios vinculados
- ✅ Datas de ativação e expiração de planos
- ✅ Cálculo automático de vencimentos

### 💰 Gestão de Planos

- ✅ Criação de planos personalizados
- ✅ Configuração de preço e duração (em dias)
- ✅ Descrição detalhada de benefícios
- ✅ Validação de uso antes de exclusão
- ✅ Planos padrão pré-configurados (Basic, Standard, Premium)

### 📋 Sistema de Templates

- ✅ Templates personalizáveis para clientes
- ✅ Armazenamento de conteúdo estruturado (JSON)
- ✅ Status ativo/inativo
- ✅ Versionamento por timestamps

### 🌐 Gestão de Domínios

- ✅ Cadastro de domínios
- ✅ Integração com Cloudflare (API, email, senha)
- ✅ Configuração de SSL
- ✅ Limite de domínios por registro
- ✅ Associação de domínios com clientes
- ✅ Validação de uso antes de exclusão

### 💳 Informações Bancárias

- ✅ Cadastro de múltiplas contas por cliente
- ✅ Armazenamento de agência, conta, senhas (senha completa, 6 dígitos, 4 dígitos)
- ✅ Campo de anotações para observações
- ✅ Controle de saldo
- ✅ Associação com templates e domínios
- ✅ Status ativo/inativo por registro

### 📜 Auditoria e Logs

- ✅ Registro de todos os logins
- ✅ Armazenamento de IP de origem
- ✅ Captura de User-Agent
- ✅ Timestamp preciso (UTC)
- ✅ Histórico por usuário
- ✅ Logs de eventos do sistema

---

## 🏗️ Arquitetura

O projeto segue o padrão **MVC (Model-View-Controller)** com separação clara de responsabilidades:

### 📦 Estrutura MVC

```
┌─────────────────────────────────────────────┐
│              APPLICATION LAYER              │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   VIEW   │  │CONTROLLER│  │  MODEL   │  │
│  │          │  │          │  │          │  │
│  │ Templates│◄─┤  Routes  │◄─┤   Data   │  │
│  │   HTML   │  │  Logic   │  │  MongoDB │  │
│  │   CSS    │  │  Auth    │  │  Schema  │  │
│  │   JS     │  │  CRUD    │  │  CRUD    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                             │
└─────────────────────────────────────────────┘
         │               │               │
         ▼               ▼               ▼
    Jinja2          Flask Blueprints   PyMongo
```

### 🗂️ Camadas do Sistema

#### **Models** (`app/models/`)
- Definição das estruturas de dados
- Interação com o MongoDB
- Validações de negócio
- Operações CRUD
- **Classes**: `User`, `Admin`, `Client`, `Plan`, `Template`, `Domain`, `Info`, `LoginLog`

#### **Controllers** (`app/controllers/`)
- Processamento de requisições HTTP
- Lógica de negócio
- Validação de permissões
- Manipulação de formulários
- **Blueprints**: `auth`, `admin`, `client`, `plan`, `template`, `domain`, `info`, `main`

#### **Views** (`app/views/`)
- Renderização de templates
- Preparação de dados para exibição
- Camada de apresentação
- **Classes**: `AuthView`, `AdminView`, `ClientView`, `PlanView`, `TemplateView`, `DomainView`, `InfoView`

#### **Templates** (`app/templates/`)
- Interface visual em HTML
- Herança de layouts (Jinja2)
- Componentes reutilizáveis (navbar, dashboard)
- Formulários dinâmicos

---

## 🛠️ Tecnologias

### Backend
- **[Flask 2.3.3](https://flask.palletsprojects.com/)** - Framework web minimalista e poderoso
- **[PyMongo 4.6.0](https://pymongo.readthedocs.io/)** - Driver oficial MongoDB para Python
- **[Flask-PyMongo 2.3.0](https://flask-pymongo.readthedocs.io/)** - Integração Flask + MongoDB
- **[Flask-Login 0.6.2](https://flask-login.readthedocs.io/)** - Gerenciamento de sessões de usuário
- **[Flask-Bcrypt 1.0.1](https://flask-bcrypt.readthedocs.io/)** - Hashing seguro de senhas
- **[Flask-WTF 1.2.1](https://flask-wtf.readthedocs.io/)** - Integração com formulários e CSRF
- **[Python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)** - Gerenciamento de variáveis de ambiente
- **[Email-validator 2.1.0](https://pypi.org/project/email-validator/)** - Validação de endereços de e-mail

### Frontend
- **[Bootstrap 5](https://getbootstrap.com/)** - Framework CSS responsivo
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine
- **JavaScript Vanilla** - Scripts customizados

### Banco de Dados
- **[MongoDB 4.6+](https://www.mongodb.com/)** - Banco de dados NoSQL orientado a documentos

### Ferramentas de Desenvolvimento
- **[Husky 9.1.7](https://typicode.github.io/husky/)** - Git hooks para qualidade de código
- **[Flake8](https://flake8.pycqa.org/)** - Linter Python
- **[Git](https://git-scm.com/)** - Controle de versão

---

## 🚀 Instalação

### Pré-requisitos

Certifique-se de ter instalado:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **MongoDB 4.6+** - [Download](https://www.mongodb.com/try/download/community)
- **Git** - [Download](https://git-scm.com/downloads)
- **Node.js** (opcional, para Git hooks) - [Download](https://nodejs.org/)

### Verificar Instalação

```bash
# Verificar Python
python --version  # ou python3 --version

# Verificar MongoDB
mongod --version

# Verificar Git
git --version
```

### Passo a Passo

#### 1. Clone o Repositório

```bash
git clone https://github.com/rootkitoriginal/client_manager.git
cd client_manager
```

#### 2. Crie um Ambiente Virtual

```bash
# Linux/macOS
python3 -m venv venv

# Windows
python -m venv venv
```

#### 3. Ative o Ambiente Virtual

```bash
# Linux/macOS
source venv/bin/activate

# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

#### 4. Instale as Dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. (Opcional) Configure Git Hooks

```bash
# Se tiver Node.js instalado
npm install
```

---

## ⚙️ Configuração

### 1. Configurar MongoDB

Inicie o servidor MongoDB:

```bash
# Linux (systemd)
sudo systemctl start mongodb
sudo systemctl enable mongodb

# macOS (Homebrew)
brew services start mongodb-community

# Windows
# Inicie o serviço 'MongoDB Server' no Gerenciador de Serviços

# Ou manualmente
mongod --dbpath /caminho/para/dados
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env  # Linux/macOS
type nul > .env  # Windows CMD
```

Adicione as configurações:

```env
# Configurações Flask
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1

# Segurança
SECRET_KEY=sua-chave-secreta-super-segura-aqui-mude-isso

# Banco de Dados MongoDB
MONGO_URI=mongodb://localhost:27017/client_manager

# Opcional: Configuração de produção
# MONGO_URI=mongodb://usuario:senha@host:porta/database
```

**⚠️ IMPORTANTE**: Altere `SECRET_KEY` para uma string aleatória e segura em produção!

```bash
# Gerar uma SECRET_KEY segura
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Inicializar o Banco de Dados

Na primeira execução, o sistema criará automaticamente:

- ✅ **Super Admin padrão**: `superadmin` / `Admin@123`
- ✅ **3 Planos padrão**: Basic, Standard, Premium
- ✅ **Templates iniciais**

```bash
python run.py
```

**🔒 Segurança**: Altere a senha padrão imediatamente após o primeiro login!

---

## 📖 Uso

### Iniciar o Servidor

```bash
# Modo desenvolvimento
python run.py

# Ou usando Flask CLI
flask run

# Modo debug
flask run --debug

# Especificar porta
flask run --port 8000

# Acessível na rede local
flask run --host 0.0.0.0
```

O servidor estará disponível em: **http://127.0.0.1:5000**

### Primeiro Acesso

1. **Acesse o sistema**: http://127.0.0.1:5000
2. **Faça login** com o super admin padrão:
   - **Usuário**: `superadmin`
   - **Senha**: `Admin@123`
3. **Altere a senha** imediatamente:
   - Acesse `Perfil` → `Editar` → `Alterar Senha`
4. **Crie novos administradores**:
   - Acesse `Admins` → `Criar Novo Admin`

### Criar Super Admin Manualmente

Se necessário, crie um super admin via CLI:

```bash
python create_superadmin.py <usuario> <senha>

# Exemplo
python create_superadmin.py admin SenhaSegura@2025
```

### Estrutura de Permissões

| Nível          | Permissões                                                      |
|----------------|-----------------------------------------------------------------|
| **super_admin**| Acesso total: gerenciar admins, clientes, planos, templates     |
| **admin**      | Gerenciar clientes, planos, informações (sem gerenciar admins) |
| **client**     | Visualizar apenas suas próprias informações e dashboard         |

---

## 📂 Estrutura do Projeto

```plaintext
client_manager/
│
├── app/                          # Aplicação principal
│   ├── __init__.py              # Factory pattern e inicialização
│   ├── db_init.py               # Inicialização do banco de dados
│   │
│   ├── controllers/             # Controladores (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py             # Autenticação (login/logout)
│   │   ├── admin.py            # Gestão de administradores
│   │   ├── client.py           # Gestão de clientes
│   │   ├── plan.py             # Gestão de planos
│   │   ├── template.py         # Gestão de templates
│   │   ├── domain.py           # Gestão de domínios
│   │   ├── info.py             # Gestão de informações bancárias
│   │   └── main.py             # Rotas principais (index, dashboard)
│   │
│   ├── models/                  # Modelos de dados
│   │   ├── __init__.py
│   │   ├── user.py             # Classe base User
│   │   ├── admin.py            # Modelo Admin (herda User)
│   │   ├── client.py           # Modelo Client (herda User)
│   │   ├── plan.py             # Modelo Plan
│   │   ├── template.py         # Modelo Template
│   │   ├── domain.py           # Modelo Domain
│   │   ├── info.py             # Modelo Info (dados bancários)
│   │   └── login_log.py        # Modelo LoginLog (auditoria)
│   │
│   ├── views/                   # Camada de apresentação
│   │   ├── __init__.py
│   │   ├── base_view.py        # Classe base para views
│   │   ├── auth_view.py        # Views de autenticação
│   │   ├── admin_view.py       # Views de administradores
│   │   ├── client_view.py      # Views de clientes
│   │   ├── plan_view.py        # Views de planos
│   │   ├── template_view.py    # Views de templates
│   │   ├── domain_view.py      # Views de domínios
│   │   ├── info_view.py        # Views de informações
│   │   └── main_view.py        # Views principais
│   │
│   ├── templates/               # Templates HTML (Jinja2)
│   │   ├── layout.html         # Layout base
│   │   ├── navbar.html         # Barra de navegação
│   │   ├── index.html          # Página inicial
│   │   ├── dashboard.html      # Dashboard base
│   │   │
│   │   ├── auth/               # Templates de autenticação
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── register_admin.html
│   │   │
│   │   ├── dashboard/          # Dashboards específicos
│   │   │   ├── admin.html
│   │   │   └── client.html
│   │   │
│   │   ├── admins/             # CRUD de administradores
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── profile.html
│   │   │
│   │   ├── clients/            # CRUD de clientes
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── view.html
│   │   │   └── domains.html
│   │   │
│   │   ├── plans/              # CRUD de planos
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── view.html
│   │   │
│   │   ├── templates/          # CRUD de templates
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── view.html
│   │   │
│   │   ├── domains/            # CRUD de domínios
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   └── view.html
│   │   │
│   │   └── infos/              # CRUD de informações
│   │       ├── list.html
│   │       ├── client_list.html
│   │       ├── create.html
│   │       ├── edit.html
│   │       └── view.html
│   │
│   ├── static/                  # Arquivos estáticos
│   │   ├── css/
│   │   │   └── main.css        # Estilos customizados
│   │   └── js/
│   │       └── main.js         # Scripts JavaScript
│   │
│   └── utils/                   # Utilitários
│       ├── __init__.py
│       └── user_loader.py      # Flask-Login user loader
│
├── .flake8                      # Configuração do Flake8
├── .gitignore                   # Arquivos ignorados pelo Git
├── .husky/                      # Git hooks
├── config.py                    # Configurações da aplicação
├── create_superadmin.py         # Script para criar super admin
├── INITIALIZATION.md            # Documentação de inicialização
├── package.json                 # Dependências Node.js (Husky)
├── requirements.txt             # Dependências Python
├── run.py                       # Ponto de entrada da aplicação
├── setup.sh                     # Script de instalação automatizado
└── README.md                    # Este arquivo
```

---

## 🗄️ Modelos de Dados

### Collections MongoDB

#### **admins**
```json
{
  "_id": ObjectId,
  "username": String (unique),
  "password": String (hashed),
  "role": String ("admin" | "super_admin"),
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **clients**
```json
{
  "_id": ObjectId,
  "username": String (unique),
  "password": String (hashed),
  "plan_id": ObjectId (ref: plans),
  "template_id": ObjectId (ref: templates),
  "status": String ("active" | "inactive"),
  "planActivatedAt": DateTime,
  "expiredAt": DateTime,
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **plans**
```json
{
  "_id": ObjectId,
  "name": String,
  "description": String,
  "price": Float,
  "duration_days": Integer,
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **templates**
```json
{
  "_id": ObjectId,
  "name": String,
  "description": String,
  "content": Object (JSON),
  "status": String ("active" | "inactive"),
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **domains**
```json
{
  "_id": ObjectId,
  "name": String,
  "cloudflare_api": String,
  "cloudflare_email": String,
  "cloudflare_password": String,
  "cloudflare_status": Boolean,
  "ssl": Boolean,
  "domain_limit": Integer,
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **infos**
```json
{
  "_id": ObjectId,
  "client_id": ObjectId (ref: clients),
  "agencia": String,
  "conta": String,
  "senha": String,
  "senha6": String,
  "senha4": String,
  "anotacoes": String,
  "saldo": Float,
  "template_id": ObjectId (ref: templates),
  "domain_id": ObjectId (ref: domains),
  "status": String ("active" | "inactive"),
  "createdAt": DateTime,
  "updatedAt": DateTime
}
```

#### **client_domains**
```json
{
  "_id": ObjectId,
  "client_id": ObjectId (ref: clients),
  "domain_id": ObjectId (ref: domains),
  "subdomain": String,
  "createdAt": DateTime
}
```

#### **login_logs**
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "username": String,
  "role": String,
  "user_type": String,
  "ip_address": String,
  "user_agent": String,
  "created_at": DateTime
}
```

---

## 🛣️ Rotas da API

### Autenticação (`/auth`)

| Método | Rota           | Descrição              | Permissão |
|--------|----------------|------------------------|-----------|
| GET    | `/login`       | Exibir página de login | Público   |
| POST   | `/login`       | Processar login        | Público   |
| GET    | `/logout`      | Fazer logout           | Logado    |

### Administradores (`/admins`)

| Método | Rota                | Descrição               | Permissão    |
|--------|---------------------|-------------------------|--------------|
| GET    | `/`                 | Listar administradores  | super_admin  |
| GET    | `/create`           | Formulário de criação   | super_admin  |
| POST   | `/create`           | Criar administrador     | super_admin  |
| GET    | `/edit/<id>`        | Formulário de edição    | super_admin  |
| POST   | `/edit/<id>`        | Atualizar administrador | super_admin  |
| POST   | `/delete/<id>`      | Deletar administrador   | super_admin  |
| GET    | `/profile`          | Ver perfil próprio      | admin+       |
| POST   | `/profile`          | Atualizar perfil        | admin+       |

### Clientes (`/clients`)

| Método | Rota                          | Descrição                       | Permissão |
|--------|-------------------------------|---------------------------------|-----------|
| GET    | `/`                           | Listar clientes                 | admin+    |
| GET    | `/create`                     | Formulário de criação           | admin+    |
| POST   | `/create`                     | Criar cliente                   | admin+    |
| GET    | `/edit/<id>`                  | Formulário de edição            | admin+    |
| POST   | `/edit/<id>`                  | Atualizar cliente               | admin+    |
| POST   | `/delete/<id>`                | Deletar cliente                 | admin+    |
| GET    | `/view/<id>`                  | Ver detalhes do cliente         | admin+    |
| GET    | `/<id>/domains`               | Gerenciar domínios do cliente   | admin+    |
| POST   | `/<id>/domains/add`           | Adicionar domínio ao cliente    | admin+    |
| POST   | `/<id>/domains/remove/<dom>`  | Remover domínio do cliente      | admin+    |

### Planos (`/plans`)

| Método | Rota            | Descrição             | Permissão |
|--------|-----------------|-----------------------|-----------|
| GET    | `/`             | Listar planos         | admin+    |
| GET    | `/create`       | Formulário de criação | admin+    |
| POST   | `/create`       | Criar plano           | admin+    |
| GET    | `/edit/<id>`    | Formulário de edição  | admin+    |
| POST   | `/edit/<id>`    | Atualizar plano       | admin+    |
| POST   | `/delete/<id>`  | Deletar plano         | admin+    |
| GET    | `/view/<id>`    | Ver detalhes do plano | admin+    |

### Templates (`/templates`)

| Método | Rota            | Descrição             | Permissão |
|--------|-----------------|-----------------------|-----------|
| GET    | `/`             | Listar templates      | admin+    |
| GET    | `/create`       | Formulário de criação | admin+    |
| POST   | `/create`       | Criar template        | admin+    |
| GET    | `/edit/<id>`    | Formulário de edição  | admin+    |
| POST   | `/edit/<id>`    | Atualizar template    | admin+    |
| POST   | `/delete/<id>`  | Deletar template      | admin+    |
| GET    | `/view/<id>`    | Ver detalhes          | admin+    |

### Domínios (`/domains`)

| Método | Rota            | Descrição             | Permissão |
|--------|-----------------|-----------------------|-----------|
| GET    | `/`             | Listar domínios       | admin+    |
| GET    | `/create`       | Formulário de criação | admin+    |
| POST   | `/create`       | Criar domínio         | admin+    |
| GET    | `/edit/<id>`    | Formulário de edição  | admin+    |
| POST   | `/edit/<id>`    | Atualizar domínio     | admin+    |
| POST   | `/delete/<id>`  | Deletar domínio       | admin+    |
| GET    | `/view/<id>`    | Ver detalhes          | admin+    |

### Informações (`/infos`)

| Método | Rota                 | Descrição                    | Permissão |
|--------|----------------------|------------------------------|-----------|
| GET    | `/`                  | Listar todas informações     | admin+    |
| GET    | `/client/<id>`       | Informações de um cliente    | admin+    |
| GET    | `/create/<id>`       | Formulário de criação        | admin+    |
| POST   | `/create/<id>`       | Criar informação             | admin+    |
| GET    | `/edit/<id>`         | Formulário de edição         | admin+    |
| POST   | `/edit/<id>`         | Atualizar informação         | admin+    |
| POST   | `/delete/<id>`       | Deletar informação           | admin+    |
| GET    | `/view/<id>`         | Ver detalhes                 | admin+    |

### Principal (`/`)

| Método | Rota         | Descrição            | Permissão |
|--------|--------------|----------------------|-----------|
| GET    | `/`          | Página inicial       | Público   |
| GET    | `/dashboard` | Dashboard do usuário | Logado    |

---

## 👨‍💻 Desenvolvimento

### Script de Configuração Rápida

Execute o script automatizado (Linux/macOS):

```bash
chmod +x setup.sh
./setup.sh
```

### Ferramentas de Qualidade de Código

#### Git Hooks (Husky)

O projeto utiliza **Husky** para garantir qualidade:

- **pre-commit**: Executa Flake8 para verificar estilo de código
- **pre-push**: Executa testes antes de enviar ao repositório

#### Flake8 (Linter Python)

Configuração em `.flake8`:

```ini
[flake8]
max-line-length = 120
exclude = 
    .git,
    __pycache__,
    venv,
    build,
    dist
ignore = E203, W503
```

Executar manualmente:

```bash
flake8 app/ --count --show-source --statistics
```

### Boas Práticas

- ✅ Use type hints quando possível
- ✅ Documente funções complexas
- ✅ Mantenha funções com responsabilidade única
- ✅ Valide dados de entrada
- ✅ Use try-except para operações de banco de dados
- ✅ Registre logs de erros com `current_app.logger`
- ✅ Não commite credenciais ou chaves secretas
- ✅ Teste localmente antes de fazer push

### Debugging

#### Flask Debug Mode

```bash
export FLASK_DEBUG=1
flask run
```

#### MongoDB Shell

```bash
# Conectar ao MongoDB
mongosh

# Usar o database
use client_manager

# Ver coleções
show collections

# Consultar dados
db.clients.find().pretty()
db.admins.find().pretty()
db.login_logs.find().sort({created_at: -1}).limit(10)
```

#### Logs da Aplicação

```python
# No código
from flask import current_app

current_app.logger.info("Mensagem informativa")
current_app.logger.error(f"Erro: {e}")
current_app.logger.warning("Aviso")
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estas etapas:

### 1. Fork o Projeto

Clique em "Fork" no GitHub.

### 2. Clone Seu Fork

```bash
git clone https://github.com/seu-usuario/client_manager.git
cd client_manager
```

### 3. Crie uma Branch

```bash
git checkout -b feature/minha-funcionalidade
# ou
git checkout -b fix/correcao-de-bug
```

### 4. Faça as Alterações

- Escreva código limpo e documentado
- Siga as convenções do projeto
- Adicione testes se aplicável

### 5. Commit

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
# ou
git commit -m "fix: corrige bug Y"
```

Padrões de commit (Conventional Commits):
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração
- `test:` - Testes
- `chore:` - Tarefas de manutenção

### 6. Push

```bash
git push origin feature/minha-funcionalidade
```

### 7. Abra um Pull Request

Vá ao GitHub e clique em "New Pull Request".

### Diretrizes

- Descreva claramente as mudanças
- Referencie issues relacionadas
- Certifique-se de que o código passa no Flake8
- Atualize a documentação se necessário

---

## 📄 Licença

Este projeto está licenciado sob a **Licença ISC**.

---

## 📧 Contato

**Autor**: [rootkitoriginal](https://github.com/rootkitoriginal)

**Repositório**: [client_manager](https://github.com/rootkitoriginal/client_manager)

---

## 🙏 Agradecimentos

- Comunidade Flask
- MongoDB
- Bootstrap
- Todos os contribuidores

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub! ⭐**

[Reportar Bug](https://github.com/rootkitoriginal/client_manager/issues) · [Solicitar Feature](https://github.com/rootkitoriginal/client_manager/issues) · [Documentação](https://github.com/rootkitoriginal/client_manager/wiki)

</div>
