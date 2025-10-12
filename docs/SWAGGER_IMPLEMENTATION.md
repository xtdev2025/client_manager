# Implementação da Documentação Swagger/OpenAPI

Este documento descreve o plano de implementação para a issue #6.

## 📋 Status Atual

### ✅ Preparação Concluída

- [x] Branch criada: `feature/swagger-openapi-docs`
- [x] Estrutura de diretórios criada: `app/api/`
- [x] Dependências adicionadas ao `requirements.txt`
- [x] Tags organizacionais definidas
- [x] Lista de 45+ endpoints mapeados

### 🔧 Dependências Adicionadas

```
flask-swagger-ui==4.11.1
apispec==6.3.0
apispec-webframeworks==0.5.2
```

## 📊 Endpoints a Documentar (45+)

### 🏠 Main Routes (2 endpoints)

- `GET /` - Página inicial
- `GET /dashboard` - Dashboard principal

### 🔐 Auth Routes (4 endpoints)

- `GET/POST /auth/login` - Login de usuários
- `GET /auth/logout` - Logout
- `GET/POST /auth/register` - Registro de clientes
- `GET/POST /auth/register_admin` - Registro de admins

### 👥 Client Routes (8 endpoints)

- `GET /clients/` - Listar clientes
- `GET/POST /clients/create` - Criar cliente
- `GET/POST /clients/edit/<client_id>` - Editar cliente
- `POST /clients/delete/<client_id>` - Deletar cliente
- `GET /clients/view/<client_id>` - Visualizar cliente
- `GET /clients/<client_id>/domains` - Domínios do cliente
- `POST /clients/<client_id>/domains/add` - Adicionar domínio
- `POST /clients/<client_id>/domains/remove/<client_domain_id>` - Remover domínio

### 🌐 Client Portal Routes (4 endpoints)

- `GET /client/my-domains` - Meus domínios
- `GET /client/my-click-stats` - Minhas estatísticas
- `GET /client/my-infos` - Minhas informações
- `GET/POST /client/my-change-password` - Trocar senha

### 👔 Admin Routes (7 endpoints)

- `GET /admins/` - Listar admins
- `GET/POST /admins/create` - Criar admin
- `GET/POST /admins/edit/<admin_id>` - Editar admin
- `POST /admins/delete/<admin_id>` - Deletar admin
- `GET/POST /admins/profile` - Perfil do admin
- `GET /admins/audit-logs` - Ver logs de auditoria
- `POST /admins/clear-audit-logs` - Limpar logs

### 💼 Plan Routes (5 endpoints)

- `GET /plans/` - Listar planos
- `GET/POST /plans/create` - Criar plano
- `GET/POST /plans/edit/<plan_id>` - Editar plano
- `POST /plans/delete/<plan_id>` - Deletar plano
- `GET /plans/view/<plan_id>` - Visualizar plano

### 🌍 Domain Routes (5 endpoints)

- `GET /domains/` - Listar domínios
- `GET/POST /domains/create` - Criar domínio
- `GET/POST /domains/edit/<domain_id>` - Editar domínio
- `POST /domains/delete/<domain_id>` - Deletar domínio
- `GET /domains/view/<domain_id>` - Visualizar domínio

### 📄 Template Routes (5 endpoints)

- `GET /templates/` - Listar templates
- `GET/POST /templates/create` - Criar template
- `GET/POST /templates/edit/<template_id>` - Editar template
- `POST /templates/delete/<template_id>` - Deletar template
- `GET /templates/view/<template_id>` - Visualizar template

### 🏦 Info Routes (6 endpoints)

- `GET /infos/` - Listar informações bancárias
- `GET /infos/client/<client_id>` - Infos por cliente
- `GET/POST /infos/create/<client_id>` - Criar info
- `GET/POST /infos/edit/<info_id>` - Editar info
- `GET /infos/view/<info_id>` - Visualizar info
- `POST /infos/delete/<info_id>` - Deletar info

## 🎯 Tarefas Pendentes

### 1. Configuração Base

- [ ] Implementar função `init_swagger()` em `app/api/swagger.py`
- [ ] Configurar Swagger UI em `/api/docs`
- [ ] Configurar APISpec com OpenAPI 3.0
- [ ] Integrar Swagger com Flask app factory

### 2. Schemas Pydantic

- [ ] Schema para `User` (Admin/Client)
- [ ] Schema para `Client` com relacionamentos
- [ ] Schema para `Admin`
- [ ] Schema para `Plan`
- [ ] Schema para `Domain`
- [ ] Schema para `Template`
- [ ] Schema para `Info` (informações bancárias)
- [ ] Schema para `AuditLog`
- [ ] Schemas de erro (400, 401, 403, 404, 500)

### 3. Documentação de Endpoints

- [ ] Documentar Main Routes (2)
- [ ] Documentar Auth Routes (4)
- [ ] Documentar Client Routes (8)
- [ ] Documentar Client Portal Routes (4)
- [ ] Documentar Admin Routes (7)
- [ ] Documentar Plan Routes (5)
- [ ] Documentar Domain Routes (5)
- [ ] Documentar Template Routes (5)
- [ ] Documentar Info Routes (6)

### 4. Autenticação e Segurança

- [ ] Configurar autenticação Bearer Token no Swagger UI
- [ ] Documentar fluxo de autenticação
- [ ] Adicionar exemplos de headers de autenticação
- [ ] Documentar rate limiting

### 5. Exemplos e Validação

- [ ] Adicionar exemplos de request para cada endpoint
- [ ] Adicionar exemplos de response (success)
- [ ] Adicionar exemplos de response (error)
- [ ] Testar todos os endpoints via Swagger UI

### 6. Documentação Complementar

- [ ] Atualizar README.md com link para `/api/docs`
- [ ] Adicionar seção sobre como usar a API
- [ ] Documentar autenticação via API
- [ ] Adicionar exemplos de integração

## 🎨 Organização por Tags

```python
SWAGGER_TAGS = [
    'Auth',           # Autenticação e autorização
    'Main',           # Rotas principais
    'Clients',        # Gerenciamento de clientes (admin)
    'Client Portal',  # Área do cliente (my-*)
    'Admins',         # Gerenciamento de admins
    'Plans',          # Gerenciamento de planos
    'Domains',        # Gerenciamento de domínios
    'Templates',      # Gerenciamento de templates
    'Infos',          # Informações bancárias
    'Audit'           # Logs de auditoria
]
```

## 🚀 Como Continuar

1. **Instalar dependências:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Implementar configuração base:**
   - Editar `app/api/swagger.py`
   - Implementar `init_swagger(app)`
   - Registrar blueprint no app factory

3. **Criar schemas:**
   - Expandir `app/schemas/` com modelos OpenAPI
   - Usar Pydantic para validação

4. **Documentar endpoints:**
   - Adicionar decorators de documentação
   - Usar APISpec para gerar spec

5. **Testar:**
   - Acessar `/api/docs`
   - Validar todos os endpoints
   - Testar autenticação

## 📚 Referências

- [APISpec Documentation](https://apispec.readthedocs.io/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

## ✅ Critérios de Aceitação (Issue #6)

- [ ] Swagger UI acessível em `/api/docs`
- [ ] Todos os 45+ endpoints documentados
- [ ] Esquemas Pydantic integrados
- [ ] Exemplos de request/response
- [ ] Autenticação funcional na UI
- [ ] Documentação de erros (400, 401, 403, 404, 500)
- [ ] Documentação de parâmetros
- [ ] README atualizado
- [ ] Tags organizadas
- [ ] Modelos de dados documentados
