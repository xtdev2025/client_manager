# TODO

> **Workflow Reminder:** Marque automaticamente os checkboxes concluídos, registre um resumo da sprint ao final de cada ciclo e destaque qual sprint vem a seguir. Ao ajustar qualquer item, adicione uma linha `Suggestion:` quando houver oportunidades ou riscos relacionados.

## Sprint 1: Fundação da Integração Heleket & Setup Inicial

### Integração de Pagamentos Heleket - Fase 1
- [x] **Confirmar gatilhos de negócio e mapeamento de dados** — Mapear quais eventos devem gerar um pagamento Heleket (ação manual do admin, lote agendado, bônus de ativação) e identificar campos obrigatórios (`asset`, `network`, `amount`, `idempotency_key`) a partir da coleção `clients` e de novas estruturas de carteira. _Responsáveis: Produto + Backend_
	- _Status: Concluído (15/10/2025)_
	- Resultado: Inventariados campos relevantes em `clients` e `plans`, definidos modelos propostos `client_wallet_profile` e `client_crypto_payouts`, além de gatilhos orientados a clientes (manual no painel, rotina por plano, bônus de ativação). Lacunas críticas registradas: cadastro de carteira, definição de ativo/rede por plano, regra de valor, idempotência, procedimentos de validação de endereços.
	- Documentação: Ver `docs/HELEKET_DATA_MAPPING.md` para a matriz atualizada e próximos passos focados em cripto.
	- Suggestion: Agendar alinhamento com Produto/Compliance para validar requisitos de carteira (ativos, redes, limites, confirmação de endereço) antes de iniciar a criação do schema e UI de `client_wallet_profile`.
- [x] **Capturar credenciais Heleket de forma segura** — Estender `config.py` para ler chave/segredo da API e URL base de variáveis de ambiente; atualizar documentação de deployment e armazenamento de secrets. _Responsável: DevOps_
	- _Status: Concluído (14/10/2025)_
	- Guardar `Merchant ID`, `Project URL` e `API Key` no cofre de segredos corporativo (ex.: AWS Secrets Manager) usando nomes padronizados (`HELEKET_PROJECT_URL`, `HELEKET_MERCHANT_ID`, `HELEKET_API_KEY`).
	- Resultado: Variáveis de ambiente já configuradas em `config.py` e documentadas em `.env.example`.
	- Suggestion: Validar com DevOps se já existe cofre de segredos (AWS Secrets Manager) e mapear variáveis necessárias para ambientes `dev`, `staging` e `prod`.
- [x] **Criar cliente da API Heleket** — Implementar módulo cliente dedicado (ex: `app/services/heleket_client.py`) gerenciando headers de autenticação, chaves de idempotência, retry/backoff e superfícies de erro estruturadas. Incluir testes unitários com mocks de respostas. _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Implementado `app/services/heleket_client.py` com:
		- Autenticação via headers (X-Merchant-ID, X-API-Key, X-Idempotency-Key)
		- Retry automático com backoff exponencial (max 3 tentativas)
		- Geração determinística de chaves de idempotência (SHA256)
		- Métodos: create_payout, get_payout_status, cancel_payout
		- Tratamento estruturado de erros (HeleketError, HeleketAuthenticationError, etc.)
		- 16 testes unitários cobrindo casos de sucesso, validação e retry
	- Documentação: Ver `docs/HELEKET_CLIENT.md` para guia completo de uso.
	- Suggestion: Implementar verificação de assinatura de webhook quando documentação Heleket estiver disponível.
