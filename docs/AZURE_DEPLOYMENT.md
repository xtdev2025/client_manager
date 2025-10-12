# 🚀 Deploy no Azure - Client Manager

## 📋 Pré-requisitos

- Conta Azure ativa
- Azure CLI instalado (`az`)
- Git instalado
- MongoDB Atlas ou Azure Cosmos DB

---

## 🎯 Opção 1: Azure App Service (Recomendado)

### Vantagens:
- ✅ Mais rápido e fácil
- ✅ Auto-scaling
- ✅ SSL/HTTPS automático
- ✅ Integração com GitHub Actions
- ✅ Gerenciamento simplificado

### 1️⃣ Instalar Azure CLI

```bash
# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verificar instalação
az --version
```

### 2️⃣ Login no Azure

```bash
az login
```

### 3️⃣ Criar Grupo de Recursos

```bash
az group create \
  --name rg-clientmanager \
  --location eastus
```

### 4️⃣ Criar App Service Plan (Linux)

```bash
# Free Tier (para testes)
az appservice plan create \
  --name plan-clientmanager \
  --resource-group rg-clientmanager \
  --sku F1 \
  --is-linux

# OU Production (B1 - Basic)
az appservice plan create \
  --name plan-clientmanager \
  --resource-group rg-clientmanager \
  --sku B1 \
  --is-linux
```

### 5️⃣ Criar Web App

```bash
az webapp create \
  --resource-group rg-clientmanager \
  --plan plan-clientmanager \
  --name clientmanager-rootkit \
  --runtime "PYTHON:3.10"
```

### 6️⃣ Configurar Variáveis de Ambiente

```bash
# MongoDB URI
az webapp config appsettings set \
  --resource-group rg-clientmanager \
  --name clientmanager-rootkit \
  --settings MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/clientmanager"

# Secret Key
az webapp config appsettings set \
  --resource-group rg-clientmanager \
  --name clientmanager-rootkit \
  --settings SECRET_KEY="sua-chave-secreta-aqui"

# Flask Config
az webapp config appsettings set \
  --resource-group rg-clientmanager \
  --name clientmanager-rootkit \
  --settings FLASK_CONFIG="production"
```

### 7️⃣ Criar arquivo `startup.sh`

```bash
#!/bin/bash
gunicorn --bind=0.0.0.0 --timeout 600 run:app
```

### 8️⃣ Configurar Startup Command

```bash
az webapp config set \
  --resource-group rg-clientmanager \
  --name clientmanager-rootkit \
  --startup-file "startup.sh"
```

### 9️⃣ Deploy via Git

```bash
# Configurar deployment local git
az webapp deployment source config-local-git \
  --name clientmanager-rootkit \
  --resource-group rg-clientmanager

# Adicionar remote
git remote add azure <URL_RETORNADA>

# Deploy
git push azure main
```

### 🔟 Acessar Aplicação

```
https://clientmanager-rootkit.azurewebsites.net
```

---

## 🖥️ Opção 2: Azure Virtual Machine (Mais Controle - IaaS)

### Vantagens:
- ✅ Controle total do servidor
- ✅ Pode instalar qualquer software
- ✅ Mais barato para apps grandes
- ✅ Acesso SSH completo

### 1️⃣ Criar VM Ubuntu

```bash
az vm create \
  --resource-group rg-clientmanager \
  --name vm-clientmanager \
  --image Ubuntu2204 \
  --size Standard_B1s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard
```

### 2️⃣ Abrir Porta 80 (HTTP) e 443 (HTTPS)

```bash
az vm open-port \
  --port 80 \
  --resource-group rg-clientmanager \
  --name vm-clientmanager

az vm open-port \
  --port 443 \
  --resource-group rg-clientmanager \
  --name vm-clientmanager
```

### 3️⃣ Conectar via SSH

```bash
# Obter IP público
az vm show \
  --resource-group rg-clientmanager \
  --name vm-clientmanager \
  --show-details \
  --query publicIps \
  --output tsv

# Conectar
ssh azureuser@<IP_PUBLICO>
```

### 4️⃣ Instalar Dependências na VM

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# Instalar Nginx
sudo apt install -y nginx

