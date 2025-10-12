#!/bin/bash

echo "🧪 Testando todos os workflows com Act (dry-run)..."
echo "📁 Total de workflows: 6 (CI, Test, Deploy, Security, CodeQL, Dependency Review)"
echo ""

# Função para testar workflow
test_workflow() {
    local workflow=$1
    local job=$2
    local description=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Testando: $workflow"
    echo "📝 Descrição: $description"
    
    if [ -n "$job" ]; then
        act push -W .github/workflows/$workflow --secret-file .secrets --env-file .env.act --job $job --dryrun
    else
        act push -W .github/workflows/$workflow --secret-file .secrets --env-file .env.act --dryrun
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ $workflow passou no teste"
    else
        echo "❌ $workflow falhou no teste"
    fi
    echo ""
}

# Testar workflows essenciais
test_workflow "ci.yml" "validate" "Lint, formatação e validação de código"
test_workflow "test.yml" "" "Testes unitários e integração com MongoDB"
test_workflow "deploy.yml" "" "Deploy para staging e production"
test_workflow "security.yml" "" "Scan de segurança (Bandit & Safety)"
test_workflow "codeql.yml" "" "Análise de segurança do código"
test_workflow "dependency-review.yml" "" "Análise de dependências em PRs"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Resumo dos testes concluído!"
echo ""
echo "📊 Workflows consolidados (de 12 para 6):"
echo "  ✅ ci.yml - CI principal"
echo "  ✅ test.yml - Testes automatizados"
echo "  ✅ deploy.yml - Deployment"
echo "  ✅ security.yml - Security scan"
echo "  ✅ codeql.yml - Code analysis"
echo "  ✅ dependency-review.yml - Dependency check"
echo ""
echo "🗑️  Removidos:"
echo "  ❌ ci-simple.yml (redundante)"
echo "  ❌ gemini-*.yml (5 workflows não utilizados)"