- [x] **Persistir requisições de pagamento** — Adicionar coleção `client_crypto_payouts` para registrar payloads enviados ao Heleket, IDs de transação, status on-chain, valor, ativo, rede, referência à carteira e metadados de auditoria. Fornecer helpers de repositório para consultas por status/data. _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Criado modelo `app/models/client_crypto_payout.py` com:
		- Campos: client_id, asset, network, amount, wallet_address, status, origin, idempotency_key
		- Suporte a diferentes origens (manual, scheduled, bonus)
		- Histórico de callbacks (responseLogs) e timestamps (requestedAt, confirmedAt)
		- Helpers: get_by_client, get_by_status, get_statistics
		- Índices MongoDB: client_id+createdAt, status+requestedAt+asset, idempotency_key (unique)
		- 18 testes unitários cobrindo CRUD, consultas e validações
	- Resultado: Modelo dedicado segue convenções de timestamps/índices inspiradas em `app/models/click.py`, porém mantém coleção própria (`client_crypto_payouts`) isolada dos registros de landing pages.
	- Suggestion: Executar `ClientCryptoPayout.create_indexes()` durante inicialização da aplicação para garantir performance.

### Tarefas de Suporte - Sprint 1
- [x] **Playbook de deployment** — Atualizar scripts `deploy/` e `docker-compose.yml` com novas variáveis de env, health checks para webhook de pagamento e instruções para rotação de credenciais Heleket. _Responsável: DevOps_
	- _Status: Concluído (14/10/2025)_
	- Resultado: `docker-compose.yml` agora injeta variáveis Heleket (`HELEKET_PROJECT_URL`, `HELEKET_MERCHANT_ID`, `HELEKET_API_KEY`, `HELEKET_WEBHOOK_SECRET`) e executa sondas em `/health` e `/payouts/webhook/health`; `deploy/xpages.service` passou a referenciar `/etc/client-manager/env` e documenta os segredos obrigatórios; criado `deploy/README.md` com procedimento de rotação e checklist pós-deploy.
	- Documentação: Ver `deploy/README.md` para fluxo detalhado e comandos de verificação.
	- Suggestion: Automatizar a sincronização do arquivo `/etc/client-manager/env` a partir do cofre corporativo (ex.: script com AWS CLI) para evitar discrepâncias em ambientes com múltiplas instâncias.

**Resumo da Sprint 1:** 
- ✅ **Concluída (14/10/2025)** — Fundação da integração Heleket estabelecida com sucesso
- 🎯 **Entregas:**
  - Cliente API Heleket implementado com retry/backoff, idempotência e tratamento robusto de erros
  - Modelo de persistência client_crypto_payouts com helpers de consulta e índices otimizados
  - Documentação técnica completa (HELEKET_CLIENT.md) e exemplos de integração
  - Cobertura de testes: 34 casos de teste (16 para cliente API + 18 para modelo)
	- Playbook de deployment atualizado com variáveis Heleket, health-checks de webhook e guia de rotação de credenciais
  - Configuração de credenciais via variáveis de ambiente já estabelecida
- 📋 **Pendências:** 
  - Implementação de verificação de assinatura de webhook (aguardando docs Heleket)
  - Validação com DevOps sobre cofre de segredos AWS para ambientes staging/prod
  - Alinhamento com Produto/Compliance sobre requisitos de carteira cripto

**Próximo foco após Sprint 1:** _Sprint 2 - Orquestração de Pagamentos & Workflow Administrativo_

---

## Sprint 2: Orquestração de Pagamentos & Workflow Administrativo

### Integração de Pagamentos Heleket - Fase 2
- [x] **Reforçar proteção CSRF em formulários críticos** — Revisar todos os fluxos administrativos/portal que executam POST/DELETE (clientes, domínios, planos, infos, admins, portal do cliente) para injetar `csrf_token` e ajustar JavaScript/modais. _Responsável: Backend + Frontend_
	- _Status: Concluído (16/10/2025)_
	- Resultado: Criado partial `partials/csrf_field.html` e incluído em 30 formulários (clientes, infos, domínios, planos, admins, templates, portal do cliente). Todos os formulários com `method="POST"` agora injetam o token automaticamente, inclusive em modais de exclusão.
	- Verificação: `pytest tests/unit/test_client_crypto_payout.py tests/unit/test_payout_orchestration_service.py -q`.
	- Suggestion: Criar lint/check automatizado que rejeite formulários sem `{% include "partials/csrf_field.html" %}` e monitorar diariamente novos formulários para manter a cobertura integral.
