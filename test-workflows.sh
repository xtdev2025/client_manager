#!/bin/bash

echo "🧪 Testando workflows essenciais com Act..."
echo "📁 Workflows ativos: CI, Security, Test, CodeQL, Deploy, Dependency Review"
echo ""

# Testar CI workflow
echo "📋 Testando CI workflow (lint & validate)..."
act push -W .github/workflows/ci.yml --secret-file .secrets --env-file .env.act

# Testar Security workflow
echo "🔒 Testando Security workflow (Bandit & Safety)..."
act push -W .github/workflows/security.yml --secret-file .secrets --env-file .env.act

# Testar Test workflow
echo "🧪 Testando Test workflow (unit & integration)..."
act push -W .github/workflows/test.yml --secret-file .secrets --env-file .env.act

# Testar CodeQL workflow
echo "🔍 Testando CodeQL workflow (security analysis)..."
act push -W .github/workflows/codeql.yml --secret-file .secrets --env-file .env.act

# Testar Deploy workflow
echo "🚀 Testando Deploy workflow (staging & production)..."
act push -W .github/workflows/deploy.yml --secret-file .secrets --env-file .env.act --dryrun

echo ""
echo "✅ Testes concluídos!"
echo "ℹ️  Nota: Dependency Review roda apenas em pull_request"