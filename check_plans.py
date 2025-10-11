from app import create_app, mongo
from app.models.client import Client
from app.models.plan import Plan

app = create_app()
with app.app_context():
    # Get all clients
    clients = list(mongo.db.users.find({'role': 'client'}))
    print(f"Total de clientes: {len(clients)}\n")
    
    for client in clients:
        print(f"Cliente: {client.get('username')}")
        print(f"  - ID: {client.get('_id')}")
        print(f"  - plan_id: {client.get('plan_id')}")
        
        if client.get('plan_id'):
            plan = Plan.get_by_id(client.get('plan_id'))
            if plan:
                print(f"  - Plano encontrado: {plan.get('name')}")
            else:
                print(f"  - ⚠️ Plano não encontrado no banco!")
        else:
            print(f"  - ⚠️ Sem plan_id definido")
        
        print(f"  - expiredAt: {client.get('expiredAt')}")
        print(f"  - planActivatedAt: {client.get('planActivatedAt')}")
        print()