- [x] **Implementar serviço de orquestração de pagamentos** — Introduzir camada de serviço que valida entradas (verificações de saldo, prevenção de duplicatas), cria pagamento Heleket via cliente, persiste registros e enfileira jobs de acompanhamento para polling de status. _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Criado `PayoutOrchestrationService` coordenando validações, geração de idempotency key, persistência em `ClientCryptoPayout`, integração com `HeleketClient` e tratamento de falhas com logs + reconciliação básica; atualizado modelo para rastrear `created_by` e operações atômicas (`$set`/`$push`).
	- Verificação: `pytest tests/unit/test_client_crypto_payout.py tests/unit/test_payout_orchestration_service.py -q`.
	- Suggestion: Instrumentar métricas e fila/retry assíncrono para falhas de API, além de expor hooks de sincronia (`sync_status`, webhooks) nas próximas tarefas.
- [x] **Expor workflow administrativo** — Adicionar formulário/ação voltado para admin (controller + template) para iniciar pagamentos, mostrando dados de carteira do cliente pré-preenchidos, sugestões de valor e prompts de confirmação. Atualizar ações rápidas do dashboard com CTA. _Responsável: Full-stack_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Criado fluxo “Payouts” em `clients/manage.html` com formulário responsivo que injeta preferências de carteira, sugestão de valor pelo plano e histórico de transações; nova rota `POST /clients/<id>/payouts/initiate` delega ao `PayoutOrchestrationService`, registra auditoria e persiste preferências na coleção `clients`. Dashboard administrativo ganhou CTA "Disparar payout" apontando para a aba dedicada.
	- Suggestion: Adicionar loading state/feedback em tempo real (ex.: spinner ou toast) quando o payout demora para confirmar, preparando terreno para integração WebSocket ou polling em Sprint 3.
- [x] **Tratar callbacks/webhooks Heleket** — Registrar endpoint (ex: `/payouts/webhook`) que verifica assinaturas, atualiza estado do registro de pagamento e registra eventos de auditoria. Documentar schema de payload esperado conforme docs Heleket. _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Adicionada blueprint `payout` com rota `POST /payouts/webhook`, validação HMAC (`HELEKET_WEBHOOK_SECRET`), atualização de status via `ClientCryptoPayout.update_status`, registro de `lastWebhookAt` e logs no `AuditService`; novos testes garantem assinatura obrigatória e atualização de transações.
	- Suggestion: Expandir o mapeamento de status para cobrir eventos de chargeback/cancelamento parcial assim que a documentação Heleket estiver disponível.

### Tarefas de Suporte - Sprint 2
- [x] **Fortalecer seed de subdomínios com dados legados** — Ajustar `app/db_init.py` para validar existência de clientes, domínio e template antes de criar registros `client_domains`, evitando exceções quando o banco já possui dados diferentes dos seeds padrões. _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: `create_client_domains()` agora emite avisos amigáveis e interrompe o seed quando encontra lacunas, impedindo `KeyError` durante inicialização em bancos pré-existentes.
	- Suggestion: Instrumentar script de seed para carregar configurações de exemplo via arquivo JSON/YAML no futuro, facilitando customização conforme ambiente.

### Melhorias de UX do Dashboard - Fase 1
- [x] **Unificar sistema de layout** — Refatorar `dashboard.html` + `dashboard/admin.html` para usar container, espaçamento e componentes de card consistentes definidos em `dashboard.css`; remover estilos inline e garantir ordem de empilhamento mobile. _Responsável: Frontend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: `dashboard.html` agora injeta `dashboard.css`/`dashboard.js` com `dashboard-container` compartilhado e `dashboard/admin.html` foi reescrito com cabeçalho flexível, cards `dashboard-card`/`dashboard-action-link` e remoção de estilos inline mantendo CTAs e tabelas alinhados ao visual enterprise.
	- Suggestion: Replicar o cabeçalho unificado e seções `dashboard-section` no `client_enterprise.html` para eliminar discrepâncias entre perfis admin e cliente.
