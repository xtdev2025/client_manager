# 📋 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased] - 2025-10-16

### 🆕 Adicionado

- (Sprint 2) Workflow administrativo de payouts: Nova aba "Payouts" em `clients/manage.html` com formulário guiado, histórico de transações, âncoras de navegação e persistência de preferências de carteira por cliente via `Client.update_crypto_wallet_preferences`.
- (Sprint 2) Endpoint `/payouts/webhook`: Blueprint dedicada com validação HMAC (`HELEKET_WEBHOOK_SECRET`), atualização de status em `ClientCryptoPayout.update_status` e registro de auditoria centralizado.
- (Sprint 2) Testes automatizados de payouts: Novos cenários garantem fluxo administrativo (`tests/integration/test_admin_payout_workflow.py`) e callbacks Heleket (`tests/unit/test_payout_webhook.py`).
- (Sprint 2) Partial CSRF reutilizável: `app/templates/partials/csrf_field.html` centraliza o input `csrf_token` e foi incluído em todos os formulários `POST` para padronizar a proteção.
- (Sprint 1) Health-check endpoints operacionais: adicionados `GET /health` e `GET /payouts/webhook/health` para suporte a sondas de infraestrutura e alerta de segredo ausente.

### 🔄 Modificado

- (Sprint 2) Dashboard Enterprise: Quick action "Disparar payout" agora aponta diretamente para o novo fluxo administrativo.
- (Sprint 2) Documentação operacional: `TODO.md` e `.github/copilot-instructions.md` reforçam o workflow de sprints (auto-completar itens, registrar resumos e sinalizar próximos focos).
- (Sprint 2) `docs/HELEKET_DATA_MAPPING.md`: Revisado para refletir requisitos de carteira/ativo/rede e próximos alinhamentos com Produto/Compliance.
- (Sprint 2) Base de testes: `tests/conftest.py` limpa `client_crypto_payouts` por padrão para evitar vazamento entre cenários.
- (Sprint 1) Playbook de deployment: `docker-compose.yml` injeta credenciais Heleket com health-checks da rota de webhook; `deploy/xpages.service` referencia `/etc/client-manager/env` e `deploy/README.md` detalha rotação de segredos.

### 🐛 Corrigido

- (Sprint 2) Seed de subdomínios resiliente: `create_client_domains()` agora valida pré-condições e emite avisos, evitando `KeyError` em bancos com dados legados.

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
