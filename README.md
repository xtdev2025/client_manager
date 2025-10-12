# 🎯 Client Manager - Sistema de Gerenciamento de Clientes

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.6.0-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/license-ISC-blue.svg)](LICENSE)

Sistema completo de gerenciamento de clientes com autenticação robusta, controle de acesso baseado em funções (RBAC), gestão de planos de assinatura, templates personalizados, domínios e informações bancárias.

## 📚 Documentação

### 📖 Guias de Início Rápido

- **[📋 Índice Completo](docs/INDEX.md)** - Índice organizado de toda documentação
- **[🚀 API Quick Reference](docs/API_QUICK_REFERENCE.md)** - Referência rápida da API
- **[🏗️ Arquitetura](docs/ARCHITECTURE.md)** - Arquitetura completa do sistema

### 🎉 API Documentation (Swagger/OpenAPI)

**Documentação interativa disponível em `/api/docs`**

- ✅ 63+ endpoints documentados
- ✅ Interface interativa Swagger UI
- ✅ Especificação OpenAPI 3.0.3

### 📁 Mais Documentação

Toda a documentação técnica está organizada em [`docs/`](docs/):

- Deploy (AWS, Azure)
- Migração e Modernização
- Scripts e Rotas
- Dashboard e Templates

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Instalação e Configuração](#-instalação-e-configuração)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Configuração Inicial](#configuração-inicial)
  - [Inicialização do Sistema](#inicialização-do-sistema)
- [Uso do Sistema](#-uso-do-sistema)
  - [Primeiro Acesso](#primeiro-acesso)
  - [Criação Manual de Super Admin](#criação-manual-de-super-admin)
  - [Níveis de Acesso](#níveis-de-acesso)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Modelos de Dados](#-modelos-de-dados)
- [Rotas da API](#-rotas-da-api)
- [Desenvolvimento](#-desenvolvimento)
- [Testes](#-testes)
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
- **[Pydantic 2.5.0](https://docs.pydantic.dev/)** - Validação de dados
- **[Flask-Limiter 3.5.0](https://flask-limiter.readthedocs.io/)** - Rate limiting e proteção contra ataques

### Frontend

- **[Bootstrap 5](https://getbootstrap.com/)** - Framework CSS responsivo
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine
- **JavaScript Vanilla** - Scripts customizados

### Banco de Dados

- **[MongoDB 4.6+](https://www.mongodb.com/)** - Banco de dados NoSQL orientado a documentos

### Ferramentas de Desenvolvimento

- **[Pytest 7.4.3](https://pytest.org/)** - Framework de testes
- **[Pytest-Flask 1.3.0](https://pytest-flask.readthedocs.io/)** - Testes para Flask
- **[Pytest-Cov 4.1.0](https://pytest-cov.readthedocs.io/)** - Cobertura de testes
- **[Husky 9.1.7](https://typicode.github.io/husky/)** - Git hooks para qualidade de código
- **[Flake8](https://flake8.pycqa.org/)** - Linter Python
- **[Git](https://git-scm.com/)** - Controle de versão

---

## 🚀 Instalação e Configuração

### 📦 Deploy em Produção

**Quer fazer deploy na nuvem?** Veja nossos guias completos:

#### Azure

- 📘 **[Guia Completo Azure](docs/AZURE_DEPLOYMENT.md)** - App Service + VM
- ⚡ **[Quick Start Azure](DEPLOY_AZURE.md)** - Deploy em 5 minutos

```bash
python scripts/azure_deploy.py  # Deploy automático
```

#### AWS (Amazon Web Services)

- 📕 **[Guia Completo AWS](docs/AWS_DEPLOYMENT.md)** - 4 opções (EB, EC2, ECS, Lambda)
- ⚡ **[Quick Start AWS](DEPLOY_AWS.md)** - Deploy em 10 minutos

```bash
python scripts/aws_eb_deploy.py   # Elastic Beanstalk (Recomendado)
python scripts/aws_ec2_deploy.py  # EC2 (Mais barato)
```

**Opções de Deploy:**

- ✅ **Azure App Service** - PaaS simplificado
- ✅ **Azure VM** - Controle total
- ✅ **AWS Elastic Beanstalk** - Auto-scaling fácil
- ✅ **AWS EC2** - $8/mês (Free tier: $0/ano)
- ✅ **AWS ECS** - Containerizado com Docker
- ✅ **AWS Lambda** - Serverless ~$2-5/mês

---

### Pré-requisitos (Desenvolvimento Local)

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

## 📖 Uso do Sistema

### Inicialização do Sistema

#### Inicialização Automática

Quando o aplicativo é iniciado pela **primeira vez**, ele verifica automaticamente se existem dados iniciais no banco de dados e cria:

**1. Super Admin Padrão** (se não existir nenhum usuário admin):

- **Usuário**: `superadmin`
- **Senha**: `Admin@123`

**⚠️ IMPORTANTE**: Por segurança, você deve fazer login e **alterar esta senha imediatamente**!

**2. Planos Padrão** (se não existirem planos cadastrados):

- **Basic Plan**: R$ 29,99/mês
- **Standard Plan**: R$ 59,99/mês  
- **Premium Plan**: R$ 99,99/mês

### Iniciar o Servidor

```bash
# Ativar ambiente virtual primeiro
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Iniciar aplicação
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

O servidor estará disponível em: **<http://127.0.0.1:5000>**

### Primeiro Acesso

1. **Acesse o sistema**: <http://127.0.0.1:5000>
2. **Faça login** com o super admin padrão:
   - **Usuário**: `superadmin`
   - **Senha**: `Admin@123`
3. **Altere a senha imediatamente**:
   - Acesse `Perfil` → `Editar` → `Alterar Senha`
4. **Crie novos administradores** (opcional):
   - Acesse `Admins` → `Criar Novo Admin`

### Criação Manual de Super Admin

Se você precisar criar um super admin manualmente (por exemplo, se o superadmin padrão for excluído ou esqueceu a senha), use o script `create_superadmin.py`:

```bash
python scripts/create_superadmin.py <username> <password>
```

**Exemplos:**

```bash
# Criar super admin com nome 'admin' e senha 'SenhaSegura@2025'
python scripts/create_superadmin.py admin SenhaSegura@2025

# Criar super admin com nome 'rootkit' e senha personalizada
python scripts/create_superadmin.py rootkit MinhaS3nh@Forte!
```

**Notas:**

- O script criará um novo super_admin mesmo que já existam outros administradores
- Use uma senha forte com letras maiúsculas, minúsculas, números e símbolos
- O usuário será criado com role `super_admin`

### Níveis de Acesso

O sistema possui **três níveis de acesso** hierárquicos:

#### 1. **super_admin** (Super Administrador)

**Permissões Completas:**

- ✅ Criar, editar e excluir outros administradores
- ✅ Gerenciar todos os clientes
- ✅ Criar, editar e excluir planos
- ✅ Gerenciar templates
- ✅ Gerenciar domínios
- ✅ Gerenciar informações bancárias
- ✅ Visualizar logs de auditoria
- ✅ Acesso total ao sistema

**Proteções:**

- ⚠️ O sistema não permite excluir o último super_admin
- ⚠️ Super admins não podem se auto-excluir

#### 2. **admin** (Administrador)

**Permissões:**

- ✅ Gerenciar clientes (criar, editar, excluir)
- ✅ Gerenciar planos (criar, editar, excluir)
- ✅ Gerenciar templates
- ✅ Gerenciar domínios
- ✅ Gerenciar informações bancárias
- ✅ Visualizar dashboards

**Restrições:**

- ❌ **Não pode** gerenciar outros administradores
- ❌ **Não pode** visualizar/editar dados de outros admins

#### 3. **client** (Cliente)

**Permissões:**

- ✅ Visualizar seu próprio dashboard
- ✅ Ver informações da sua conta
- ✅ Ver seu plano ativo
- ✅ Ver seus templates
- ✅ Ver seus domínios

**Restrições:**

- ❌ **Não pode** acessar área administrativa
- ❌ **Não pode** visualizar dados de outros clientes
- ❌ **Não pode** modificar configurações do sistema

### Tabela Resumida de Permissões

| Nível          | Gerenciar Admins | Gerenciar Clientes | Gerenciar Planos | Ver Próprios Dados | Acesso Total |
|----------------|:----------------:|:------------------:|:----------------:|:------------------:|:------------:|
| **super_admin**|        ✅        |         ✅         |        ✅        |         ✅         |      ✅      |
| **admin**      |        ❌        |         ✅         |        ✅        |         ✅         |      ❌      |
| **client**     |        ❌        |         ❌         |        ❌        |         ✅         |      ❌      |

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
├── scripts/                     # Scripts utilitários (Python)
│   ├── create_superadmin.py    # Criar super admin manualmente
│   ├── setup.py                # Setup automatizado do projeto
│   ├── startup.py              # Script de inicialização (produção)
│   ├── aws_eb_deploy.py        # Deploy AWS Elastic Beanstalk
│   ├── aws_ec2_deploy.py       # Deploy AWS EC2
│   ├── azure_deploy.py         # Deploy Azure App Service
│   ├── test_workflows.py       # Testar workflows essenciais
│   └── test_all_workflows.py   # Testar todos os workflows
│
├── tests/                       # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py             # Configuração pytest
│   ├── unit/                   # Testes unitários
│   │   ├── test_auth_service.py
│   │   ├── test_client_service.py
│   │   └── test_audit_service.py
│   └── integration/            # Testes de integração
│       ├── test_auth_routes.py
│       └── test_plan_routes.py
│
├── .env                         # Variáveis de ambiente (não versionado)
├── .env.example                 # Exemplo de variáveis de ambiente
├── .flake8                      # Configuração do Flake8
├── .gitignore                   # Arquivos ignorados pelo Git
├── .husky/                      # Git hooks
├── ARCHITECTURE.md              # Documentação da arquitetura
├── CODE_OF_CONDUCT.md           # Código de conduta
├── config.py                    # Configurações da aplicação
├── package.json                 # Dependências Node.js (Husky)
├── pytest.ini                   # Configuração do pytest
├── requirements.txt             # Dependências Python
├── run.py                       # Ponto de entrada da aplicação
├── TEMPLATE_FIELDS_SYSTEM.md    # Sistema de campos de templates
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

### Scripts de Automação

O projeto inclui scripts Python para automação de tarefas:

#### Setup e Configuração

```bash
# Setup automatizado do projeto
python scripts/setup.py

# Criar super admin manualmente
python scripts/create_superadmin.py <username> <password>
```

#### Deploy em Nuvem

```bash
# Deploy no Azure
python scripts/azure_deploy.py

# Deploy no AWS Elastic Beanstalk
python scripts/aws_eb_deploy.py

# Deploy no AWS EC2
python scripts/aws_ec2_deploy.py
```

#### Testes de Workflows

```bash
# Testar todos os workflows GitHub Actions
python scripts/test_all_workflows.py

# Testar workflows essenciais
python scripts/test_workflows.py
```

#### Startup (Produção)

```bash
# Script de inicialização para Azure App Service
python scripts/startup.py
```

O script irá:

- ✅ Verificar versão do Python (3.9+)
- ✅ Criar ambiente virtual (se não existir)
- ✅ Atualizar pip
- ✅ Instalar todas as dependências
- ✅ Verificar instalação do MongoDB
- ✅ Verificar se MongoDB está rodando
- ✅ Criar arquivo .env (se não existir)
- ✅ Mostrar próximos passos

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
- ✅ Valide dados de entrada com pydantic schemas
- ✅ Use try-except para operações de banco de dados
- ✅ Registre logs de erros com `current_app.logger`
- ✅ Não commite credenciais ou chaves secretas
- ✅ Teste localmente antes de fazer push
- ✅ Utilize a camada de serviços para lógica de negócio
- ✅ Implemente auditoria para operações sensíveis

### 🧪 Testes

O projeto utiliza **pytest** para testes automatizados.

#### Executar Todos os Testes

```bash
# Instalar dependências de teste
pip install -r requirements.txt

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app --cov-report=html

# Executar apenas testes unitários
pytest tests/unit/

# Executar apenas testes de integração
pytest tests/integration/

# Executar testes específicos
pytest tests/unit/test_auth_service.py -v
```

#### Estrutura de Testes

```plaintext
tests/
├── __init__.py
├── conftest.py              # Fixtures e configurações
├── unit/                    # Testes unitários
│   ├── test_auth_service.py
│   ├── test_client_service.py
│   └── ...
└── integration/             # Testes de integração
    ├── test_auth_routes.py
    └── ...
```

#### Escrever Novos Testes

```python
# Exemplo de teste unitário
def test_validate_client_data(app):
    """Test client data validation"""
    with app.app_context():
        # Setup
        success, plan_id = Plan.create('Test Plan', 'Desc', 99.99, 30)
        
        # Execute
        valid, error = ClientService.validate_client_data(
            'testuser', 'password123', plan_id
        )
        
        # Assert
        assert valid is True
        assert error is None
```

### 🔒 Checklist de Segurança para Produção

Antes de fazer deploy em produção, certifique-se de:

#### Configuração

- [ ] Alterar `SECRET_KEY` para uma chave forte e aleatória
- [ ] Definir `FLASK_ENV=production`
- [ ] Configurar `MONGO_URI` com credenciais seguras
- [ ] Usar HTTPS com certificado SSL válido
- [ ] Configurar firewall para portas adequadas
- [ ] Definir rate limiting adequado para sua aplicação

#### Autenticação e Autorização

- [ ] Alterar senha padrão do super admin (`Admin@123`)
- [ ] Implementar política de senhas fortes
- [ ] Considerar implementar 2FA para administradores
- [ ] Revisar e testar todas as permissões RBAC
- [ ] Validar que decoradores `@admin_required` e `@super_admin_required` estão em todas as rotas sensíveis

#### Banco de Dados

- [ ] Criar backup automático do MongoDB
- [ ] Configurar autenticação no MongoDB
- [ ] Restringir acesso ao MongoDB apenas para IPs conhecidos
- [ ] Implementar índices para melhor performance
- [ ] Criptografar dados sensíveis (informações bancárias)

#### Logging e Monitoramento

- [ ] Configurar logs de aplicação em produção
- [ ] Implementar monitoramento de erros (ex: Sentry)
- [ ] Revisar logs de auditoria regularmente
- [ ] Configurar alertas para atividades suspeitas

#### Validação e Sanitização

- [ ] Todas as entradas de usuário são validadas
- [ ] Proteção contra SQL/NoSQL injection (PyMongo protege por padrão)
- [ ] Proteção CSRF habilitada em formulários
- [ ] Validação de upload de arquivos (se implementado)

#### Dependências e Atualizações

- [ ] Todas as dependências estão atualizadas
- [ ] Vulnerabilidades conhecidas foram corrigidas
- [ ] Configurar alertas de segurança do GitHub
- [ ] Planejar atualizações regulares

#### Infraestrutura

- [ ] Usar servidor WSGI em produção (Gunicorn, uWSGI)
- [ ] Configurar proxy reverso (Nginx, Apache)
- [ ] Limitar recursos (CPU, memória) por processo
- [ ] Configurar backup de arquivos estáticos

### 🔧 Troubleshooting

#### Problema: Testes falhando com erro de conexão MongoDB

```bash
# Solução: Certifique-se que MongoDB está rodando
sudo systemctl start mongodb
# ou
mongod --dbpath /path/to/data
```

#### Problema: Rate limiting muito restritivo

```python
# Ajustar em app/__init__.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"]  # Aumentar limites
)
```

#### Problema: Erros de importação em testes

```bash
# Adicionar diretório raiz ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/client_manager"
```

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

## 🚀 Modernização e Melhorias Recentes

### 🐍 Migração Shell → Python (Dezembro 2024)

**Todos os scripts foram convertidos de Bash (.sh) para Python (.py)**:

- ✅ **6 scripts convertidos** com sucesso
- ✅ **Melhor portabilidade** - Funciona em Windows, Linux e macOS
- ✅ **Tratamento de erros robusto** - Exception handling adequado
- ✅ **Código estruturado** - Classes e métodos organizados
- ✅ **Logs informativos** - Feedback visual com emojis

**Scripts Convertidos**:

- `startup.sh` → `startup.py`
- `test-workflows.sh` → `test_workflows.py`
- `test-all-workflows.sh` → `test_all_workflows.py`
- `aws_eb_deploy.sh` → `aws_eb_deploy.py`
- `aws_ec2_deploy.sh` → `aws_ec2_deploy.py`
- `azure_deploy.sh` → `azure_deploy.py`

📚 **Documentação**: [Migração Shell → Python](docs/MIGRATION_SHELL_TO_PYTHON.md) | [Scripts Documentation](docs/SCRIPTS_DOCUMENTATION.md)

### Camada de Serviços (`app/services/`)

O projeto agora implementa uma **camada de serviços** para separar a lógica de negócio dos controllers:

- **AuthService**: Gerencia autenticação, validação de credenciais e registro de login
- **ClientService**: Lógica de negócio para operações com clientes
- **AuditService**: Sistema de auditoria para registrar operações sensíveis

**Benefícios**:

- ✅ Separação clara de responsabilidades
- ✅ Código mais testável e reutilizável
- ✅ Facilita manutenção e evolução do código

### Validação com Pydantic (`app/schemas/`)

Schemas de validação para garantir integridade dos dados:

- **UserCreateSchema**: Validação de criação de usuários
- **ClientCreateSchema**: Validação específica para clientes
- **AdminCreateSchema**: Validação específica para admins
- **PlanCreateSchema**: Validação de planos
- **DomainCreateSchema**: Validação de domínios

**Benefícios**:

- ✅ Validação robusta e centralizada
- ✅ Type safety com hints
- ✅ Mensagens de erro descritivas

### Rate Limiting com Flask-Limiter

Proteção contra abuso e ataques de força bruta:

```python
# Login: 10 tentativas por minuto
@limiter.limit("10 per minute")

# Registro de admin: 5 tentativas por minuto
@limiter.limit("5 per minute")

# Limite global: 200 requisições/dia, 50/hora
default_limits=["200 per day", "50 per hour"]
```

### Sistema de Auditoria

Registro automático de operações sensíveis na collection `audit_logs`:

- ✅ Criação, edição e exclusão de admins
- ✅ Criação, edição e exclusão de planos
- ✅ Criação e exclusão de domínios
- ✅ Tentativas de login (sucesso e falha)

**Informações registradas**:

- Ação realizada
- Tipo de entidade
- ID da entidade afetada
- ID do usuário que realizou a ação
- IP address e User Agent
- Timestamp
- Detalhes adicionais

### Type Hints

Todas as funções principais agora possuem **type hints** para melhor:

- IDE autocomplete
- Detecção de erros em tempo de desenvolvimento
- Documentação automática
- Refatoração segura

### Testes Automatizados

Suite completa de testes com pytest:

```plaintext
tests/
├── unit/                    # Testes unitários
│   ├── test_auth_service.py
│   └── test_client_service.py
└── integration/             # Testes de integração
    └── test_auth_routes.py
```

**Cobertura**: Testes para autenticação, validação, CRUD de clientes

---

## 📚 Documentação Adicional

### Documentos Técnicos

- 📘 **[Arquitetura do Sistema](docs/ARCHITECTURE.md)** - Visão geral da arquitetura
- 🔧 **[Scripts Python](docs/SCRIPTS_DOCUMENTATION.md)** - Documentação completa dos scripts
- 🔄 **[Migração Shell→Python](docs/MIGRATION_SHELL_TO_PYTHON.md)** - Detalhes da conversão
- 🚀 **[Deploy AWS](docs/AWS_DEPLOYMENT.md)** - Guia completo AWS
- ☁️ **[Deploy Azure](docs/AZURE_DEPLOYMENT.md)** - Guia completo Azure
- 🔐 **[Configuração AWS](docs/AWS_CREDENTIALS_SETUP.md)** - Setup de credenciais
- 📋 **[Sistema de Templates](docs/TEMPLATE_FIELDS_SYSTEM.md)** - Campos de templates
- 🔍 **[API Documentation](docs/API_DOCUMENTATION.md)** - Documentação da API
- ⚡ **[API Quick Reference](docs/API_QUICK_REFERENCE.md)** - Referência rápida
- 📊 **[Swagger Implementation](docs/SWAGGER_IMPLEMENTATION.md)** - Implementação Swagger
- 📈 **[Swagger Endpoints Report](docs/SWAGGER_ENDPOINTS_REPORT.md)** - Relatório de endpoints

### Guias de Deploy Rápido

- ⚡ **[Quick Start AWS](DEPLOY_AWS.md)** - Deploy AWS em 10 minutos
- ⚡ **[Quick Start Azure](DEPLOY_AZURE.md)** - Deploy Azure em 5 minutos

### Código de Conduta e Contribuição

- 🤝 **[Contributing Guidelines](.github/CONTRIBUTING.md)** - Como contribuir
- 📜 **[Code of Conduct](CODE_OF_CONDUCT.md)** - Código de conduta
- 🔧 **[Copilot Instructions](.github/copilot-instructions.md)** - Instruções para AI

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

[Reportar Bug](https://github.com/rootkitoriginal/client_manager/issues) · [Solicitar Feature](https://github.com/rootkitoriginal/client_manager/issues) · [Documentação](docs/) · [Scripts Python](docs/SCRIPTS_DOCUMENTATION.md)

---

### 🔄 Changelog Recente

**v2.1.0 - Dezembro 2024**

- 🐍 **Migração completa**: Shell scripts → Python scripts
- 📚 **Documentação expandida**: 12+ documentos técnicos
- 🚀 **Deploy melhorado**: Scripts mais robustos e portáveis
- ✅ **Compatibilidade**: Windows, Linux, macOS
- 🔧 **Manutenibilidade**: Código estruturado e testável

</div>
