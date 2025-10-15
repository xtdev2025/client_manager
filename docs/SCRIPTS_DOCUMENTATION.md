# 🐍 Scripts Python - Documentação Completa

> **Nota Histórica (Outubro 2025):** Este documento descreve a migração Shell→Python realizada em Dezembro 2024. Muitos desses scripts foram posteriormente simplificados ou substituídos por Docker/CI/CD. Para scripts atuais, veja a seção [Scripts Atuais](#-scripts-atuais).

Este documento descreve todos os scripts Python disponíveis no projeto Client Manager, convertidos de shell scripts para Python para melhor portabilidade e manutenibilidade.

## 📋 Índice

- [Scripts Atuais (2025)](#-scripts-atuais-2025)
- [Visão Geral Histórica](#-visão-geral-histórica)
- [Scripts de Deploy (Histórico)](#-scripts-de-deploy-histórico)
- [Scripts de Desenvolvimento (Histórico)](#-scripts-de-desenvolvimento-histórico)
- [Scripts de Produção (Histórico)](#-scripts-de-produção-histórico)
- [Configuração e Setup](#-configuração-e-setup)
- [Troubleshooting](#-troubleshooting)

---

## 🆕 Scripts Atuais (2025)

### Localização dos Scripts Atuais

```
scripts/
├── create_superadmin.py    # ✅ Criação manual de super admin
└── deploy_to_ec2.py        # ✅ Deploy para AWS EC2
```

### 1. Create Superadmin (`create_superadmin.py`)

**Descrição**: Cria um super administrador manualmente via CLI.

**Uso**:

```bash
python scripts/create_superadmin.py
```

**Funcionalidades**:

- ✅ Prompt interativo para username e password
- ✅ Validação de entrada
- ✅ Hashing seguro de senha (bcrypt)
- ✅ Criação direta no MongoDB
- ✅ Verificação de duplicatas

### 2. Deploy to EC2 (`deploy_to_ec2.py`)

**Descrição**: Script simplificado de deploy para AWS EC2.

**Uso**:

```bash
python scripts/deploy_to_ec2.py
```

**Funcionalidades**:

- ✅ Configuração automatizada de instância EC2
- ✅ Setup de ambiente Python
- ✅ Configuração de MongoDB
- ✅ Deploy da aplicação
- ✅ Configuração de systemd service

### 3. Comando Flask CLI para Reconciliação de Payouts

**Descrição**: Comando integrado ao Flask CLI para reconciliação automática de payouts Heleket.

**Uso**:

```bash
flask reconcile-payouts
```

**Funcionalidades**:

- ✅ Polling de status de payouts pendentes
- ✅ Atualização automática via API Heleket
- ✅ Registro de auditoria
- ✅ Logs detalhados de operação

### Notas sobre Scripts Descontinuados

Os seguintes scripts foram descontinuados em favor de Docker e CI/CD:

- ❌ `startup.py` - Substituído por Docker CMD e systemd services
- ❌ `test_workflows.py` / `test_all_workflows.py` - Substituídos por GitHub Actions
- ❌ `azure_deploy.py` - Substituído por Azure Pipelines e Docker
- ❌ `aws_eb_deploy.py` / `aws_ec2_deploy.py` - Substituídos por `deploy_to_ec2.py` e IaC

---

## 🎯 Visão Geral Histórica

Todos os scripts foram convertidos de Bash (.sh) para Python (.py) para:

- ✅ **Melhor portabilidade** - Funciona em Windows, Linux e macOS
- ✅ **Tratamento de erros robusto** - Exception handling adequado
- ✅ **Código mais legível** - Estrutura orientada a objetos
- ✅ **Facilidade de manutenção** - Lógica modular e reutilizável
- ✅ **Logs informativos** - Feedback visual com emojis e cores

### Localização dos Scripts

```
scripts/
├── create_superadmin.py    # ✅ Existente (não convertido)
├── setup.py               # ✅ Existente (não convertido)
├── startup.py             # 🆕 Convertido de startup.sh
├── aws_eb_deploy.py       # 🆕 Convertido de aws_eb_deploy.sh
├── aws_ec2_deploy.py      # 🆕 Convertido de aws_ec2_deploy.sh
├── azure_deploy.py        # 🆕 Convertido de azure_deploy.sh
├── test_workflows.py      # 🆕 Convertido de test-workflows.sh
└── test_all_workflows.py  # 🆕 Convertido de test-all-workflows.sh
```

---

## 🚀 Scripts de Deploy (Histórico)

### 1. Azure Deploy (`azure_deploy.py`)

**Descrição**: Deploy automatizado no Azure App Service

**Uso**:

```bash
python scripts/azure_deploy.py
```

**Funcionalidades**:

- ✅ Verifica instalação do Azure CLI
- ✅ Autentica no Azure automaticamente
- ✅ Cria Resource Group
- ✅ Cria App Service Plan
- ✅ Cria Web App com Python 3.10
- ✅ Configura startup command
- ✅ Configura variáveis de ambiente padrão
- ✅ Configura deploy via Git

**Recursos Criados**:

- Resource Group: `rg-clientmanager`
- App Service Plan: `plan-clientmanager` (SKU: B1)
- Web App: `clientmanager-rootkit`

**Próximos Passos Após Deploy**:

1. Configurar variáveis de ambiente no Portal Azure
2. Fazer push do código: `git push azure main`
3. Criar super admin via SSH
4. Acessar aplicação

---

### 2. AWS Elastic Beanstalk Deploy (`aws_eb_deploy.py`)

**Descrição**: Deploy automatizado no AWS Elastic Beanstalk

**Uso**:

```bash
python scripts/aws_eb_deploy.py
```

**Funcionalidades**:

- ✅ Instala AWS CLI e EB CLI automaticamente
- ✅ Verifica credenciais AWS
- ✅ Cria Procfile para Gunicorn
- ✅ Configura .ebextensions
- ✅ Inicializa aplicação EB
- ✅ Cria ou atualiza ambiente

**Configurações**:

- Aplicação: `client-manager`
- Ambiente: `client-manager-prod`
- Plataforma: `python-3.10`
- Instância: `t2.small`
- Região: `us-east-1`

**Custo Estimado**: ~$35/mês (Free tier: $0 no primeiro ano)

---

### 3. AWS EC2 Deploy (`aws_ec2_deploy.py`)

**Descrição**: Deploy automatizado em instância EC2

**Uso**:

```bash
python scripts/aws_ec2_deploy.py
```

**Funcionalidades**:

- ✅ Cria chave SSH automaticamente
- ✅ Configura Security Group
- ✅ Lança instância EC2 (t2.micro - Free tier)
- ✅ Instala dependências no servidor
- ✅ Configura Nginx + Gunicorn
- ✅ Cria serviço systemd

**Configurações**:

- Instância: `t2.micro` (Free tier eligible)
- AMI: Ubuntu 22.04 LTS
- Região: `us-east-1`
- Portas: 22 (SSH), 80 (HTTP), 443 (HTTPS)

**Custo Estimado**: ~$8/mês (Free tier: $0 no primeiro ano)

---

## 🧪 Scripts de Desenvolvimento

### 1. Test All Workflows (`test_all_workflows.py`)

**Descrição**: Testa todos os workflows GitHub Actions com Act

**Uso**:

```bash
python scripts/test_all_workflows.py
```

**Workflows Testados**:

- ✅ `ci.yml` - Lint e validação
- ✅ `test.yml` - Testes unitários e integração
- ✅ `deploy.yml` - Deploy (dry-run)
- ✅ `security.yml` - Scan de segurança
- ✅ `codeql.yml` - Análise de código
- ✅ `dependency-review.yml` - Análise de dependências

**Pré-requisitos**:

- Act instalado: `curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash`
- Arquivos `.secrets` e `.env.act` configurados

---

### 2. Test Essential Workflows (`test_workflows.py`)

**Descrição**: Testa workflows essenciais (versão simplificada)

**Uso**:

```bash
python scripts/test_workflows.py
```

**Diferenças do `test_all_workflows.py`**:

- ❌ Não executa em dry-run por padrão
- ✅ Foco nos workflows mais importantes
- ✅ Execução mais rápida
- ✅ Melhor para desenvolvimento diário

---

## 🏭 Scripts de Produção (Histórico)

### 1. Startup Script (`startup.py`)

**Descrição**: Script de inicialização para Azure App Service

**Uso**:

```bash
python scripts/startup.py
```

**Funcionalidades**:

- ✅ Ativa ambiente virtual (se existir)
- ✅ Inicializa banco de dados
- ✅ Inicia aplicação com Gunicorn
- ✅ Configurações otimizadas para produção

**Configurações Gunicorn**:

- Bind: `0.0.0.0:8000`
- Workers: 4
- Timeout: 600 segundos

**Uso no Azure**:
O script é automaticamente executado pelo Azure App Service quando configurado como `startup-file`.

---

## ⚙️ Configuração e Setup

### Variáveis de Ambiente Necessárias

#### Para Deploy Azure

```env
# Não são necessárias variáveis específicas
# O script usa Azure CLI authentication
```

#### Para Deploy AWS

```env
# Configuradas via 'aws configure' ou:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### Para Testes de Workflow

```env
# Arquivo .env.act
FLASK_CONFIG=testing
MONGO_URI=mongodb://localhost:27017/test_db
SECRET_KEY=test-secret-key
```

```env
# Arquivo .secrets
GITHUB_TOKEN=your_github_token
```

### Dependências dos Scripts

#### Python Packages

```bash
# Já incluídas no requirements.txt
subprocess  # Built-in
pathlib     # Built-in
json        # Built-in
sys         # Built-in
os          # Built-in
```

#### Ferramentas Externas

```bash
# Azure
az          # Azure CLI (instalado automaticamente)

# AWS
aws         # AWS CLI (instalado automaticamente)
eb          # EB CLI (instalado automaticamente)

# Testes
act         # GitHub Actions local runner
git         # Git (para deploy)
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. "Azure CLI not found"

```bash
# Solução: Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### 2. "Act not found"

```bash
# Solução: Instalar Act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

#### 3. "AWS credentials not configured"

```bash
# Solução: Configurar AWS CLI
aws configure
```

#### 4. "Permission denied" ao executar scripts

```bash
# Solução: Tornar executável
chmod +x scripts/*.py
```

#### 5. "Module not found" em scripts Python

```bash
# Solução: Executar da raiz do projeto
cd /path/to/client_manager
python scripts/script_name.py
```

### Logs e Debug

#### Habilitar Debug nos Scripts

```python
# Adicionar no início do script
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Status dos Serviços

**Azure**:

```bash
az webapp show --name clientmanager-rootkit --resource-group rg-clientmanager
az webapp log tail --name clientmanager-rootkit --resource-group rg-clientmanager
```

**AWS EB**:

```bash
eb status
eb logs --stream
eb health
```

**AWS EC2**:

```bash
aws ec2 describe-instances --instance-ids i-1234567890abcdef0
ssh -i clientmanager-key.pem ubuntu@<public-ip>
sudo journalctl -u clientmanager -f
```

### Performance e Otimização

#### Melhorar Velocidade de Deploy

1. **Cache de dependências**: Use cache do pip
2. **Deploy incremental**: Apenas arquivos modificados
3. **Paralelização**: Execute testes em paralelo

#### Monitoramento

```bash
# Azure
az monitor metrics list --resource clientmanager-rootkit

# AWS
aws cloudwatch get-metric-statistics --namespace AWS/ElasticBeanstalk
```

---

## 📊 Comparação: Shell vs Python

| Aspecto | Shell Scripts (.sh) | Python Scripts (.py) |
|---------|-------------------|---------------------|
| **Portabilidade** | ❌ Linux/macOS apenas | ✅ Windows/Linux/macOS |
| **Tratamento de Erros** | ⚠️ Básico | ✅ Robusto com exceptions |
| **Legibilidade** | ⚠️ Moderada | ✅ Excelente |
| **Manutenibilidade** | ❌ Difícil | ✅ Fácil |
| **Debugging** | ❌ Limitado | ✅ Ferramentas avançadas |
| **Reutilização** | ❌ Baixa | ✅ Alta (OOP) |
| **Testes** | ❌ Difícil | ✅ Fácil com pytest |

---

## 🚀 Próximos Passos

### Melhorias Planejadas

1. **Testes automatizados** para os scripts
2. **Configuração via arquivo** (YAML/JSON)
3. **Interface CLI** com argumentos
4. **Rollback automático** em caso de falha
5. **Integração com CI/CD** pipelines
6. **Monitoramento** e alertas
7. **Multi-região** deploy
8. **Blue-green deployment**

### Contribuição

Para contribuir com melhorias nos scripts:

1. Fork o repositório
2. Crie branch: `git checkout -b feature/script-improvement`
3. Faça alterações nos scripts em `scripts/`
4. Adicione testes se aplicável
5. Commit: `git commit -m "feat: improve script X"`
6. Push: `git push origin feature/script-improvement`
7. Abra Pull Request

---

<div align="center">

**📚 Documentação atualizada em:** `2024-12-19`

**🔄 Última conversão:** Shell → Python

**✅ Status:** Todos os scripts convertidos e testados

</div>
