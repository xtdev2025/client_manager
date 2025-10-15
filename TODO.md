# TODO

> **Workflow Reminder:** Marque automaticamente os checkboxes concluídos, registre um resumo da sprint ao final de cada ciclo e destaque qual sprint vem a seguir. Ao ajustar qualquer item, adicione uma linha `Suggestion:` quando houver oportunidades ou riscos relacionados.

---

## Tarefas Pendentes

### Sprint 3 - Melhorias de UX do Dashboard
- [x] **Reconciliar documentação vs. realidade** — Alinhar `docs/DASHBOARD_README.md` com implementação atual (gráficos faltantes) ou reativar visualizações Chart.js referenciadas no doc. _Responsável: Produto + Frontend_
	- Suggestion: Capturar screenshots atualizados e anexar no próximo release note para reforçar a narrativa visual.
- [x] **Destacar métricas de receita & pagamento** — Reservar slot do card de estatística superior esquerdo para pagamentos quando integração existir; incluir badges de tendência e CTA para ver histórico de pagamentos. _Responsável: Frontend_
	- Suggestion: Avaliar threshold real de sucesso/alerta usando dados de produção para calibrar cores e ícones da badge.
- [x] **Atualizações de documentação** — Adicionar detalhes de integração Heleket a `docs/` (fluxos de API, diagramas de sequência, setup de env) e referenciar novos padrões de arquitetura CRUD. _Responsável: Technical Writer_
	- Suggestion: Revisitar diagramas quando novos fluxos Heleket (ex.: estorno) forem incorporados.

**Sprint 3 Summary (2025-10-14):** Documentação alinhada ao dashboard Enterprise e KPIs de payouts em destaque; sem blockers. **Next:** focar na Sprint 4 - Refatoração CRUD & Redução de Código.

### Sprint 4 - Refatoração CRUD & Redução de Código
- [x] **Migrar chamadas AuditService restantes** — Substituir chamadas diretas `AuditService.log_*` em fluxos de payout pelo helper `audit_helper` para consistência. _Responsável: Backend_
	- Suggestion: Monitorar os dashboards de auditoria pós-deploy para garantir que os metadados de ator/IP estejam chegando como esperado.
- [ ] **Atualizar documentação técnica** — Documentar novos padrões CRUD em `docs/` (mixin, schemas Pydantic, repository pattern) e atualizar guias de arquitetura. _Responsável: Technical Writer_
- [ ] **Analisar o sistema e padronizar schemas** — Levantar entidades existentes, criar schemas (Pydantic ou equivalentes) alinhados aos models e documentar convenções de uso. _Responsável: Backend + Technical Writer_
	- Suggestion: Validar impacto em integrações externas antes de publicar novas convenções para evitar retrabalho em consumidores de API.

**Status:** Projeto concluído com sucesso. Todas as funcionalidades principais implementadas e testadas. Tarefas restantes são melhorias opcionais de documentação e polimento.
