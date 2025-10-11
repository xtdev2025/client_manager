from app import create_app
import sys

app = create_app()

def print_startup_info():
    """Print useful startup information"""
    print("\n" + "="*80)
    print("🚀 CLIENT MANAGER - Sistema de Gerenciamento de Clientes")
    print("="*80)
    print("\n📍 Servidor rodando em: http://localhost:5000")
    print("\n📚 DOCUMENTAÇÃO DA API (63 Endpoints Documentados):")
    print("   • Swagger UI (Interativo): http://localhost:5000/api/docs")
    print("   • OpenAPI JSON Spec:       http://localhost:5000/api/swagger.json")
    print("   • Documentação Completa:   docs/API_DOCUMENTATION.md")
    print("   • Quick Reference:         docs/API_QUICK_REFERENCE.md")
    
    print("\n🔐 AUTENTICAÇÃO:")
    print("   • Login:           http://localhost:5000/auth/login")
    print("   • Logout:          http://localhost:5000/auth/logout")
    print("   • Registrar Admin: http://localhost:5000/auth/register_admin")
    
    print("\n📊 PRINCIPAIS ENDPOINTS:")
    print("   • Dashboard:       http://localhost:5000/dashboard")
    print("   • Clientes:        http://localhost:5000/clients/")
    print("   • Domínios:        http://localhost:5000/domains/")
    print("   • Templates:       http://localhost:5000/templates/")
    print("   • Planos:          http://localhost:5000/plans/")
    print("   • Infos Bancárias: http://localhost:5000/infos/")
    print("   • Administradores: http://localhost:5000/admins/")
    print("   • Audit Logs:      http://localhost:5000/admins/audit-logs")
    
    print("\n👤 PORTAL DO CLIENTE:")
    print("   • Minhas Infos:    http://localhost:5000/client/my-infos")
    print("   • Meus Domínios:   http://localhost:5000/client/my-domains")
    print("   • Estatísticas:    http://localhost:5000/client/my-click-stats")
    print("   • Mudar Senha:     http://localhost:5000/client/my-change-password")
    
    print("\n🔧 INFORMAÇÕES TÉCNICAS:")
    print(f"   • Python:          {sys.version.split()[0]}")
    print(f"   • Flask:           {app.config.get('FLASK_ENV', 'production')}")
    print(f"   • Debug Mode:      {app.debug}")
    print(f"   • MongoDB:         {app.config.get('MONGO_URI', 'N/A').split('@')[-1] if '@' in app.config.get('MONGO_URI', '') else 'localhost'}")
    print(f"   • Rate Limiting:   Ativo (200/dia, 50/hora)")
    
    print("\n📝 ENDPOINTS REGISTRADOS:")
    # Count and group endpoints
    endpoints_by_blueprint = {}
    total_routes = 0
    
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
            if blueprint not in endpoints_by_blueprint:
                endpoints_by_blueprint[blueprint] = 0
            endpoints_by_blueprint[blueprint] += 1
            total_routes += 1
    
    for blueprint, count in sorted(endpoints_by_blueprint.items()):
        print(f"   • {blueprint.capitalize():20s} {count:3d} rotas")
    
    print(f"\n   📊 TOTAL: {total_routes} endpoints registrados")
    
    print("\n💡 DICAS:")
    print("   • Use Ctrl+C para parar o servidor")
    print("   • Acesse /api/docs para documentação interativa")
    print("   • Logs de auditoria disponíveis em /admins/audit-logs")
    print("   • Usuário padrão: superadmin (veja logs acima para senha)")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    print_startup_info()
    app.run(debug=True)