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
	- Resultado: Padrões de `app/models/click.py` reutilizados para timestamps e índices.
	- Suggestion: Executar `ClientCryptoPayout.create_indexes()` durante inicialização da aplicação para garantir performance.

### Tarefas de Suporte - Sprint 1
- [ ] **Playbook de deployment** — Atualizar scripts `deploy/` e `docker-compose.yml` com novas variáveis de env, health checks para webhook de pagamento e instruções para rotação de credenciais Heleket. _Responsável: DevOps_

**Resumo da Sprint 1:** 
- ✅ **Concluída (14/10/2025)** — Fundação da integração Heleket estabelecida com sucesso
- 🎯 **Entregas:**
  - Cliente API Heleket implementado com retry/backoff, idempotência e tratamento robusto de erros
  - Modelo de persistência client_crypto_payouts com helpers de consulta e índices otimizados
  - Documentação técnica completa (HELEKET_CLIENT.md) e exemplos de integração
  - Cobertura de testes: 34 casos de teste (16 para cliente API + 18 para modelo)
  - Configuração de credenciais via variáveis de ambiente já estabelecida
- 📋 **Pendências:** 
  - Implementação de verificação de assinatura de webhook (aguardando docs Heleket)
  - Validação com DevOps sobre cofre de segredos AWS para ambientes staging/prod
  - Alinhamento com Produto/Compliance sobre requisitos de carteira cripto

**Próximo foco após Sprint 1:** _Sprint 2 - Orquestração de Pagamentos & Workflow Administrativo_

---

## Sprint 2: Orquestração de Pagamentos & Workflow Administrativo

### Integração de Pagamentos Heleket - Fase 2
- [ ] **Implementar serviço de orquestração de pagamentos** — Introduzir camada de serviço que valida entradas (verificações de saldo, prevenção de duplicatas), cria pagamento Heleket via cliente, persiste registros e enfileira jobs de acompanhamento para polling de status. _Responsável: Backend_
- [ ] **Expor workflow administrativo** — Adicionar formulário/ação voltado para admin (controller + template) para iniciar pagamentos, mostrando dados de carteira do cliente pré-preenchidos, sugestões de valor e prompts de confirmação. Atualizar ações rápidas do dashboard com CTA. _Responsável: Full-stack_
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