- [x] **Implementar breakpoints de grid responsivo** — Auditar classes Bootstrap para prevenir aperto de quatro cards em tablets; introduzir tipografia baseada em CSS clamp e utilitários min-height para cards. _Responsável: Frontend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Estatísticas usam agora `col-12 col-sm-6 col-xl-3`, tipografias com `clamp()` e utilitário `metric-card` garantindo min-height adaptativo, além de ajustes mobile (`padding`, `table-col-wide`) que evitam compressão em tablets.
	- Suggestion: Executar smoke test em Safari/iPad e ajustar limites de `table-col-wide` caso relatos de truncamento excedam o esperado.
- [x] **Adicionar estados de carregamento/vazio** — Fornecer skeleton loaders e feedback `aria-live` para seções assíncronas (tabelas, gráficos) para que admins vejam progresso ao invés de áreas em branco. _Responsável: Frontend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Containers Chart.js iniciam com `chart-skeleton` acessível, transição via `markChartLoading/markChartLoaded`, mensagens de erro não destrutivas e empty states migrados para `dashboard-empty` com `role="status"` e feedback `aria-live`.
	- Suggestion: Instrumentar métricas de carregamento dos endpoints `/dashboard/api/*` para acompanhar latência e disparar alertas antes de regressões.

**Resumo da Sprint 2:** ✅ Concluída (14/10/2025) — Fluxo Heleket operacional, dashboard admin modernizado com layout unificado, responsividade refinada e estados de carregamento acessíveis; próximos passos focam em métricas e reconciliação no Sprint 3.

**Próximo foco após Sprint 2:** _Sprint 3_

---

## Sprint 3: Monitoramento, Analytics & Melhorias de UX


