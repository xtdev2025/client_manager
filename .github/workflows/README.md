# 🔄 GitHub Actions Workflows

Este diretório contém os workflows consolidados do projeto. De **12 workflows originais**, mantivemos apenas **6 essenciais** para otimização e clareza.

## 📋 Workflows Ativos

### 1. **CI** (`ci.yml`)

**Trigger:** Push e Pull Request em `main` e `develop`

Executa validações de qualidade de código:

- ✅ **Lint**: Verifica código com `flake8`
- ✅ **Formatação**: Valida formatação com `black` e `isort`
- ✅ **Type Checking**: Análise de tipos com `mypy`
- ✅ **Validação**: Verifica `requirements.txt` e dependências
- ✅ **Security Check**: Scan com `safety` para vulnerabilidades conhecidas

**Jobs:**

- `lint` - Análise de código
- `validate` - Validação de estrutura

---

### 2. **Tests** (`test.yml`)

**Trigger:** Push e Pull Request em `main` e `develop`

Executa suite completa de testes:

- 🧪 **Unit Tests**: Testes unitários com cobertura
- 🔗 **Integration Tests**: Testes de integração
- 🐍 **Matrix Testing**: Python 3.9, 3.10, 3.11
- 🗄️ **MongoDB Service**: Container MongoDB para testes
- 📊 **Coverage**: Upload para Codecov

**Requisitos:**

- MongoDB 5.0
- Arquivo `.env` com configurações de teste

---

### 3. **Deploy** (`deploy.yml`)

**Trigger:** Push em `main`, tags `v*`, e manual dispatch

Gerencia deployment da aplicação:

- 🐳 **Build**: Constrói imagem Docker
- 📦 **Registry**: Push para GitHub Container Registry
- 🌐 **Staging**: Deploy automático em pushes para `main`
- 🚀 **Production**: Deploy em tags ou manual

**Ambientes:**

- `staging` - Ambiente de homologação
- `production` - Ambiente de produção

---

### 4. **Security** (`security.yml`)

**Trigger:** Push, Pull Request, e schedule semanal (segunda 2h)

Análise de segurança da aplicação:

- 🔒 **Bandit**: Scan de vulnerabilidades em código Python
- 🛡️ **Safety**: Verifica dependências com vulnerabilidades conhecidas
- 📄 **Reports**: Gera relatórios JSON
- 📤 **Artifacts**: Upload de relatórios de segurança

**Schedule:** Toda segunda-feira às 2h (UTC)

---

### 5. **CodeQL** (`codeql.yml`)

**Trigger:** Push, Pull Request, e schedule semanal (segunda 6h)

Análise avançada de segurança do GitHub:

- 🔍 **Deep Analysis**: Análise semântica do código
- 🐍 **Python Analysis**: Detecta padrões inseguros em Python
- 📜 **JavaScript Analysis**: Análise de arquivos JS/TS
- 🎯 **Security Queries**: `security-extended` e `security-and-quality`
- 📊 **Security Events**: Integração com GitHub Security tab

**Schedule:** Toda segunda-feira às 6h (UTC)

---

### 6. **Dependency Review** (`dependency-review.yml`)

**Trigger:** Pull Requests para `main`

Análise de dependências em PRs:

- 📦 **Review**: Verifica mudanças em dependências
- ⚠️ **Severity**: Falha em vulnerabilidades moderadas ou superiores
- ✅ **License Check**: Permite MIT, Apache-2.0, BSD, ISC
- ❌ **License Block**: Bloqueia GPL-2.0, GPL-3.0

---

## 🗑️ Workflows Removidos

Os seguintes workflows foram removidos por redundância ou falta de uso:

| Workflow | Motivo da Remoção |
|----------|-------------------|
| `ci-simple.yml` | Redundante com `ci.yml` - apenas echo statements |
| `gemini-dispatch.yml` | Não estava em uso ativo |
| `gemini-review.yml` | Não estava em uso ativo |
| `gemini-triage.yml` | Não estava em uso ativo |
| `gemini-invoke.yml` | Não estava em uso ativo |
| `gemini-scheduled-triage.yml` | Não estava em uso ativo |

> **Nota:** Se precisar reativar workflows Gemini AI no futuro, consulte o histórico do Git.

---

## 🧪 Testando Workflows Localmente

Use o [Act](https://github.com/nektos/act) para testar workflows localmente:

### Teste Rápido (workflows principais)

```bash
./test-workflows.sh
```

### Teste Completo (todos os workflows com dry-run)

```bash
./test-all-workflows.sh
```

### Teste Individual

```bash
act push -W .github/workflows/ci.yml --secret-file .secrets --env-file .env.act
```

---

## 📊 Fluxo de CI/CD

```
┌─────────────┐
│   Push/PR   │
└──────┬──────┘
       │
       ├─────► CI (lint, format, type check)
       │
       ├─────► Tests (unit + integration)
       │
       ├─────► Security (bandit + safety)
       │
       └─────► CodeQL (security analysis)
              
┌─────────────┐
│  PR Review  │
└──────┬──────┘
       │
       └─────► Dependency Review

┌─────────────┐
│ Push main   │
└──────┬──────┘
       │
       ├─────► Build Docker Image
       │
       └─────► Deploy to Staging

┌─────────────┐
│  Tag v*.*   │
└──────┬──────┘
       │
       └─────► Deploy to Production
```

---

## ⚙️ Configuração Necessária

### Secrets (GitHub Repository Settings)

- `GITHUB_TOKEN` - Gerado automaticamente
- `CODECOV_TOKEN` - Para upload de cobertura (opcional)

### Variables (GitHub Repository Settings)

- Nenhuma variável customizada necessária atualmente

### Branch Protection

Recomenda-se configurar em `main`:

- ✅ Require status checks: `CI / lint`, `Tests / test`, `Security / security`
- ✅ Require pull request reviews
- ✅ Require branches to be up to date

---

## 📈 Métricas

- **Redução:** 12 → 6 workflows (50% menos arquivos)
- **Tempo de CI:** ~5-10 minutos (dependendo dos testes)
- **Cobertura:** Análise completa com security + tests
- **Matrix Testing:** 3 versões do Python

---

## 🔗 Links Úteis

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Act - Local Testing](https://github.com/nektos/act)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Codecov](https://codecov.io/)

---

**Última atualização:** 11 de outubro de 2025  
**Versão:** 2.0 (Consolidada)
