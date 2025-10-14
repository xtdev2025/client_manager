# 📋 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased] - 2025-10-14

### 🆕 Adicionado

- **Workflow Reminder**: Inserido aviso no `TODO.md` para reforçar auto-completar tarefas, registrar resumos de sprint e sinalizar o próximo foco.
- **Doc Heleket Data Mapping**: Criado `docs/HELEKET_DATA_MAPPING.md` com inventário de campos orientado a `clients`, gatilhos propostos e lacunas para payouts em cripto.

### 🔄 Modificado

- **Guidelines de Contribuição**: Atualização de `.github/copilot-instructions.md` para alinhar o trabalho com `TODO.md`, exigir sugestões contextuais, resumos de sprint e sincronização com `CHANGELOG.md`.
- **TODO.md**: Item "Confirmar gatilhos de negócio e mapeamento de dados" mantém status concluído com foco em ativos digitais, introduzindo `client_wallet_profile` e `client_crypto_payouts` como entregáveis futuros.
- **docs/HELEKET_DATA_MAPPING.md**: Revisado para refletir o Heleket como gateway cripto, trocar requisitos bancários por carteira/ativo/rede e adicionar pauta de alinhamento com Produto/Compliance.

---

## [2.1.0] - 2024-12-19

### 🆕 Adicionado

- **Scripts Python**: Conversão completa de 6 scripts shell para Python
  - `scripts/startup.py` - Script de inicialização para produção
  - `scripts/test_workflows.py` - Teste de workflows essenciais
  - `scripts/test_all_workflows.py` - Teste completo de workflows
  - `scripts/aws_eb_deploy.py` - Deploy AWS Elastic Beanstalk
  - `scripts/aws_ec2_deploy.py` - Deploy AWS EC2
  - `scripts/azure_deploy.py` - Deploy Azure App Service

- **Documentação Expandida**:
  - `docs/SCRIPTS_DOCUMENTATION.md` - Documentação completa dos scripts
  - `docs/MIGRATION_SHELL_TO_PYTHON.md` - Detalhes da migração
  - `CHANGELOG.md` - Este arquivo de changelog

### 🔄 Modificado

- **README.md**:
  - Atualização dos comandos de deploy para Python
  - Nova seção de modernização
  - Documentação adicional expandida
  - Changelog recente adicionado
  - Estrutura do projeto atualizada

### 🗑️ Removido

- **Scripts Shell Legacy**:
  - `startup.sh` → Convertido para `scripts/startup.py`
  - `test-workflows.sh` → Convertido para `scripts/test_workflows.py`
  - `test-all-workflows.sh` → Convertido para `scripts/test_all_workflows.py`
  - `scripts/aws_eb_deploy.sh` → Convertido para `scripts/aws_eb_deploy.py`
  - `scripts/aws_ec2_deploy.sh` → Convertido para `scripts/aws_ec2_deploy.py`
  - `scripts/azure_deploy.sh` → Convertido para `scripts/azure_deploy.py`

### 🔧 Melhorias Técnicas

- **Portabilidade**: Scripts agora funcionam em Windows, Linux e macOS
- **Tratamento de Erros**: Exception handling robusto em Python
- **Estrutura OOP**: Classes organizadas para melhor manutenibilidade
- **Logging Aprimorado**: Feedback visual com emojis e mensagens claras
- **Permissões**: Scripts Python configurados como executáveis

---

## [2.0.0] - 2024-11-XX

### 🆕 Adicionado

- **Camada de Serviços**: Implementação de services layer
  - `AuthService` - Gerenciamento de autenticação
  - `ClientService` - Lógica de negócio para clientes
  - `AuditService` - Sistema de auditoria

- **Validação com Pydantic**: Schemas de validação robusta
  - `UserCreateSchema` - Validação de usuários
  - `ClientCreateSchema` - Validação de clientes
  - `AdminCreateSchema` - Validação de administradores

- **Rate Limiting**: Proteção contra abuso com Flask-Limiter
- **Sistema de Auditoria**: Logs automáticos de operações sensíveis
- **Type Hints**: Tipagem estática em funções principais
- **Testes Automatizados**: Suite completa com pytest

### 🔄 Modificado

- **Arquitetura MVC**: Separação clara de responsabilidades
- **Documentação API**: Swagger/OpenAPI 3.0.3 implementado
- **Segurança**: Melhorias em autenticação e autorização

---

## [1.5.0] - 2024-10-XX

### 🆕 Adicionado

- **API Documentation**: Swagger UI em `/api/docs`
- **63+ Endpoints**: Documentação completa da API
- **OpenAPI 3.0.3**: Especificação padronizada

### 🔄 Modificado

- **Interface**: Melhorias no dashboard
- **Performance**: Otimizações de consultas MongoDB

---

## [1.0.0] - 2024-09-XX

### 🆕 Adicionado

- **Sistema Base**: Implementação inicial do Client Manager
- **Autenticação**: Sistema completo de login/logout
- **RBAC**: Controle de acesso baseado em funções
- **CRUD Completo**: Gestão de clientes, admins, planos
- **Templates**: Sistema de templates personalizáveis
- **Domínios**: Gestão de domínios com Cloudflare
- **Informações Bancárias**: Gerenciamento seguro de dados
- **Dashboard**: Painéis específicos por tipo de usuário
- **Auditoria**: Logs de acesso e operações

### 🛠️ Tecnologias

- **Backend**: Flask 2.3.3, PyMongo 4.6.0
- **Frontend**: Bootstrap 5, Jinja2
- **Database**: MongoDB 4.6+
- **Autenticação**: Flask-Login, Flask-Bcrypt
- **Validação**: Flask-WTF, Email-validator

---

## Tipos de Mudanças

- `🆕 Adicionado` para novas funcionalidades
- `🔄 Modificado` para mudanças em funcionalidades existentes
- `🗑️ Removido` para funcionalidades removidas
- `🔧 Melhorias Técnicas` para melhorias internas
- `🐛 Corrigido` para correções de bugs
- `🔒 Segurança` para correções de vulnerabilidades

---

## Links de Comparação

- [2.1.0...HEAD](https://github.com/rootkitoriginal/client_manager/compare/v2.1.0...HEAD)
- [2.0.0...2.1.0](https://github.com/rootkitoriginal/client_manager/compare/v2.0.0...v2.1.0)
- [1.5.0...2.0.0](https://github.com/rootkitoriginal/client_manager/compare/v1.5.0...v2.0.0)
- [1.0.0...1.5.0](https://github.com/rootkitoriginal/client_manager/compare/v1.0.0...v1.5.0)

---

<div align="center">

**📝 Mantido por**: [rootkitoriginal](https://github.com/rootkitoriginal)

**📅 Última atualização**: 19 de Dezembro de 2024

</div>
