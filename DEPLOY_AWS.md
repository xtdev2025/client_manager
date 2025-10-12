# AWS Deployment Quick Start Guide

## 🚀 Deploy Rápido - 10 Minutos

### Pré-requisitos

- [ ] **Conta AWS + Credenciais** - [📖 Ver guia completo de como obter](docs/AWS_CREDENTIALS_SETUP.md)
- [ ] AWS CLI instalado
- [ ] MongoDB Atlas (criar em: <https://cloud.mongodb.com>)

> 🆕 **Primeira vez na AWS?** Veja nosso guia completo: [Como Obter Credenciais AWS](docs/AWS_CREDENTIALS_SETUP.md)

### Opção A: Elastic Beanstalk (Recomendado para Produção)

#### 1. Instalar ferramentas

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# EB CLI
pip install awsebcli --upgrade --user
```

#### 2. Configurar credenciais

```bash
aws configure
# Insira: Access Key ID, Secret Access Key, region (us-east-1)
```

#### 3. Preparar projeto

```bash
# Adicionar Gunicorn
echo "gunicorn==21.2.0" >> requirements.txt

# Criar Procfile
echo "web: gunicorn --bind :8000 --workers 4 --timeout 600 run:app" > Procfile

# Criar .ebextensions/python.config
mkdir -p .ebextensions
cat > .ebextensions/python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: app/static
EOF
```

#### 4. Deploy

```bash
# Inicializar EB
eb init -p python-3.10 client-manager --region us-east-1

# Criar ambiente e fazer deploy
eb create client-manager-prod

# Configurar variáveis de ambiente
eb setenv SECRET_KEY="sua-chave-secreta"
eb setenv MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/clientmanager"
eb setenv FLASK_CONFIG="production"

# Abrir no navegador
eb open
```

#### 5. Criar super admin

```bash
eb ssh
cd /var/app/current
python scripts/create_superadmin.py rootkit 13rafael
exit
```

**Pronto!** 🎉

---

### Opção B: EC2 (Mais Barato)

#### 1. Executar script automatizado

```bash
./scripts/aws_ec2_deploy.sh
```

#### 2. Ou seguir manual

Ver guia completo: [docs/AWS_DEPLOYMENT.md](./docs/AWS_DEPLOYMENT.md)

---

### Opção C: Lambda (Serverless - Mais Barato)

#### 1. Instalar Zappa

```bash
pip install zappa
```

#### 2. Configurar e deploy

```bash
# Inicializar
zappa init

# Editar zappa_settings.json com suas credenciais

# Deploy
zappa deploy production

# Obter URL
zappa status production
```

---

## 🎯 Comandos Úteis

### Elastic Beanstalk

```bash
# Ver status
eb status

# Ver logs
eb logs --stream

# Deploy nova versão
eb deploy

# Escalar
eb scale 2

# SSH
eb ssh

# Deletar
eb terminate
```

### EC2

```bash
# Listar instâncias
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name]' --output table

# SSH na instância
ssh -i clientmanager-key.pem ubuntu@<IP>

# Ver logs
sudo journalctl -u clientmanager -f

# Restart app
sudo systemctl restart clientmanager
```

### Lambda (Zappa)

```bash
# Deploy
zappa deploy production

# Update
zappa update production

# Ver logs
zappa tail production

# Status
zappa status production

# Deletar
zappa undeploy production
```

---

## 💰 Custos Estimados

| Opção | Custo/mês | Melhor Para |
|-------|-----------|-------------|
| **EB (Free Tier)** | $0 (1º ano) | Testes |
| **EB (Prod)** | $35 | Produção |
| **EC2 t2.micro** | $8 | Controle |
| **Lambda** | $2-5 | Baixo tráfego |

+ MongoDB Atlas M0: **$0** (512MB grátis permanente)

---

## 🆘 Problemas Comuns

### App não inicia (EB)

```bash
eb logs
```

### 502 Bad Gateway (EC2)

```bash
sudo systemctl status clientmanager
sudo journalctl -u clientmanager -n 50
```

### Banco não conecta

- Verificar MONGO_URI está correto
- Whitelist IP no MongoDB Atlas: `0.0.0.0/0`
- Testar localmente: `mongosh "mongodb+srv://..."`

---

## 📚 Documentação Completa

Ver: [docs/AWS_DEPLOYMENT.md](./docs/AWS_DEPLOYMENT.md)

- ✅ 4 opções de deploy detalhadas
- ✅ Configuração de MongoDB na AWS
- ✅ SSL/HTTPS setup
- ✅ Troubleshooting completo
- ✅ Scripts automatizados

---

## 🔥 Dica: Free Tier

Aproveite o **AWS Free Tier** (primeiro ano):

- EC2 t2.micro: 750 horas/mês grátis
- Lambda: 1M requests/mês grátis
- MongoDB Atlas M0: Grátis permanente

**Total: $0/mês no primeiro ano!** 🎉
