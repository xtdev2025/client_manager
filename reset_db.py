#!/usr/bin/env python
"""
Script para resetar o banco de dados completamente
Uso: python reset_db.py
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def reset_database():
    """Reseta o banco de dados completamente"""
    
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/clientmanager')
    
    print("=" * 80)
    print("🗑️  RESETANDO BANCO DE DADOS")
    print("=" * 80)
    print()
    
    try:
        # Conectar ao MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Conectado ao MongoDB")
        
        # Obter o banco de dados
        db_name = mongo_uri.split('/')[-1]
        db = client[db_name]
        
        # Listar coleções existentes
        collections = db.list_collection_names()
        print(f"\n📋 Coleções encontradas: {len(collections)}")
        for col in collections:
            count = db[col].count_documents({})
            print(f"   • {col}: {count} documentos")
        
        # Confirmar
        print()
        confirm = input("⚠️  ATENÇÃO: Isso vai APAGAR TODOS OS DADOS! Confirmar? (digite 'SIM'): ")
        
        if confirm != 'SIM':
            print("❌ Operação cancelada")
            return False
        
        print()
        print("🗑️  Deletando todas as coleções...")
        
        # Deletar todas as coleções
        for collection_name in collections:
            db[collection_name].drop()
            print(f"   ✅ {collection_name} deletada")
        
        print()
        print("=" * 80)
        print("✅ BANCO DE DADOS RESETADO COM SUCESSO!")
        print("=" * 80)
        print()
        print("📝 Próximo passo: Execute o Client Manager para reinicializar os dados:")
        print("   cd /home/rootkit/Apps/xPages/client_manager")
        print("   python run.py")
        print()
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao resetar banco: {e}")
        return False

if __name__ == '__main__':
    reset_database()
