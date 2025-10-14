# TODO

> **Workflow Reminder:** Marque automaticamente os checkboxes concluídos, registre um resumo da sprint ao final de cada ciclo e destaque qual sprint vem a seguir. Ao ajustar qualquer item, adicione uma linha `Suggestion:` quando houver oportunidades ou riscos relacionados.

---

## Tarefas Pendentes

### Sprint 3 - Melhorias de UX do Dashboard
- [ ] **Reconciliar documentação vs. realidade** — Alinhar `docs/DASHBOARD_README.md` com implementação atual (gráficos faltantes) ou reativar visualizações Chart.js referenciadas no doc. _Responsável: Produto + Frontend_
- [ ] **Destacar métricas de receita & pagamento** — Reservar slot do card de estatística superior esquerdo para pagamentos quando integração existir; incluir badges de tendência e CTA para ver histórico de pagamentos. _Responsável: Frontend_
- [ ] **Atualizações de documentação** — Adicionar detalhes de integração Heleket a `docs/` (fluxos de API, diagramas de sequência, setup de env) e referenciar novos padrões de arquitetura CRUD. _Responsável: Technical Writer_

### Sprint 4 - Refatoração CRUD & Redução de Código
- [ ] **Migrar chamadas AuditService restantes** — Substituir chamadas diretas `AuditService.log_*` em fluxos de payout pelo helper `audit_helper` para consistência. _Responsável: Backend_
- [ ] **Atualizar documentação técnica** — Documentar novos padrões CRUD em `docs/` (mixin, schemas Pydantic, repository pattern) e atualizar guias de arquitetura. _Responsável: Technical Writer_

**Status:** Projeto concluído com sucesso. Todas as funcionalidades principais implementadas e testadas. Tarefas restantes são melhorias opcionais de documentação e polimento.
