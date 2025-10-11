# 📊 Relatório Completo de Endpoints - Swagger/OpenAPI

**Data de Geração:** 2025-10-11  
**Versão da API:** 1.0.0  
**Especificação:** OpenAPI 3.0.3

## 📍 URLs de Acesso

- **Swagger UI (Interativo):** http://localhost:5000/api/docs
- **OpenAPI JSON Spec:** http://localhost:5000/api/swagger.json
- **Documentação Markdown:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Referência Rápida:** [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| **Total de Endpoints** | 63 |
| **Total de Categorias** | 10 |
| **Schemas Pydantic** | 22 |
| **Servidor** | http://localhost:5000 |

---

## 📁 Main (2 endpoints)

Rotas principais da aplicação.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/` | Home page | Não |
| GET | `/dashboard` | User dashboard | Sim 🔒 |

---

## 📁 Auth (7 endpoints)

Autenticação e autorização de usuários.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/auth/login` | Display login page | Não |
| POST | `/auth/login` | Process login | Não |
| GET | `/auth/logout` | Logout user | Sim 🔒 |
| GET | `/auth/register` | Display registration page | Não |
| POST | `/auth/register` | Register new client | Não |
| GET | `/auth/register_admin` | Display admin registration page | Sim 🔒 |
| POST | `/auth/register_admin` | Register new admin | Sim 🔒 |

---

## 📁 Clients (10 endpoints)

Gerenciamento de clientes (área administrativa).

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/clients/` | List all clients | Sim 🔒 |
| GET | `/clients/create` | Display client creation form | Sim 🔒 |
| POST | `/clients/create` | Create new client | Sim 🔒 |
| POST | `/clients/delete/{client_id}` | Delete client | Sim 🔒 |
| GET | `/clients/edit/{client_id}` | Display client edit form | Sim 🔒 |
| POST | `/clients/edit/{client_id}` | Update client | Sim 🔒 |
| GET | `/clients/view/{client_id}` | View client details | Sim 🔒 |
| GET | `/clients/{client_id}/domains` | List client domains | Sim 🔒 |
| POST | `/clients/{client_id}/domains/add` | Add domain to client | Sim 🔒 |
| POST | `/clients/{client_id}/domains/remove/{client_domain_id}` | Remove domain from client | Sim 🔒 |

---

## 📁 Client Portal (5 endpoints)

Portal de auto-serviço para clientes (rotas my-*).

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/client/my-change-password` | Display password change form | Sim 🔒 |
| POST | `/client/my-change-password` | Change my password | Sim 🔒 |
| GET | `/client/my-click-stats` | View my click statistics | Sim 🔒 |
| GET | `/client/my-domains` | View my domains | Sim 🔒 |
| GET | `/client/my-infos` | View my banking information | Sim 🔒 |

---

## 📁 Admins (8 endpoints)

Gerenciamento de administradores.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/admins/` | List all admins | Sim 🔒 |
| GET | `/admins/create` | Display admin creation form | Sim 🔒 |
| POST | `/admins/create` | Create new admin | Sim 🔒 |
| POST | `/admins/delete/{admin_id}` | Delete admin | Sim 🔒 |
| GET | `/admins/edit/{admin_id}` | Display admin edit form | Sim 🔒 |
| POST | `/admins/edit/{admin_id}` | Update admin | Sim 🔒 |
| GET | `/admins/profile` | View admin profile | Sim 🔒 |
| POST | `/admins/profile` | Update admin profile | Sim 🔒 |

---

## 📁 Plans (7 endpoints)

Gerenciamento de planos de assinatura.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/plans/` | List all plans | Sim 🔒 |
| GET | `/plans/create` | Display plan creation form | Sim 🔒 |
| POST | `/plans/create` | Create new plan | Sim 🔒 |
| POST | `/plans/delete/{plan_id}` | Delete plan | Sim 🔒 |
| GET | `/plans/edit/{plan_id}` | Display plan edit form | Sim 🔒 |
| POST | `/plans/edit/{plan_id}` | Update plan | Sim 🔒 |
| GET | `/plans/view/{plan_id}` | View plan details | Sim 🔒 |

---

## 📁 Domains (7 endpoints)

Gerenciamento de domínios.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/domains/` | List all domains | Sim 🔒 |
| GET | `/domains/create` | Display domain creation form | Sim 🔒 |
| POST | `/domains/create` | Create new domain | Sim 🔒 |
| POST | `/domains/delete/{domain_id}` | Delete domain | Sim 🔒 |
| GET | `/domains/edit/{domain_id}` | Display domain edit form | Sim 🔒 |
| POST | `/domains/edit/{domain_id}` | Update domain | Sim 🔒 |
| GET | `/domains/view/{domain_id}` | View domain details | Sim 🔒 |

---

## 📁 Templates (7 endpoints)

Gerenciamento de templates.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/templates/` | List all templates | Sim 🔒 |
| GET | `/templates/create` | Display template creation form | Sim 🔒 |
| POST | `/templates/create` | Create new template | Sim 🔒 |
| POST | `/templates/delete/{template_id}` | Delete template | Sim 🔒 |
| GET | `/templates/edit/{template_id}` | Display template edit form | Sim 🔒 |
| POST | `/templates/edit/{template_id}` | Update template | Sim 🔒 |
| GET | `/templates/view/{template_id}` | View template details | Sim 🔒 |

---

## 📁 Infos (8 endpoints)

Gerenciamento de informações bancárias.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/infos/` | List all banking information | Sim 🔒 |
| GET | `/infos/client/{client_id}` | Get banking info by client | Sim 🔒 |
| GET | `/infos/create/{client_id}` | Display info creation form | Sim 🔒 |
| POST | `/infos/create/{client_id}` | Create new banking info | Sim 🔒 |
| POST | `/infos/delete/{info_id}` | Delete banking info | Sim 🔒 |
| GET | `/infos/edit/{info_id}` | Display info edit form | Sim 🔒 |
| POST | `/infos/edit/{info_id}` | Update banking info | Sim 🔒 |
| GET | `/infos/view/{info_id}` | View banking info details | Sim 🔒 |

---

## 📁 Audit (2 endpoints)

Logs de auditoria e monitoramento do sistema.

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/admins/audit-logs` | View audit logs | Sim 🔒 |
| POST | `/admins/clear-audit-logs` | Clear audit logs | Sim 🔒 |

---

## 📦 Schemas Pydantic (22 schemas)

Todos os schemas estão registrados no OpenAPI e disponíveis no Swagger UI:

1. **AdminListResponse** - Lista paginada de administradores
2. **AdminSchema** - Schema de administrador individual
3. **AuditLogListResponse** - Lista paginada de logs de auditoria
4. **AuditLogSchema** - Schema de log de auditoria individual
5. **ClientListResponse** - Lista paginada de clientes
6. **ClientSchema** - Schema de cliente individual
7. **DashboardStatsSchema** - Estatísticas do dashboard
8. **DomainListResponse** - Lista paginada de domínios
9. **DomainSchema** - Schema de domínio individual
10. **ErrorResponse** - Resposta de erro padrão
11. **InfoListResponse** - Lista paginada de informações bancárias
12. **InfoSchema** - Schema de informação bancária individual
13. **LoginRequest** - Requisição de login
14. **LoginResponse** - Resposta de login
15. **PaginationInfo** - Informações de paginação
16. **PlanListResponse** - Lista paginada de planos
17. **PlanSchema** - Schema de plano individual
18. **SuccessResponse** - Resposta de sucesso padrão
19. **TemplateListResponse** - Lista paginada de templates
20. **TemplateSchema** - Schema de template individual
21. **UserSchema** - Schema de usuário base
22. **ValidationError** - Erro de validação

---

## 🔐 Informações de Autenticação

- **Método:** Session-based (Flask-Login)
- **Rate Limiting:** Ativo (200 requisições/dia, 50/hora)
- **Níveis de Permissão:**
  - 🔓 **Público** - Sem autenticação necessária
  - 🔒 **Autenticado** - Requer login (client/admin/super_admin)
  - 🔐 **Admin** - Requer permissões de administrador
  - 🛡️ **Super Admin** - Requer permissões de super administrador

---

## ✅ Status de Validação

- ✅ Todos os 63 endpoints estão documentados no Swagger UI
- ✅ OpenAPI 3.0.3 specification completa
- ✅ 22 Pydantic schemas registrados
- ✅ Request/Response bodies documentados
- ✅ Códigos de status HTTP especificados
- ✅ Parâmetros de rota documentados
- ✅ Tags organizacionais aplicadas
- ✅ Funcionalidade "Try it out" disponível

---

## 📝 Notas Adicionais

- Todos os endpoints foram validados usando MCP Playwright
- A documentação é gerada automaticamente pelos Pydantic schemas
- O Swagger UI está totalmente funcional e interativo
- Suporte completo para OpenAPI 3.0.3

---

**Gerado por:** GitHub Copilot + MCP Playwright  
**Data:** 2025-10-11
