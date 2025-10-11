#!/usr/bin/env python3
"""
Script de configuração para o Client Manager
Este script configura o ambiente e inicializa o banco de dados

Usage: python scripts/setup.py
"""

import os
import sys
import subprocess
import platform
import shutil


def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 50)
    print(f"  {message}")
    print("=" * 50 + "\n")


def print_success(message):
    """Print a success message"""
    print(f"✓ {message}")


def print_warning(message):
    """Print a warning message"""
    print(f"⚠ AVISO: {message}")


def print_error(message):
    """Print an error message"""
    print(f"✗ ERRO: {message}")


def print_info(message):
    """Print an info message"""
    print(f"ℹ {message}")


def check_python_version():
    """Check if Python version is 3.9 or higher"""
    print_info("Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ é necessário. Versão atual: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def check_venv_exists():
    """Check if virtual environment already exists"""
    return os.path.exists('venv')


def create_venv():
    """Create a Python virtual environment"""
    print_info("Criando ambiente virtual Python...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print_success("Ambiente virtual criado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print_error("Falha ao criar ambiente virtual")
        return False


def get_venv_python():
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == 'Windows':
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:
        return os.path.join('venv', 'bin', 'python')


def get_venv_pip():
    """Get the path to pip in the virtual environment"""
    if platform.system() == 'Windows':
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        return os.path.join('venv', 'bin', 'pip')


def upgrade_pip():
    """Upgrade pip to the latest version"""
    print_info("Atualizando pip...")
    try:
        pip_path = get_venv_pip()
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        print_success("pip atualizado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print_warning("Não foi possível atualizar o pip, mas continuando...")
        return True


def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    print_info("Instalando dependências Python...")
    try:
        pip_path = get_venv_pip()
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print_success("Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print_error("Falha ao instalar dependências")
        return False


def check_mongodb():
    """Check if MongoDB is installed"""
    print_info("Verificando MongoDB...")
    
    if shutil.which('mongod') is None:
        print_warning("MongoDB não foi encontrado no PATH")
        print_info("Por favor, instale o MongoDB:")
        print("  • Ubuntu/Debian: sudo apt install mongodb")
        print("  • macOS (Homebrew): brew install mongodb-community")
        print("  • Windows: https://www.mongodb.com/try/download/community")
        return False
    
    print_success("MongoDB encontrado!")
    return True


def check_mongodb_running():
    """Check if MongoDB is running"""
    print_info("Verificando se MongoDB está em execução...")
    
    try:
        # Try to connect using pymongo
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure
        
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise an exception if cannot connect
        client.close()
        
        print_success("MongoDB está em execução!")
        return True
    except (ImportError, ConnectionFailure):
        print_warning("MongoDB não está em execução ou não está acessível")
        print_info("Para iniciar o MongoDB:")
        print("  • Ubuntu/Debian: sudo systemctl start mongodb")
        print("  • macOS (Homebrew): brew services start mongodb-community")
        print("  • Windows: Inicie o serviço 'MongoDB Server' no Gerenciador de Serviços")
        print("  • Manual: mongod --dbpath /caminho/para/dados")
        return False


def check_env_file():
    """Check if .env file exists"""
    print_info("Verificando arquivo .env...")
    
    if not os.path.exists('.env'):
        print_warning("Arquivo .env não encontrado")
        
        if os.path.exists('.env.example'):
            print_info("Copiando .env.example para .env...")
            shutil.copy('.env.example', '.env')
            print_success("Arquivo .env criado a partir do .env.example")
            print_warning("Por favor, edite o arquivo .env e configure:")
            print("  • SECRET_KEY (gere uma chave segura)")
            print("  • MONGO_URI (se necessário)")
            return True
        else:
            print_error("Arquivo .env.example também não foi encontrado")
            print_info("Crie um arquivo .env com as seguintes variáveis:")
            print("  FLASK_APP=run.py")
            print("  FLASK_ENV=development")
            print("  SECRET_KEY=sua-chave-secreta-aqui")
            print("  MONGO_URI=mongodb://localhost:27017/client_manager")
            return False
    
    print_success("Arquivo .env encontrado!")
    return True


def print_next_steps():
    """Print instructions for next steps"""
    print_header("Configuração Concluída!")
    
    print("📋 Próximos passos:\n")
    
    print("1. Ativar o ambiente virtual:")
    if platform.system() == 'Windows':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Iniciar o aplicativo:")
    print("   python run.py")
    print("   ou")
    print("   flask run")
    
    print("\n3. Acessar o sistema:")
    print("   http://127.0.0.1:5000")
    
    print("\n4. Fazer login com o super admin padrão:")
    print("   Usuário: superadmin")
    print("   Senha: Admin@123")
    print("   ⚠ ALTERE A SENHA IMEDIATAMENTE!")
    
    print("\n5. Criar super admin manualmente (opcional):")
    print("   python scripts/create_superadmin.py <username> <password>")
    
    print("\n📚 Para mais informações, consulte README.md")
    print()


def main():
    """Main setup function"""
    print_header("Client Manager - Setup")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create or check virtual environment
    if check_venv_exists():
        print_success("Ambiente virtual já existe")
    else:
        if not create_venv():
            sys.exit(1)
    
    # Upgrade pip
    if not upgrade_pip():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check MongoDB
    mongodb_installed = check_mongodb()
    if mongodb_installed:
        check_mongodb_running()
    
    # Check .env file
    check_env_file()
    
    # Print next steps
    print_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
