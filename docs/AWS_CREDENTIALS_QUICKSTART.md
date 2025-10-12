# 🚀 Quick Start - Obter Credenciais AWS em 5 Minutos

## Passo a Passo Visual

### 1️⃣ Criar Conta AWS

```
🌐 https://aws.amazon.com/free/
   ↓
📧 Email + Senha
   ↓
💳 Cartão (verificação, não cobra)
   ↓
✅ Conta criada!
```

### 2️⃣ Obter Access Keys

#### Método Rápido (IAM User):

1. **Acesse**: <https://console.aws.amazon.com/iam/>

2. **Navegue**:
   ```
   Console AWS
      ↓
   🔍 Buscar "IAM"
      ↓
   👥 Users (menu lateral)
      ↓
   ➕ Add users
   ```

3. **Criar usuário**:
   ```
   Nome: client-manager-dev
   ☑️ Access key - Programmatic access
   ```

4. **Permissões** (escolha uma):

   **Opção A - Desenvolvimento** (mais fácil):
   ```
   ☑️ AdministratorAccess
   ```

   **Opção B - Produção** (mais seguro):
   ```
   ☑️ AmazonEC2FullAccess
   ☑️ AWSElasticBeanstalkFullAccess
   ☑️ AmazonS3FullAccess
   ```

5. **Criar e SALVAR**:
   ```
   Access Key ID: AKIA... (copie!)
   Secret Access Key: wJalr... (copie!)
   📥 Download .csv (recomendado)
   ```

   ⚠️ **ATENÇÃO**: Você só verá o Secret uma vez!

### 3️⃣ Configurar AWS CLI

```bash
# Instalar AWS CLI (se não tem)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configurar credenciais
aws configure
```

**Cole suas credenciais**:

```bash
AWS Access Key ID [None]: AKIA... (cole aqui)
AWS Secret Access Key [None]: wJalr... (cole aqui)
Default region name [None]: us-east-1
Default output format [None]: json
```

### 4️⃣ Testar

```bash
# Verificar se funcionou
aws sts get-caller-identity
```

**Deve mostrar**:

```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/client-manager-dev"
}
```

✅ **Se viu isso, funcionou! Pode fazer deploy agora!**

### 5️⃣ Fazer Deploy

```bash
# Opção A: Elastic Beanstalk (mais fácil)
./scripts/aws_eb_deploy.sh

# OU

# Opção B: EC2 (mais barato)
./scripts/aws_ec2_deploy.sh
```

---

## 🎯 Resumo Ultra-Rápido

```bash
# 1. Criar conta
open https://aws.amazon.com/free/

# 2. Criar IAM user e obter keys
open https://console.aws.amazon.com/iam/
# Users → Add user → Copiar Access Keys

# 3. Configurar
aws configure
# Cole: Access Key ID
# Cole: Secret Access Key
# Digite: us-east-1
# Digite: json

# 4. Testar
aws sts get-caller-identity

# 5. Deploy!
./scripts/aws_eb_deploy.sh
```

---

## 🔗 Links Diretos

| Ação | Link |
|------|------|
| **Criar conta** | <https://aws.amazon.com/free/> |
| **Console IAM** | <https://console.aws.amazon.com/iam/> |
| **Criar IAM User** | <https://console.aws.amazon.com/iam/#/users$new> |
| **Billing/Custos** | <https://console.aws.amazon.com/billing/> |

---

## ⚠️ Problemas Comuns

### "Unable to locate credentials"

```bash
# Reconfigurar
aws configure
```

### "Access Denied"

**Problema**: Faltam permissões

**Solução**: Adicione política `AdministratorAccess` ao usuário IAM

### Esqueci de salvar Secret Key

**Solução**: Crie uma nova access key

1. IAM → Users → Seu usuário
2. Security credentials
3. Create access key
4. Salve desta vez! 😅

---

## 📚 Guia Completo

Para detalhes completos, veja: [AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)

---

## 💡 Dicas

- ✅ **Salve** as credenciais em gerenciador de senhas
- ✅ **Ative MFA** para segurança extra
- ✅ **Configure alerta** de custos ($10)
- ✅ **Use Free Tier** primeiro ano grátis!
- ❌ **NUNCA** compartilhe suas keys
- ❌ **NUNCA** comite no Git

---

**Agora é só fazer deploy! 🚀**

```bash
cd /home/rootkit/Apps/xPages/client_manager
./scripts/aws_eb_deploy.sh
```
