# 📋 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased] - 2025-10-15

### 🆕 Adicionado

- (Sprint 3) Analytics de pagamentos: Dashboard administrativo exibe cards de KPIs, gráfico doughnut e distribuição de volume alimentados por agregações de `ClientCryptoPayout`, consumidos via `/dashboard/api/admin-stats`.
- (Sprint 3) Reconciliação Heleket: Novo `PayoutReconciliationService` com métodos `schedule_pending`/`check_now`, comando CLI `flask reconcile-payouts` e endpoint admin `POST /payouts/reconcile` para disparo manual.
- (Sprint 2) Workflow administrativo de payouts: Nova aba "Payouts" em `clients/manage.html` com formulário guiado, histórico de transações, âncoras de navegação e persistência de preferências de carteira por cliente via `Client.update_crypto_wallet_preferences`.
- (Sprint 2) Endpoint `/payouts/webhook`: Blueprint dedicada com validação HMAC (`HELEKET_WEBHOOK_SECRET`), atualização de status em `ClientCryptoPayout.update_status` e registro de auditoria centralizado.
- (Sprint 2) Testes automatizados de payouts: Novos cenários garantem fluxo administrativo (`tests/integration/test_admin_payout_workflow.py`) e callbacks Heleket (`tests/unit/test_payout_webhook.py`).
- (Sprint 2) Partial CSRF reutilizável: `app/templates/partials/csrf_field.html` centraliza o input `csrf_token` e foi incluído em todos os formulários `POST` para padronizar a proteção.
- (Sprint 1) Health-check endpoints operacionais: adicionados `GET /health` e `GET /payouts/webhook/health` para suporte a sondas de infraestrutura e alerta de segredo ausente.
- (Sprint 5) Helpers de view compartilhados: `BaseView` extendido com métodos `render_form` e `render_table` para padronização de templates CRUD; todas as classes `*View` atualizadas para usar conveniência mínima.
- (Sprint 5) Método centralizado de contagem de subdomínios: `Domain.get_subdomain_count()` implementado e consumido por controllers `client` e `domain` para eliminar duplicação.
- (Sprint 5) Testes automatizados de scaffolding: Suite parametrizada `test_crud_scaffolding.py` com 40 testes validando comportamento consistente dos mixins CRUD para todas as entidades (domain, client, plan, template, info).
- (Sprint 5) Sessão de threat modeling agendada: Foco em vetores de abuso de pagamento, spoofing de webhook e vazamento de dados, com garantia de conformidade às políticas internas de segurança.
- (Sprint 5) Acessibilidade aprimorada: Adicionados `aria-label` em botões de ícones únicos em templates de listagem (clients, domains, plans, infos) para conformidade WCAG.
- (Sprint 5) Instrumentação de métricas: Atributos `data-cta` e `data-section` adicionados aos links de estatísticas do dashboard para suporte futuro a analytics e testes A/B.

### 🔄 Modificado

- (Documentação) Atualização completa de toda documentação para refletir o estado atual do projeto: `README.md`, `docs/INDEX.md`, `docs/ARCHITECTURE.md`, `docs/README.md`, `docs/MODERNIZATION_SUMMARY.md` e `docs/SCRIPTS_DOCUMENTATION.md` foram atualizados removendo referências a arquivos inexistentes (`DEPLOY_AWS.md`, `DEPLOY_AZURE.md`, `MIGRATION_GUIDE.md`, `API_DOCUMENTATION.md`) e adicionando documentação completa da integração Heleket, sistema de paginas (templates Jinja2), estrutura atual (controllers, services, schemas, repositories) e estado dos scripts (atuais vs. descontinuados).
- (Sprint 3) Modelo `ClientCryptoPayout` expandido com `statusHistory`, rastreio de polling (`lastStatusCheckAt`, `nextStatusCheckAt`, `retryCount`, `alertState`) e normalização de status compartilhada para webhooks/polling.
- (Sprint 3) Blueprint de autenticação voltou a expor rotas em `/auth/*`, mantendo compatibilidade com fluxos administrativos e testes de integração.
- (Sprint 3) Tabelas do dashboard admin: cabeçalhos clicáveis com ordenação client-side, sincronização com cards mobile e estilos refinados em `dashboard.js`, `dashboard.css` e `dashboard/admin.html`.
- (Sprint 3) Dashboard admin: card superior esquerdo prioriza KPIs de pagamentos Heleket com badge de tendência e CTA para histórico.
- (Sprint 3) Documentação: `docs/DASHBOARD_README.md` e `docs/HELEKET_README.md` atualizados com métricas reais, checklist de ambiente e diagrama de sequência do fluxo Heleket.
- (Sprint 4) Auditoria centralizada: Controllers de autenticação, admins, clientes e payouts, além do `PayoutReconciliationService`, agora usam `audit_helper.log_*` com metadados de ator/IP opcionais para garantir consistência nos registros.
- (Sprint 4) Backlog atualizado: `TODO.md` ganhou tarefa para analisar o sistema, padronizar schemas para os models e documentar convenções antes da entrega.
- (Sprint 2) Dashboards administrativos: `dashboard.html`, `dashboard/admin.html` e `dashboard/admin_enterprise.html` agora compartilham o cabeçalho `dashboard-section`, cards reutilizáveis e quick actions consistentes.
- (Sprint 2) Responsividade do dashboard: `dashboard.css` ganhou tipografia com `clamp()`, utilitário `metric-card`, ajustes `table-col-wide` e padding mobile para manter legibilidade em tablets.
- (Sprint 2) Feedback assíncrono: `dashboard.js` passou a controlar `markChartLoading/markChartLoaded`, skeleton loaders e mensagens `aria-live` ao carregar gráficos (admin e cliente enterprise).
- (Sprint 2) Dashboard Enterprise: Quick action "Disparar payout" agora aponta diretamente para o novo fluxo administrativo.
- (Sprint 2) Documentação operacional: `TODO.md` e `.github/copilot-instructions.md` reforçam o workflow de sprints (auto-completar itens, registrar resumos e sinalizar próximos focos).
- (Sprint 2) `docs/HELEKET_DATA_MAPPING.md`: Revisado para refletir requisitos de carteira/ativo/rede e próximos alinhamentos com Produto/Compliance.
- (Sprint 2) Base de testes: `tests/conftest.py` limpa `client_crypto_payouts` por padrão para evitar vazamento entre cenários.
- (Sprint 1) Playbook de deployment: `docker-compose.yml` injeta credenciais Heleket com health-checks da rota de webhook; `deploy/xpages.service` referencia `/etc/client-manager/env` e `deploy/README.md` detalha rotação de segredos.
- (Sprint 4) Normalização de formulários: `app.schemas.forms.parse_form` ignora campos ausentes para manter defaults dos schemas e impedir validações falsas para `status` e flags booleanas.
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

**📅 Última atualização**: 14 de Outubro de 2025

</div>
