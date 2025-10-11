# Documentação do Client Manager

Documentação técnica completa do sistema de gerenciamento de clientes.

## 📚 Índice de Documentação

### 🏗️ Arquitetura e Design

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitetura completa do sistema
  - Padrão MVC com Services
  - Estrutura de diretórios
  - Fluxo de dados
  - Segurança e autenticação
  - Testes e qualidade de código
  - Exemplos práticos de extensão

### 📄 Sistema de Templates

- **[TEMPLATE_FIELDS_SYSTEM.md](./TEMPLATE_FIELDS_SYSTEM.md)** - Sistema de templates
  - Como funcionam os templates
  - Slugs e rotas públicas
  - Páginas HTML personalizadas
  - Roadmap de funcionalidades futuras

### 🔌 API e Documentação

- **[SWAGGER_IMPLEMENTATION.md](./SWAGGER_IMPLEMENTATION.md)** - Implementação Swagger/OpenAPI
  - Plano de implementação da API REST
  - Lista completa de 45+ endpoints
  - Schemas e modelos de dados
  - Tags organizacionais
  - Critérios de aceitação

## 🚀 Início Rápido

Para começar a desenvolver, consulte o [README.md](../README.md) principal na raiz do projeto.

### Links Importantes

- [README Principal](../README.md) - Instalação e configuração
- [Arquitetura](./ARCHITECTURE.md) - Entenda o sistema
- [API Docs](./SWAGGER_IMPLEMENTATION.md) - Integração via API

## 📊 Diagramas e Fluxos

### Fluxo de Autenticação

```
Cliente/Admin → Login Form → Auth Service → Validação
                                    ↓
                            Flask-Login Session
                                    ↓
                            Dashboard (Role-based)
```

### Estrutura MVC

```
View (Templates) ← Controller (Routes) ← Service (Business Logic) ← Model (Database)
       ↓                   ↓                      ↓                       ↓
   HTML/Jinja2        Flask Routes         Python Classes          MongoDB
```

## 🔐 Segurança

O sistema implementa múltiplas camadas de segurança:

- **Autenticação**: Flask-Login + Bcrypt
- **Autorização**: Decoradores `@login_required`, `@admin_required`, `@super_admin_required`
- **CSRF**: Flask-WTF com tokens CSRF
- **Rate Limiting**: Flask-Limiter
- **Validação**: Pydantic schemas
- **Auditoria**: Sistema completo de logs

## 🧪 Testes

O projeto possui 36 testes automatizados cobrindo:

- **Autenticação** (9 testes)
- **Serviços de Auditoria** (7 testes)
- **Serviços de Auth** (9 testes)
- **Serviços de Cliente** (11 testes)

Para executar os testes:

```bash
pytest tests/ -v
```

## 📝 Contribuindo

Ao adicionar novas funcionalidades:

1. Consulte [ARCHITECTURE.md](./ARCHITECTURE.md) para seguir os padrões
2. Adicione testes apropriados
3. Documente endpoints no [SWAGGER_IMPLEMENTATION.md](./SWAGGER_IMPLEMENTATION.md)
4. Atualize esta documentação se necessário

## 🔗 Links Úteis

- [Issue #6 - Swagger/OpenAPI](https://github.com/rootkitoriginal/client_manager/issues/6)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📋 Status do Projeto

- ✅ Sistema de autenticação completo
- ✅ CRUD de clientes, admins, planos, domínios, templates
- ✅ Sistema de auditoria
- ✅ 36 testes automatizados
- ✅ Segurança (CVE-2024-5629 resolvido)
- 🚧 Documentação API Swagger/OpenAPI (em desenvolvimento)

---

**Última atualização:** 11 de outubro de 2025
