# TODO

> **Workflow Reminder:** Marque automaticamente os checkboxes concluídos, registre um resumo da sprint ao final de cada ciclo e destaque qual sprint vem a seguir. Ao ajustar qualquer item, adicione uma linha `Suggestion:` quando houver oportunidades ou riscos relacionados.

## Sprint 1: Fundação da Integração Heleket & Setup Inicial

### Integração de Pagamentos Heleket - Fase 1
- [ ] **Confirmar gatilhos de negócio e mapeamento de dados** — Mapear quais eventos devem gerar um pagamento Heleket (ação manual do admin, lote agendado, baseado em limite) e identificar campos obrigatórios (`amount`, `currency`, informações bancárias do beneficiário) das coleções existentes (`infos`, `clients`). _Responsáveis: Produto + Backend_
	- _Status: Em andamento (14/10/2025)_
	- Suggestion: Levantar fluxos atuais de criação de pagamentos com líderes de produto e extrair modelo de dados a partir de `app/models/info.py` e `app/models/client.py` antes de entrevistas com stakeholders.
- [ ] **Capturar credenciais Heleket de forma segura** — Estender `config.py` para ler chave/segredo da API e URL base de variáveis de ambiente; atualizar documentação de deployment e armazenamento de secrets. _Responsável: DevOps_
	- Guardar `Merchant ID`, `Project URL` e `API Key` no cofre de segredos corporativo (ex.: AWS Secrets Manager) usando nomes padronizados (`HELEKET_PROJECT_URL`, `HELEKET_MERCHANT_ID`, `HELEKET_API_KEY`).
	- Suggestion: Validar com DevOps se já existe cofre de segredos (AWS Secrets Manager) e mapear variáveis necessárias para ambientes `dev`, `staging` e `prod`.
- [ ] **Criar cliente da API Heleket** — Implementar módulo cliente dedicado (ex: `app/services/heleket_client.py`) gerenciando headers de autenticação, chaves de idempotência, retry/backoff e superfícies de erro estruturadas. Incluir testes unitários com mocks de respostas. _Responsável: Backend_
	- Suggestion: Definir interface baseada nas rotas de payouts e contemplar abstração para futuros endpoints (ex: cancelamento, consulta) para evitar refatorações.
- [ ] **Persistir requisições de pagamento** — Adicionar modelo/coleção `Payout` para registrar payloads de requisição, IDs Heleket, status, valor, moeda, IDs de cliente/info associados e metadados de auditoria. Fornecer helpers de repositório para consultas por status/data. _Responsável: Backend_
	- Suggestion: Reaproveitar padrões de `app/models/click.py` para timestamps e índices; planejar índices em `status` + `createdAt` para relatórios.

### Tarefas de Suporte - Sprint 1
- [ ] **Playbook de deployment** — Atualizar scripts `deploy/` e `docker-compose.yml` com novas variáveis de env, health checks para webhook de pagamento e instruções para rotação de credenciais Heleket. _Responsável: DevOps_

**Resumo da Sprint 1:** _(preencher quando concluída)_

**Próximo foco após Sprint 1:** _Sprint 2_

---

## Sprint 2: Orquestração de Pagamentos & Workflow Administrativo

### Integração de Pagamentos Heleket - Fase 2
- [ ] **Implementar serviço de orquestração de pagamentos** — Introduzir camada de serviço que valida entradas (verificações de saldo, prevenção de duplicatas), cria pagamento Heleket via cliente, persiste registros e enfileira jobs de acompanhamento para polling de status. _Responsável: Backend_
- [ ] **Expor workflow administrativo** — Adicionar formulário/ação voltado para admin (controller + template) para iniciar pagamentos, mostrando informações bancárias do cliente pré-preenchidas, sugestões de valor e prompts de confirmação. Atualizar ações rápidas do dashboard com CTA. _Responsável: Full-stack_
- [ ] **Tratar callbacks/webhooks Heleket** — Registrar endpoint (ex: `/payouts/webhook`) que verifica assinaturas, atualiza estado do registro de pagamento e registra eventos de auditoria. Documentar schema de payload esperado conforme docs Heleket. _Responsável: Backend_

### Melhorias de UX do Dashboard - Fase 1
- [ ] **Unificar sistema de layout** — Refatorar `dashboard.html` + `dashboard/admin.html` para usar container, espaçamento e componentes de card consistentes definidos em `dashboard.css`; remover estilos inline e garantir ordem de empilhamento mobile. _Responsável: Frontend_
- [ ] **Implementar breakpoints de grid responsivo** — Auditar classes Bootstrap para prevenir aperto de quatro cards em tablets; introduzir tipografia baseada em CSS clamp e utilitários min-height para cards. _Responsável: Frontend_
- [ ] **Adicionar estados de carregamento/vazio** — Fornecer skeleton loaders e feedback `aria-live` para seções assíncronas (tabelas, gráficos) para que admins vejam progresso ao invés de áreas em branco. _Responsável: Frontend_

**Resumo da Sprint 2:** _(preencher quando concluída)_

**Próximo foco após Sprint 2:** _Sprint 3_

---

## Sprint 3: Monitoramento, Analytics & Melhorias de UX

### Integração de Pagamentos Heleket - Fase 3
- [ ] **Adicionar reconciliação & monitoramento** — Construir tarefa periódica ou ação manual para buscar status de pagamentos em andamento, destacar falhas e notificar admins (email/slack/log). _Responsável: Backend_
- [ ] **Integrar analytics** — Exibir KPIs de pagamento (totais pendentes/pagos/falhados) em cards ou gráficos do dashboard administrativo. _Responsável: Frontend_
- [ ] **Testes & QA** — Cobrir cliente API, workflows de serviço, tratamento de webhook e fluxos de UI com testes automatizados; preparar checklist de staging com credenciais sandbox Heleket. _Responsável: QA_

### Melhorias de UX do Dashboard - Fase 2
- [ ] **Reconciliar documentação vs. realidade** — Alinhar `docs/DASHBOARD_README.md` com implementação atual (gráficos faltantes) ou reativar visualizações Chart.js referenciadas no doc. _Responsável: Produto + Frontend_
- [ ] **Destacar métricas de receita & pagamento** — Reservar slot do card de estatística superior esquerdo para pagamentos quando integração existir; incluir badges de tendência e CTA para ver histórico de pagamentos. _Responsável: Frontend_
- [ ] **Melhorar usabilidade de tabelas** — Adicionar cabeçalhos ordenáveis, controles de tabela fixos e cards mobile compactos para `infos_detailed`, `recent_login_logs` e `recent_clicks`. _Responsável: Frontend_

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

