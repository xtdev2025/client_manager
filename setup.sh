#!/bin/bash

# Script de configuração para o Client Manager
# Este script configura o ambiente e inicializa o banco de dados

echo "=== Client Manager Setup ==="
echo "Configurando ambiente e dependências..."

# Verificar se o virtualenv já existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar o ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Verificar se o MongoDB está instalado e em execução
echo "Verificando MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "AVISO: MongoDB parece não estar instalado."
    echo "Por favor, instale o MongoDB antes de continuar:"
    echo "  Ubuntu: sudo apt install mongodb"
    echo "  macOS:  brew install mongodb-community"
    echo "  Windows: Baixe o instalador em https://www.mongodb.com/try/download/community"
else
    echo "MongoDB encontrado!"
    
    # Verificar se MongoDB está em execução
    if ! pgrep mongod > /dev/null; then
        echo "AVISO: MongoDB não está em execução."
        echo "Por favor, inicie o MongoDB antes de continuar:"
        echo "  Ubuntu: sudo systemctl start mongodb"
        echo "  macOS:  brew services start mongodb-community"
        echo "  Windows: Inicie o serviço 'MongoDB Server'"
    else
        echo "MongoDB está em execução!"
    fi
fi

# Configurar variáveis de ambiente para Flask
export FLASK_APP=app
export FLASK_ENV=development

echo ""
echo "=== Configuração concluída! ==="
echo ""
echo "Para iniciar o aplicativo, execute:"
echo "  source venv/bin/activate  # Se ainda não estiver ativado"
echo "  flask run"
echo ""
echo "Para criar um super_admin manualmente:"
echo "  python create_superadmin.py <username> <password>"
echo ""
echo "Para mais informações, consulte INITIALIZATION.md"