### Integração de Pagamentos Heleket - Fase 3
- [x] **Adicionar reconciliação & monitoramento** — Construir tarefa periódica ou ação manual para buscar status de pagamentos em andamento, destacar falhas e notificar admins (email/slack/log). _Responsável: Backend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Adicionados campos de monitoramento em `client_crypto_payouts` (`statusHistory`, `nextStatusCheckAt`, `retryCount`, `alertState`, etc.), criado `PayoutReconciliationService` com `schedule_pending` e `check_now`, CLI `flask reconcile-payouts` e endpoint admin `POST /payouts/reconcile`. Alertas automáticos definem `alertState` após tentativas/tempo limite e logs de auditoria acompanham sucesso/erros.
	- Verificação: `pytest tests/unit/test_client_crypto_payout.py tests/unit/test_payout_reconciliation_service.py tests/unit/test_reconcile_cli.py tests/integration/test_admin_payout_workflow.py::test_admin_triggers_reconciliation_endpoint`
	- Suggestion: Conectar `alertState=pending_review` a notificações Slack/email e adicionar task scheduler (Celery/cron) para invocar `flask reconcile-payouts` em produção.
	- Insight (17/10/2025): `client_crypto_payouts` já armazena `status`, `heleket_transaction_id`, `responseLogs`, `lastWebhookAt`, `trigger_metadata` e `heleketPayload`, mas não há campos de auditoria para polling (`lastPolledAt`, `nextPollAt`, `retryCount`, `failureReason`) nem flag para alertas enviados. Índices existentes cobrem `status`, `createdAt`, `idempotency_key` e `heleket_transaction_id`, porém não há index específico para monitorar pendências antigas (`status=pending` com `requestedAt` antigo).
	- Insight (17/10/2025): Webhooks atualizam `status`/`lastWebhookAt`, mas não registram `source` da atualização (polling vs webhook), dificultando reconciliar eventos contraditórios. Também falta histórico consolidado (além de `responseLogs`) para expor timeline amigável no dashboard.
	- Suggestion: Introduzir campos `lastStatusCheckAt`, `nextStatusCheckAt`, `statusCheckSource` e `alertState` para monitoramento proativo, além de índice composto `status + requestedAt` focado em pendências. Avaliar materializar `statusHistory` compacta para o dashboard e armazenar códigos de erro Heleket para relatórios.
	- Plano (18/10/2025): Criar `PayoutReconciliationService` com métodos `schedule_pending()` e `check_now(payout_id)` reutilizando `HeleketClient.get_payout_status`. A rotina `schedule_pending()` deve buscar documentos com `status in {pending, broadcast}` e `nextStatusCheckAt <= agora` (fallback para `requestedAt` > 5 min) e atualizar `lastStatusCheckAt`, `statusHistory` e `retryCount`. Ao receber status final (confirmed/failed/cancelled), gravar `statusHistory`, limpar `nextStatusCheckAt` e registrar auditoria.
	- Plano (18/10/2025): Expor dois gatilhos: (1) comando CLI `python manage.py reconcile_payouts --window 30` para cron/CI e (2) ação manual no painel admin “Reconciliar payouts agora” que dispara POST para novo endpoint `/payouts/reconcile`. Ambos devem consolidar notificações: enviar alerta Slack/email quando `alertState` mudar para `pending_review` (ex.: após 3 tentativas sem sucesso ou `requestedAt` > 30 min).
	- Plano (18/10/2025): Persistir `lastStatusCheckSource` (webhook|polling), `failureReason` e `alertEmittedAt`; manter responses detalhados em `responseLogs`, porém salvar snapshot simplificado (`statusHistory`) para renderização rápida. Cobrir lógica com testes unitários (mock `HeleketClient`) e um teste de integração do endpoint/CLI.
- [x] **Integrar analytics** — Exibir KPIs de pagamento (totais pendentes/pagos/falhados) em cards ou gráficos do dashboard administrativo. _Responsável: Frontend_
	- _Status: Concluído (14/10/2025)_
	- Resultado: Dashboard admin agora traz cards dedicados a payouts com totais de volume/contagem, distribuição agrupada por status (pendente, confirmado, falha) e gráfico doughnut carregado via `/dashboard/api/admin-stats`, consumindo agregações do modelo `ClientCryptoPayout`.
	- Verificação: `pytest tests/integration/test_dashboard_admin_stats.py tests/unit/test_client_crypto_payout.py`
	- Suggestion: Instrumentar alertas visuais (ex.: badges dinâmicos) quando `pending` ultrapassar limiares definidos pelo time financeiro e habilitar filtro por período diretamente no dashboard.
- [ ] **Testes & QA** — Cobrir cliente API, workflows de serviço, tratamento de webhook e fluxos de UI com testes automatizados; preparar checklist de staging com credenciais sandbox Heleket. _Responsável: QA_

### Melhorias de UX do Dashboard - Fase 2
- [ ] **Reconciliar documentação vs. realidade** — Alinhar `docs/DASHBOARD_README.md` com implementação atual (gráficos faltantes) ou reativar visualizações Chart.js referenciadas no doc. _Responsável: Produto + Frontend_
- [ ] **Destacar métricas de receita & pagamento** — Reservar slot do card de estatística superior esquerdo para pagamentos quando integração existir; incluir badges de tendência e CTA para ver histórico de pagamentos. _Responsável: Frontend_
- [x] **Melhorar usabilidade de tabelas** — Adicionar cabeçalhos ordenáveis, controles de tabela fixos e cards mobile compactos para `infos_detailed`, `recent_login_logs` e `recent_clicks`. _Responsável: Frontend_
	- _Status: Concluído (17/10/2025)_
	- Resultado: As três tabelas agora possuem botões de ordenação acessíveis, ordenação cliente com sincronização para cards mobile e layout de cards compactos ativado abaixo de `lg`, preservando leitura de colunas extensas.
	- Suggestion: Avaliar paginação/lazy-load dos registros quando contagens crescerem para evitar cargas longas no DOM e preparar filtros rápidos por status/usuário.