# Instalar Git
sudo apt install -y git
```

### 5️⃣ Clonar Repositório

```bash
cd /home/azureuser
git clone https://github.com/rootkitoriginal/client_manager.git
cd client_manager
```

### 6️⃣ Configurar Ambiente Python

```bash
# Criar virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn
```

### 7️⃣ Criar arquivo `.env`

```bash
nano .env
```

Adicionar:
```ini
SECRET_KEY=sua-chave-secreta-super-segura
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/clientmanager
FLASK_CONFIG=production
```

### 8️⃣ Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/clientmanager.service
```

Conteúdo:
```ini
[Unit]
Description=Client Manager Flask Application
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/client_manager
Environment="PATH=/home/azureuser/client_manager/venv/bin"
ExecStart=/home/azureuser/client_manager/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:clientmanager.sock \
    --timeout 600 \
    run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 9️⃣ Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/clientmanager
```

Conteúdo:
```nginx
server {
    listen 80;
    server_name <SEU_IP_OU_DOMINIO>;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/azureuser/client_manager/clientmanager.sock;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    location /static {
        alias /home/azureuser/client_manager/app/static;
    }
}
```

### 🔟 Ativar e Iniciar Serviços

```bash
# Habilitar site Nginx
sudo ln -s /etc/nginx/sites-available/clientmanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Iniciar aplicação
sudo systemctl start clientmanager
sudo systemctl enable clientmanager

# Verificar status
sudo systemctl status clientmanager
```

### 1️⃣1️⃣ Configurar MongoDB Atlas

1. Acesse https://cloud.mongodb.com
2. Crie um cluster gratuito
3. Adicione IP da VM Azure no Whitelist: `0.0.0.0/0` (ou IP específico)
4. Crie usuário de banco de dados
5. Copie a connection string

### 1️⃣2️⃣ Criar Super Admin

```bash
cd /home/azureuser/client_manager
source venv/bin/activate
python scripts/create_superadmin.py rootkit 13rafael
```

---

## 🔒 Configurar SSL/HTTPS (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL (substitua seu-dominio.com)
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo certbot renew --dry-run
```

---

## 📊 Monitoramento

### Ver logs da aplicação
```bash
sudo journalctl -u clientmanager -f
```

### Ver logs do Nginx
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Reiniciar aplicação
```bash
sudo systemctl restart clientmanager
```

---

## 💰 Custos Estimados

### App Service:
- **Free (F1)**: $0/mês (limitações)
- **Basic (B1)**: ~$13/mês
- **Standard (S1)**: ~$70/mês

### Virtual Machine:
- **B1s (1 vCPU, 1GB RAM)**: ~$8/mês
- **B2s (2 vCPU, 4GB RAM)**: ~$30/mês

### MongoDB Atlas:
- **Free (M0)**: $0/mês (512MB)
- **Shared (M2)**: ~$9/mês (2GB)

---

## 🎯 Recomendação

**Para começar:** Use **Azure App Service** com **MongoDB Atlas Free**
- Total: $0-13/mês
- Fácil de configurar
- Escalável
- SSL gratuito

**Para produção:** Use **VM B1s** com **MongoDB Atlas M2**
- Total: ~$17/mês
- Mais controle
- Melhor performance
- Pode hospedar múltiplas aplicações

---

## 📚 Comandos Úteis

```bash
# Ver recursos Azure
az resource list --resource-group rg-clientmanager --output table

# Ver logs do App Service
az webapp log tail --name clientmanager-rootkit --resource-group rg-clientmanager

# Restart App Service
az webapp restart --name clientmanager-rootkit --resource-group rg-clientmanager

# Deletar tudo
az group delete --name rg-clientmanager --yes
```

---

## 🆘 Troubleshooting

### App não inicia
1. Verificar logs: `az webapp log tail`
2. Verificar variáveis de ambiente
3. Verificar requirements.txt completo

### Erro 502 Bad Gateway
1. Verificar gunicorn está rodando: `sudo systemctl status clientmanager`
2. Verificar socket file existe: `ls -l clientmanager.sock`
3. Verificar logs: `sudo journalctl -u clientmanager -n 50`

### Banco de dados não conecta
1. Verificar MONGO_URI está correto
2. Verificar IP está whitelisted no Atlas
3. Testar conexão: `mongosh "mongodb+srv://..."`

---

**Boa sorte com o deploy! 🚀**
