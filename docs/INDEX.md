# 📚 Índice da Documentação

## 🚀 Início Rápido

- [README Principal](../README.md) - Visão geral do projeto
- [API Quick Reference](API_QUICK_REFERENCE.md) - Referência rápida da API
- [Routes Documentation](ROUTES_DOCUMENTATION.md) - Documentação de todas as rotas

## 🏗️ Arquitetura

- [Architecture](ARCHITECTURE.md) - Arquitetura completa do sistema (MVC + Services + Schemas)
- [Template Fields System](TEMPLATE_FIELDS_SYSTEM.md) - Sistema de campos dos templates
- [Dashboard README](DASHBOARD_README.md) - Guia do dashboard administrativo

## 💰 Integração de Pagamentos (Heleket)

- [Heleket README](HELEKET_README.md) - Documentação completa da integração Heleket
- [Heleket Client](HELEKET_CLIENT.md) - Cliente da API Heleket e exemplos de uso
- [Heleket Data Mapping](HELEKET_DATA_MAPPING.md) - Mapeamento de dados e estruturas
- [Heleket Phase 1 Summary](HELEKET_PHASE1_SUMMARY.md) - Resumo da implementação inicial

## ☁️ Deploy e Infraestrutura

### AWS

- [AWS Deployment](AWS_DEPLOYMENT.md) - Guia completo de deploy na AWS (EB, EC2, ECS, Lambda)
- [AWS Credentials Setup](AWS_CREDENTIALS_SETUP.md) - Configuração de credenciais AWS
- [AWS Credentials Quickstart](AWS_CREDENTIALS_QUICKSTART.md) - Quickstart de credenciais
- [Deploy to EC2](DEPLOY_TO_EC2.md) - Guia específico para EC2

### Azure

- [Azure Deployment](AZURE_DEPLOYMENT.md) - Guia completo de deploy no Azure (App Service + VM)

### Docker

- [Docker Internal Network Solution](SOLUTION_DOCKER_INTERNAL_NETWORK.md) - Configuração de rede Docker

## 🔄 Migração e Modernização

- [Modernization Summary](MODERNIZATION_SUMMARY.md) - Resumo completo da modernização (Shell→Python + Heleket)

## 🔧 Scripts e Desenvolvimento

- [Scripts Documentation](SCRIPTS_DOCUMENTATION.md) - Documentação de todos os scripts Python
- [CI/CD Fix](CI_FIX_GITHUB_ACTIONS.md) - Correções no GitHub Actions

## 🔌 API e Integração

- [Swagger Implementation](SWAGGER_IMPLEMENTATION.md) - Implementação do Swagger/OpenAPI
- [Swagger Endpoints Report](SWAGGER_ENDPOINTS_REPORT.md) - Relatório de 63+ endpoints

## 📝 Projeto e Gestão

- [Changelog](../CHANGELOG.md) - Histórico completo de mudanças
- [TODO](../TODO.md) - Backlog e sprints de desenvolvimento
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Código de conduta
- [Contributing Guidelines](../.github/CONTRIBUTING.md) - Como contribuir
- [Copilot Instructions](../.github/copilot-instructions.md) - Instruções para AI

## 📂 Estrutura de Documentação

```
docs/
├── INDEX.md                              # Este arquivo - índice completo
├── README.md                             # Overview da documentação
│
├── 🏗️ Arquitetura
│   ├── ARCHITECTURE.md                   # Arquitetura MVC + Services + Schemas
│   ├── ROUTES_DOCUMENTATION.md           # Documentação de rotas
│   └── TEMPLATE_FIELDS_SYSTEM.md         # Sistema de templates
│
├── 💰 Integração Heleket
│   ├── HELEKET_README.md                 # Visão geral da integração
│   ├── HELEKET_CLIENT.md                 # Cliente da API
│   ├── HELEKET_DATA_MAPPING.md           # Mapeamento de dados
│   └── HELEKET_PHASE1_SUMMARY.md         # Resumo Sprint 1
│
├── ☁️ Deploy
│   ├── AWS_DEPLOYMENT.md                 # Deploy AWS completo
│   ├── AWS_CREDENTIALS_SETUP.md          # Credenciais AWS
│   ├── AWS_CREDENTIALS_QUICKSTART.md     # Quickstart AWS
│   ├── DEPLOY_TO_EC2.md                  # EC2 específico
│   ├── AZURE_DEPLOYMENT.md               # Deploy Azure
│   └── SOLUTION_DOCKER_INTERNAL_NETWORK.md
│
├── 🔌 API
│   ├── API_QUICK_REFERENCE.md            # Referência rápida
│   ├── SWAGGER_IMPLEMENTATION.md         # Implementação Swagger
│   └── SWAGGER_ENDPOINTS_REPORT.md       # Relatório de endpoints
│
├── 🔄 Modernização
│   ├── MODERNIZATION_SUMMARY.md          # Resumo da modernização

│
├── 🔧 Scripts e CI/CD
│   ├── SCRIPTS_DOCUMENTATION.md          # Scripts Python
│   └── CI_FIX_GITHUB_ACTIONS.md          # Correções CI/CD
│
└── 📊 Dashboard
    └── DASHBOARD_README.md               # Dashboard administrativo
```

## 🎯 Para Desenvolvedores

### Primeiro Acesso

1. Leia o [README Principal](../README.md)
2. Entenda a [Arquitetura](ARCHITECTURE.md) - estrutura MVC com Services
3. Consulte a [API Quick Reference](API_QUICK_REFERENCE.md)
4. Veja as [Rotas](ROUTES_DOCUMENTATION.md)

### Desenvolvimento

- **Estrutura**: [Architecture](ARCHITECTURE.md) explica Models, Services, Controllers, Schemas
- **Templates**: [Template Fields System](TEMPLATE_FIELDS_SYSTEM.md) para páginas customizadas
- **Dashboard**: [Dashboard README](DASHBOARD_README.md) para KPIs e métricas
- **Pagamentos**: [Heleket README](HELEKET_README.md) para integração de payouts

### Deploy

- **AWS**: [AWS Deployment](AWS_DEPLOYMENT.md) - 4 opções (EB, EC2, ECS, Lambda)
- **Azure**: [Azure Deployment](AZURE_DEPLOYMENT.md) - App Service + VM
- **Docker**: Ver [docker-compose.yml](../docker-compose.yml) na raiz

### Contribuindo

- [Contributing Guidelines](../.github/CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Changelog](../CHANGELOG.md)
- [TODO](../TODO.md) - Veja sprints e tarefas em andamento
