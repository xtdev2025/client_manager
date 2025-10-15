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
- [x] **Migrar AuditService para audit_helper** — Centralizar logging de auditoria com metadados de ator/IP, remover dependências do AuditService legado. _Responsável: Backend_
- [x] **Atualizar documentação técnica** — Revisar e atualizar docs de arquitetura, API e padrões de código para refletir mudanças recentes. _Responsável: Technical Writer_
- [x] **Analisar o sistema e padronizar schemas** — Levantar entidades existentes, criar schemas (Pydantic ou equivalentes) alinhados aos models e documentar convenções de uso. _Responsável: Backend + Technical Writer_
	- Suggestion: Validar impacto em integrações externas antes de publicar novas convenções para evitar retrabalho em consumidores de API.

**Sprint 4 Summary (2025-01-15):** Migração completa do AuditService para audit_helper centralizado, padronização de schemas Pydantic com métodos audit_payload para logging seguro, e atualização da documentação técnica refletindo novos padrões CRUD. Todos os testes passando (10/10). **Next:** Monitorar produção para validar metadados de auditoria e planejar Sprint 5 focando em melhorias de performance.

**Status:** Projeto concluído com sucesso. Todas as funcionalidades principais implementadas e testadas. Tarefas restantes são melhorias opcionais de documentação e polimento.
