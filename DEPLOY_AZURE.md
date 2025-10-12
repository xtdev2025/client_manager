# Azure Deployment Quick Start Guide

## 🚀 Deploy Rápido - 5 Minutos

### Pré-requisitos
- [ ] Conta Azure (criar em: https://azure.microsoft.com/free/)
- [ ] Azure CLI instalado
- [ ] MongoDB Atlas (criar em: https://cloud.mongodb.com)

### 1. Login no Azure
```bash
az login
```

### 2. Executar Deploy Automático
```bash
# Criar recursos e fazer deploy
./scripts/azure_deploy.sh
```

### 3. Configurar Variáveis de Ambiente no Portal Azure
1. Acesse: https://portal.azure.com
2. Navegue até: App Services → clientmanager-rootkit → Configuration
3. Adicione as variáveis:
   - `SECRET_KEY`: sua-chave-secreta
   - `MONGO_URI`: mongodb+srv://...
   - `FLASK_CONFIG`: production

### 4. Criar Super Admin
```bash
# Via Azure Cloud Shell
az webapp ssh --name clientmanager-rootkit --resource-group rg-clientmanager

# Dentro da VM
cd /home/site/wwwroot
python scripts/create_superadmin.py rootkit 13rafael
```

### 5. Acessar Aplicação
```
https://clientmanager-rootkit.azurewebsites.net
```

## 🎯 Comandos Úteis

### Ver logs em tempo real
```bash
az webapp log tail --name clientmanager-rootkit --resource-group rg-clientmanager
```

### Restart da aplicação
```bash
az webapp restart --name clientmanager-rootkit --resource-group rg-clientmanager
```

### Ver status
```bash
az webapp show --name clientmanager-rootkit --resource-group rg-clientmanager --query state
```

### Deploy manual via Git
```bash
# Configurar deployment
az webapp deployment source config-local-git \
  --name clientmanager-rootkit \
  --resource-group rg-clientmanager

# Adicionar remote e fazer push
git remote add azure <URL>
git push azure main
```

## 💡 Dicas

- **Free Tier**: Use F1 para testes (limitações de performance)
- **Production**: Use B1 ou superior
- **MongoDB**: Use Atlas M0 (free) para começar
- **SSL**: Automático no Azure App Service
- **Custom Domain**: Configure no portal Azure

## 🆘 Problemas Comuns

### App não inicia
```bash
# Ver logs detalhados
az webapp log download --name clientmanager-rootkit --resource-group rg-clientmanager
```

### 502 Bad Gateway
- Verificar MONGO_URI está correto
- Verificar requirements.txt está completo
- Verificar startup.sh tem permissões de execução

### Banco não conecta
- Whitelist IP no MongoDB Atlas: 0.0.0.0/0
- Verificar connection string está correta
- Testar localmente primeiro

## 📚 Documentação Completa
Ver: [docs/AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)
