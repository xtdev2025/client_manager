# 🚀 Deploy na AWS - Client Manager

Guia completo para fazer deploy da aplicação Flask na Amazon Web Services (AWS).

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Opção 1: AWS Elastic Beanstalk (Recomendado)](#opção-1-aws-elastic-beanstalk-recomendado)
- [Opção 2: AWS EC2 (Máquina Virtual)](#opção-2-aws-ec2-máquina-virtual)
- [Opção 3: AWS ECS com Docker](#opção-3-aws-ecs-com-docker)
- [Opção 4: AWS Lambda + API Gateway (Serverless)](#opção-4-aws-lambda--api-gateway-serverless)
- [MongoDB na AWS](#mongodb-na-aws)
- [SSL/HTTPS e Domínio](#sslhttps-e-domínio)
- [Custos Estimados](#custos-estimados)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### Comparação das Opções

| Opção | Dificuldade | Controle | Custo/mês | Melhor Para |
|-------|-------------|----------|-----------|-------------|
| **Elastic Beanstalk** | ⭐⭐ Fácil | Médio | $15-30 | Produção rápida |
| **EC2** | ⭐⭐⭐ Médio | Alto | $8-50 | Controle total |
| **ECS + Docker** | ⭐⭐⭐⭐ Difícil | Alto | $20-60 | Microserviços |
| **Lambda** | ⭐⭐⭐⭐⭐ Muito Difícil | Baixo | $0-5 | Baixo tráfego |

### Pré-requisitos Gerais

- **Conta AWS** - [📖 Como criar e obter credenciais](AWS_CREDENTIALS_SETUP.md)
- AWS CLI instalado
- Git instalado
- MongoDB Atlas (ou DocumentDB na AWS)

> 🆕 **Primeira vez na AWS?** Veja nosso guia completo: [Como Obter Credenciais AWS](AWS_CREDENTIALS_SETUP.md)

---

## 📦 Opção 1: AWS Elastic Beanstalk (Recomendado)

### Vantagens

- ✅ Deploy automático
- ✅ Auto-scaling configurável
- ✅ Load balancer incluído
- ✅ SSL/HTTPS fácil
- ✅ Monitoramento integrado
- ✅ Rollback automático

### 1. Instalar AWS CLI e EB CLI

```bash
# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar instalação
aws --version

# Instalar EB CLI
pip install awsebcli --upgrade --user

# Verificar instalação
eb --version
```

### 2. Configurar AWS CLI

```bash
# Configurar credenciais (você precisará de Access Key ID e Secret Access Key)
aws configure

# Quando solicitado, insira:
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region name: us-east-1
# Default output format: json
```

### 3. Preparar Aplicação para Elastic Beanstalk

Criar arquivo `.ebextensions/python.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: app/static
```

### 4. Criar arquivo `Procfile`

```
web: gunicorn --bind :8000 --workers 4 --timeout 600 run:app
```

### 5. Atualizar `requirements.txt`

Adicionar Gunicorn se não estiver:

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### 6. Inicializar Elastic Beanstalk

```bash
# Na raiz do projeto
eb init

# Quando solicitado:
# Select a default region: 1 (us-east-1)
# Select an application to use: Create new Application
# Enter Application Name: client-manager
# Select a platform: Python
# Select a platform branch: Python 3.10
# Do you wish to continue with CodeCommit? n
# Do you want to set up SSH? y
```

### 7. Criar Ambiente e Fazer Deploy

```bash
# Criar ambiente de produção
eb create client-manager-prod

# Aguarde alguns minutos...
# Deploy automático será feito
```

### 8. Configurar Variáveis de Ambiente

```bash
# Configurar SECRET_KEY
eb setenv SECRET_KEY="sua-chave-secreta-super-segura"

# Configurar MongoDB URI
eb setenv MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/clientmanager"

# Configurar Flask Config
eb setenv FLASK_CONFIG="production"

# Aplicar configurações (restart automático)
```

### 9. Abrir Aplicação no Navegador

```bash
eb open
```

### 10. Criar Super Admin

```bash
# SSH no servidor
eb ssh

# Navegar até o diretório da aplicação
cd /var/app/current

# Criar super admin
python scripts/create_superadmin.py $ADMIN_USERNAME $ADMIN_PASSWORD

# Sair
exit
```

### Comandos Úteis - Elastic Beanstalk

```bash
# Ver status
eb status

# Ver logs em tempo real
eb logs --stream

# Fazer deploy de novas versões
git add .
git commit -m "Nova versão"
eb deploy

# Escalar aplicação
eb scale 2  # 2 instâncias

# Ver saúde da aplicação
eb health

# Configurar domínio customizado
eb setenv VIRTUAL_HOST="seudominio.com"

# Deletar ambiente (CUIDADO!)
eb terminate client-manager-prod
```

---

## 🖥️ Opção 2: AWS EC2 (Máquina Virtual)

### Vantagens

- ✅ Controle total do servidor
- ✅ Instalar qualquer software
- ✅ SSH completo
- ✅ Mais barato para apps maiores

### 1. Criar Instância EC2

```bash
# Criar par de chaves SSH
aws ec2 create-key-pair \
  --key-name clientmanager-key \
  --query 'KeyMaterial' \
  --output text > clientmanager-key.pem

# Dar permissões corretas
chmod 400 clientmanager-key.pem

# Criar security group
aws ec2 create-security-group \
  --group-name clientmanager-sg \
  --description "Client Manager Security Group"

# Obter ID do security group
SG_ID=$(aws ec2 describe-security-groups \
  --group-names clientmanager-sg \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Abrir portas 22 (SSH), 80 (HTTP), 443 (HTTPS)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Criar instância EC2 (Ubuntu 22.04, t2.micro)
aws ec2 run-instances \
  --image-id ami-0e001c9271cf7f3b9 \
  --instance-type t2.micro \
  --key-name clientmanager-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ClientManager}]'
```

### 2. Obter IP Público da Instância

```bash
# Listar instâncias
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ClientManager" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### 3. Conectar via SSH

```bash
# Conectar (substitua <IP_PUBLICO>)
ssh -i clientmanager-key.pem ubuntu@<IP_PUBLICO>
```

### 4. Configurar Servidor (Dentro da EC2)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# Instalar Nginx
sudo apt install -y nginx

# Instalar Git
sudo apt install -y git

# Clonar repositório
cd /home/ubuntu
git clone https://github.com/rootkitoriginal/client_manager.git
cd client_manager

# Criar virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn
```

### 5. Criar arquivo `.env`

```bash
nano .env
```

Adicionar:

```ini
SECRET_KEY=sua-chave-secreta-super-segura
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/clientmanager
FLASK_CONFIG=production
```

Salvar: `Ctrl+X`, `Y`, `Enter`

### 6. Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/clientmanager.service
```

Conteúdo:

```ini
[Unit]
Description=Client Manager Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/client_manager
Environment="PATH=/home/ubuntu/client_manager/venv/bin"
ExecStart=/home/ubuntu/client_manager/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:clientmanager.sock \
    --timeout 600 \
    run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Salvar: `Ctrl+X`, `Y`, `Enter`

### 7. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/clientmanager
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/client_manager/clientmanager.sock;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    location /static {
        alias /home/ubuntu/client_manager/app/static;
        expires 30d;
    }

    client_max_body_size 100M;
}
```

Salvar: `Ctrl+X`, `Y`, `Enter`

### 8. Ativar e Iniciar Serviços

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

### 9. Criar Super Admin

```bash
cd /home/ubuntu/client_manager
source venv/bin/activate
python scripts/create_superadmin.py rootkit 13rafael
```

### 10. Acessar Aplicação

Abra no navegador: `http://<IP_PUBLICO>`

### Comandos Úteis - EC2

```bash
# Ver logs da aplicação
sudo journalctl -u clientmanager -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Reiniciar aplicação
sudo systemctl restart clientmanager

# Reiniciar Nginx
sudo systemctl restart nginx

# Atualizar código
cd /home/ubuntu/client_manager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart clientmanager
```

---

## 🐳 Opção 3: AWS ECS com Docker

### Vantagens

- ✅ Containerização
- ✅ Escalabilidade horizontal
- ✅ Isolamento de ambiente
- ✅ CI/CD simplificado

### 1. Criar Dockerfile

```dockerfile
FROM python:3.10-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "600", "run:app"]
```

### 2. Criar `.dockerignore`

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git
.github
.vscode
*.md
tests/
docs/
node_modules/
.DS_Store
```

### 3. Testar Localmente

```bash
# Build da imagem
docker build -t client-manager .

# Rodar container
docker run -p 8000:8000 \
  -e SECRET_KEY="sua-chave" \
  -e MONGO_URI="mongodb+srv://..." \
  -e FLASK_CONFIG="production" \
  client-manager

# Testar no navegador: http://localhost:8000
```

### 4. Criar Repository no ECR (Elastic Container Registry)

```bash
# Criar repository
aws ecr create-repository --repository-name client-manager

# Obter URI do repository
ECR_URI=$(aws ecr describe-repositories \
  --repository-names client-manager \
  --query 'repositories[0].repositoryUri' \
  --output text)

echo "ECR URI: $ECR_URI"
```

### 5. Fazer Push da Imagem para ECR

```bash
# Login no ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URI

# Tag da imagem
docker tag client-manager:latest $ECR_URI:latest

# Push para ECR
docker push $ECR_URI:latest
```

### 6. Criar Cluster ECS

```bash
# Criar cluster
aws ecs create-cluster --cluster-name client-manager-cluster
```

### 7. Criar Task Definition

Criar arquivo `task-definition.json`:

```json
{
  "family": "client-manager-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "client-manager",
      "image": "<ECR_URI>:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_CONFIG",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:client-manager/SECRET_KEY"
        },
        {
          "name": "MONGO_URI",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:client-manager/MONGO_URI"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/client-manager",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Registrar task:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### 8. Criar Serviço ECS

```bash
aws ecs create-service \
  --cluster client-manager-cluster \
  --service-name client-manager-service \
  --task-definition client-manager-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 🚀 Opção 4: AWS Lambda + API Gateway (Serverless)

### Vantagens

- ✅ Pague apenas pelo uso
- ✅ Escalabilidade automática infinita
- ✅ Zero manutenção de servidor
- ✅ Muito barato para baixo tráfego

### Desvantagens

- ❌ Cold start (inicialização lenta)
- ❌ Limite de 15 minutos por requisição
- ❌ Mais complexo para aplicações com estado

### 1. Instalar Zappa

```bash
pip install zappa
```

### 2. Inicializar Zappa

```bash
zappa init
```

Responder perguntas:

- Environment: `production`
- S3 bucket: (usar sugestão)
- Application function: `run.app`

### 3. Editar `zappa_settings.json`

```json
{
    "production": {
        "app_function": "run.app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "client-manager",
        "runtime": "python3.10",
        "s3_bucket": "zappa-client-manager-deployments",
        "timeout_seconds": 300,
        "memory_size": 512,
        "environment_variables": {
            "FLASK_CONFIG": "production"
        },
        "aws_environment_variables": {
            "SECRET_KEY": "sua-chave-secreta",
            "MONGO_URI": "mongodb+srv://..."
        }
    }
}
```

### 4. Deploy com Zappa

```bash
# Primeiro deploy
zappa deploy production

# Updates posteriores
zappa update production

# Ver logs
zappa tail production

# Obter URL
zappa status production
```

---

## 🗄️ MongoDB na AWS

### Opção 1: MongoDB Atlas (Recomendado)

1. Criar conta: https://cloud.mongodb.com
2. Criar cluster gratuito (M0)
3. Whitelist IP: `0.0.0.0/0` (ou IPs específicos da AWS)
4. Criar usuário e senha
5. Copiar connection string

**Free Tier:** 512MB - $0/mês

### Opção 2: AWS DocumentDB (Compatível com MongoDB)

```bash
# Criar cluster DocumentDB
aws docdb create-db-cluster \
  --db-cluster-identifier client-manager-db \
  --engine docdb \
  --master-username admin \
  --master-user-password SenhaSegura123 \
  --vpc-security-group-ids sg-xxx

# Criar instância
aws docdb create-db-instance \
  --db-instance-identifier client-manager-db-instance \
  --db-instance-class db.t3.medium \
  --engine docdb \
  --db-cluster-identifier client-manager-db
```

**Custo:** ~$50-200/mês (mais caro que Atlas)

### Opção 3: MongoDB em EC2

```bash
# Instalar MongoDB na EC2
sudo apt-get install -y mongodb-org

# Iniciar serviço
sudo systemctl start mongod
sudo systemctl enable mongod

# Criar usuário
mongosh
use clientmanager
db.createUser({
  user: "admin",
  pwd: "senha123",
  roles: [{role: "readWrite", db: "clientmanager"}]
})
```

---

## 🔒 SSL/HTTPS e Domínio

### Opção 1: AWS Certificate Manager (ACM) + CloudFront

```bash
# Solicitar certificado SSL (gratuito!)
aws acm request-certificate \
  --domain-name seudominio.com \
  --validation-method DNS

# Criar distribuição CloudFront
# (Usar console AWS - mais fácil)
```

### Opção 2: Let's Encrypt com Certbot (EC2)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seudominio.com

# Renovação automática
sudo certbot renew --dry-run
```

### Configurar Domínio

1. Comprar domínio (Route 53, GoDaddy, etc.)
2. Apontar para Load Balancer ou EC2 IP
3. Configurar registros DNS:
   - Tipo A: IP público
   - Tipo CNAME: Load Balancer URL

---

## 💰 Custos Estimados

### Opção 1: Elastic Beanstalk

| Recurso | Custo/mês |
|---------|-----------|
| EC2 t2.small | $17 |
| Load Balancer | $18 |
| **Total** | **$35/mês** |

### Opção 2: EC2 (t2.micro)

| Recurso | Custo/mês |
|---------|-----------|
| EC2 t2.micro | $8 |
| IP Elástico | $0 (se usado) |
| **Total** | **$8/mês** |

### Opção 3: ECS Fargate

| Recurso | Custo/mês |
|---------|-----------|
| Fargate (0.5 vCPU, 1GB) | $15 |
| Load Balancer | $18 |
| **Total** | **$33/mês** |

### Opção 4: Lambda

| Recurso | Custo/mês |
|---------|-----------|
| Lambda (1M requests) | $0.20 |
| API Gateway | $3.50 |
| **Total** | **~$4/mês** |

### MongoDB

| Opção | Custo/mês |
|-------|-----------|
| Atlas M0 (Free) | $0 |
| Atlas M2 | $9 |
| DocumentDB | $50-200 |

### Free Tier (Primeiro Ano)

- EC2 t2.micro: 750 horas/mês grátis
- Lambda: 1M requisições grátis/mês
- MongoDB Atlas: M0 grátis permanente

---

## 🆘 Troubleshooting

### Elastic Beanstalk não inicia

```bash
# Ver logs detalhados
eb logs

# Verificar health
eb health

# Ver variáveis de ambiente
eb printenv
```

### EC2 não conecta

```bash
# Verificar security group
aws ec2 describe-security-groups --group-ids sg-xxx

# Verificar status da instância
aws ec2 describe-instance-status --instance-ids i-xxx
```

### Aplicação retorna 502

```bash
# EC2: verificar logs
sudo journalctl -u clientmanager -n 100

# Verificar se Gunicorn está rodando
ps aux | grep gunicorn
```

### MongoDB não conecta

```bash
# Testar conexão
mongosh "mongodb+srv://..."

# Verificar IP whitelist no Atlas
# Verificar security group no DocumentDB
```

---

## 📚 Scripts Úteis AWS CLI

```bash
# Listar todas as instâncias EC2
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' --output table

# Parar instância
aws ec2 stop-instances --instance-ids i-xxx

# Iniciar instância
aws ec2 start-instances --instance-ids i-xxx

# Deletar instância
aws ec2 terminate-instances --instance-ids i-xxx

# Ver custos
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## 🎯 Recomendação

### Para Começar

**Elastic Beanstalk + MongoDB Atlas Free**

- Total: ~$35/mês (ou $0 no primeiro ano com Free Tier)
- Fácil de configurar
- Escalável
- SSL gratuito

### Para Produção

**EC2 t3.small + MongoDB Atlas M2**

- Total: ~$30/mês
- Mais controle
- Melhor performance
- Custom configurations

### Para Baixo Tráfego

**Lambda + API Gateway + Atlas M0**

- Total: ~$4/mês
- Muito barato
- Zero manutenção
- Perfeito para MVPs

---

## 📖 Documentação AWS

- [Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EC2](https://docs.aws.amazon.com/ec2/)
- [ECS](https://docs.aws.amazon.com/ecs/)
- [Lambda](https://docs.aws.amazon.com/lambda/)
- [DocumentDB](https://docs.aws.amazon.com/documentdb/)

---

**Pronto para fazer deploy na AWS! 🚀**
