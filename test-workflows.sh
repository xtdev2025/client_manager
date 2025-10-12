#!/bin/bash

echo "🧪 Testando workflows com Act..."

# Testar CI workflow
echo "📋 Testando CI workflow..."
act push -W .github/workflows/ci.yml --secret-file .secrets --env-file .env.act

# Testar Security workflow
echo "🔒 Testando Security workflow..."
act push -W .github/workflows/security.yml --secret-file .secrets --env-file .env.act

# Testar Test workflow
echo "🧪 Testando Test workflow..."
act push -W .github/workflows/test.yml --secret-file .secrets --env-file .env.act

# Testar CodeQL workflow
echo "🔍 Testando CodeQL workflow..."
act push -W .github/workflows/codeql.yml --secret-file .secrets --env-file .env.act

echo "✅ Testes concluídos!"