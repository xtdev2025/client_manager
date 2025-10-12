#!/bin/bash

echo "🧪 Testando todos os workflows com Act..."

# Função para testar workflow
test_workflow() {
    local workflow=$1
    local job=$2
    echo "📋 Testando $workflow..."
    
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

# Testar workflows individuais
test_workflow "ci.yml" "validate"
test_workflow "security.yml"
test_workflow "test.yml"
test_workflow "deploy.yml"
test_workflow "codeql.yml"
test_workflow "dependency-review.yml"

echo "🎯 Resumo dos testes concluído!"