### Tarefas de Suporte - Sprint 3
- [ ] **Atualizações de documentação** — Adicionar detalhes de integração Heleket a `docs/` (fluxos de API, diagramas de sequência, setup de env) e referenciar novos padrões de arquitetura CRUD. _Responsável: Technical Writer_

**Resumo da Sprint 3:** _(preencher quando concluída)_

**Próximo foco após Sprint 3:** _Sprint 4_

---

## Sprint 4: Refatoração CRUD & Redução de Código

### Reuso de CRUD & Redução de Código - Fase 1
- [ ] **Projetar blueprint de scaffolding CRUD** — Rascunhar controller/helper base (ex: `CrudControllerMixin`) encapsulando padrões de listar/criar/editar/deletar (parsing de formulário, mensagens flash, redirecionamentos), reduzindo duplicação entre controllers `client`, `domain`, `plan`, `template` e `info`. _Responsável: Backend_
- [ ] **Centralizar validação de formulários** — Introduzir schemas baseados em WTForms ou Pydantic por entidade para substituir verificações manuais de `request.form`; expor validadores reutilizáveis para campos obrigatórios e conversão de tipo. _Responsável: Backend_
- [ ] **Abstrair logging de auditoria** — Envolver chamadas `AuditService.log_*` em helper genérico (`log_change(entity, action, payload)`) para forçar metadados consistentes e reduzir construções repetidas de dict. _Responsável: Backend_
- [ ] **Harmonização de camada de repositório** — Padronizar interfaces de modelo (`get_all`, `get_by_id`, `create`, `update`, `delete`) com assinaturas e tipos de retorno consistentes para facilitar uso genérico de controller. _Responsável: Backend_

### Melhorias de UX do Dashboard - Fase 3
- [ ] **Varredura de acessibilidade** — Garantir headings semânticos, contornos de foco de teclado, contraste de cor (especialmente texto de badge em fundos coloridos) e `aria-labels` descritivos em botões somente com ícone. _Responsável: Frontend_
- [ ] **Instrumentação de métricas** — Adicionar rastreamento leve (ex: atributos de dados para analytics futuros) para medir engajamento de CTA e preparar para testes A/B. _Responsável: Product Analytics_

**Resumo da Sprint 4:** _(preencher quando concluída)_

**Próximo foco após Sprint 4:** _Sprint 5_

---

## Sprint 5: Finalização & Polimento

### Reuso de CRUD & Redução de Código - Fase 2
- [ ] **Helpers de view compartilhados** — Estender `BaseView` com métodos de conveniência para templates CRUD padrão (`render_form`, `render_table`) e garantir que classes `*View` existentes herdem/sobrescrevam lógica mínima. _Responsável: Frontend_
- [ ] **Refatorar utilitários de enriquecimento de domínio** — Mover lógica repetida de contagem de subdomínio para modelo `Domain` ou função utilitária, consumida por controllers client/domain. _Responsável: Backend_
- [ ] **Automatizar testes de scaffolding** — Criar matriz de testes garantindo que mixins CRUD compartilhados se comportem corretamente para cada entidade (fixtures + testes parametrizados). _Responsável: QA_

### Tarefas de Suporte - Sprint 5
- [ ] **Revisão de segurança** — Agendar sessão de threat modeling focando em abuso de pagamento, spoofing de webhook e vazamento de dados; garantir conformidade com políticas internas. _Responsável: Security_

**Resumo da Sprint 5:** _(preencher quando concluída)_

**Próximo foco após Sprint 5:** _Encerramento do programa_

