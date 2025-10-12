# 🔑 Como Obter Credenciais AWS (Access Keys)

Guia completo para criar e configurar suas credenciais AWS.

## 📋 Índice

1. [Criar Conta AWS](#1-criar-conta-aws)
2. [Obter Access Keys](#2-obter-access-keys)
3. [Configurar AWS CLI](#3-configurar-aws-cli)
4. [Testar Configuração](#4-testar-configuração)
5. [Segurança e Boas Práticas](#5-segurança-e-boas-práticas)

---

## 1. 🆕 Criar Conta AWS

### Se você ainda não tem conta AWS

1. **Acesse**: <https://aws.amazon.com/free/>

2. **Clique em**: "Criar uma conta gratuita" / "Create a Free Account"

3. **Preencha os dados**:
   - Email
   - Senha
   - Nome da conta AWS

4. **Adicione informações de contato**:
   - Tipo de conta: Pessoal ou Empresa
   - Nome completo
   - Telefone
   - Endereço

5. **Adicione cartão de crédito**:
   - É necessário para verificação
   - Você NÃO será cobrado no Free Tier
   - AWS pode fazer cobrança de $1 (estorno automático)

6. **Verificação de identidade**:
   - Escolha: SMS ou Chamada telefônica
   - Insira o código recebido

7. **Escolha plano de suporte**:
   - Selecione: **"Basic Support - Free"**

8. **Pronto!** ✅
   - Aguarde alguns minutos para ativação
   - Você receberá email de confirmação

---

## 2. 🔑 Obter Access Keys

### Método 1: IAM User (Recomendado para desenvolvimento)

#### Passo 1: Fazer login no Console AWS

1. Acesse: <https://console.aws.amazon.com/>
2. Faça login com seu email e senha

#### Passo 2: Acessar IAM (Identity and Access Management)

1. No topo da página, na barra de busca, digite: **IAM**
2. Clique em **IAM** (Identity and Access Management)

   ![IAM Console](https://docs.aws.amazon.com/images/IAM/latest/UserGuide/images/console-home.png)

#### Passo 3: Criar Usuário IAM

1. No menu lateral esquerdo, clique em **"Users"** (Usuários)
2. Clique no botão **"Add users"** (Adicionar usuários)
3. Configure o usuário:

   **Nome do usuário**: `client-manager-dev` (ou seu nome preferido)

   **Access type** (Tipo de acesso):
   - ☑️ Marque: **"Access key - Programmatic access"**
   - ☐ NÃO marque: "Password - AWS Management Console access" (a menos que queira login no console também)

4. Clique em **"Next: Permissions"**

#### Passo 4: Definir Permissões

Escolha uma das opções:

**Opção A: Para testes/desenvolvimento (Permissões amplas)**

1. Clique em **"Attach existing policies directly"**
2. Na busca, digite: **AdministratorAccess**
3. Marque a checkbox ☑️ **AdministratorAccess**

   ⚠️ **ATENÇÃO**: Isso dá acesso total! Use apenas para desenvolvimento/testes.

**Opção B: Para produção (Permissões restritas)** - RECOMENDADO

1. Clique em **"Attach existing policies directly"**
2. Selecione as políticas necessárias:
   - ☑️ **AmazonEC2FullAccess** (para criar instâncias)
   - ☑️ **AWSElasticBeanstalkFullAccess** (para Elastic Beanstalk)
   - ☑️ **IAMReadOnlyAccess** (para gerenciar permissões)
   - ☑️ **AmazonS3FullAccess** (para armazenamento)

3. Clique em **"Next: Tags"**

#### Passo 5: Adicionar Tags (Opcional)

1. Você pode pular ou adicionar tags como:
   - Key: `Project`, Value: `ClientManager`
   - Key: `Environment`, Value: `Development`

2. Clique em **"Next: Review"**

#### Passo 6: Revisar e Criar

1. Revise as informações
2. Clique em **"Create user"**

#### Passo 7: SALVAR AS CREDENCIAIS! ⚠️

**IMPORTANTE**: Esta é a ÚNICA vez que você verá a Secret Access Key!

Você verá uma tela com:

```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Salve essas informações de uma destas formas**:

1. **Clique em "Download .csv"** - Salva um arquivo CSV com as credenciais
2. **Copie e cole** em um local seguro (gerenciador de senhas)
3. **NUNCA** compartilhe essas chaves publicamente!

---

### Método 2: Root User Access Keys (NÃO Recomendado)

⚠️ **AWS NÃO recomenda usar credenciais do root user!**

Mas se for apenas para teste rápido:

1. Faça login como root user
2. Clique no seu nome no canto superior direito
3. Selecione **"Security credentials"**
4. Role até **"Access keys"**
5. Clique em **"Create access key"**
6. Selecione caso de uso: **CLI**
7. Marque: "I understand the above recommendation"
8. Clique em **"Create access key"**
9. **SALVE** as credenciais!

---

## 3. ⚙️ Configurar AWS CLI

### Instalar AWS CLI (se ainda não tem)

**Linux/Ubuntu**:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar instalação
aws --version
```

**macOS**:

```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verificar
aws --version
```

**Windows**:

1. Download: <https://awscli.amazonaws.com/AWSCLIV2.msi>
2. Execute o instalador
3. Abra PowerShell e teste: `aws --version`

### Configurar Credenciais

```bash
aws configure
```

Você será solicitado a inserir:

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

**Regiões AWS Comuns**:

- `us-east-1` - Norte da Virgínia (mais comum, mais barato)
- `us-east-2` - Ohio
- `us-west-1` - Califórnia Norte
- `us-west-2` - Oregon
- `sa-east-1` - São Paulo, Brasil 🇧🇷
- `eu-west-1` - Irlanda

**Output Formats**:

- `json` - Recomendado (padrão)
- `yaml`
- `text`
- `table`

### Configuração Manual (Alternativa)

Se preferir configurar manualmente:

```bash
# Criar arquivo de credenciais
mkdir -p ~/.aws
nano ~/.aws/credentials
```

Adicione:

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Criar arquivo de config:

```bash
nano ~/.aws/config
```

Adicione:

```ini
[default]
region = us-east-1
output = json
```

---

## 4. ✅ Testar Configuração

### Teste 1: Verificar Identidade

```bash
aws sts get-caller-identity
```

Deve retornar algo como:

```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/client-manager-dev"
}
```

### Teste 2: Listar Regiões

```bash
aws ec2 describe-regions --output table
```

### Teste 3: Listar Buckets S3

```bash
aws s3 ls
```

Se tudo funcionar, você está pronto! ✅

---

## 5. 🔒 Segurança e Boas Práticas

### ⚠️ NUNCA Faça Isso

- ❌ Não compartilhe suas Access Keys
- ❌ Não comite credenciais no Git
- ❌ Não poste em fóruns/chat
- ❌ Não use em código-fonte
- ❌ Não envie por email/WhatsApp

### ✅ Sempre Faça Isso

- ✅ Use IAM Users (não root user)
- ✅ Ative MFA (Multi-Factor Authentication)
- ✅ Use políticas com menor privilégio
- ✅ Rotacione credenciais regularmente
- ✅ Delete keys não utilizadas
- ✅ Use AWS Secrets Manager para produção
- ✅ Monitore uso com AWS CloudTrail

### Habilitar MFA (Recomendado)

1. Acesse IAM Console
2. Selecione seu usuário
3. Aba **"Security credentials"**
4. Em **"Multi-factor authentication (MFA)"**, clique **"Assign MFA device"**
5. Use app como Google Authenticator ou Authy

### Rotacionar Access Keys

```bash
# Listar access keys atuais
aws iam list-access-keys --user-name client-manager-dev

# Criar nova key
aws iam create-access-key --user-name client-manager-dev

# Depois de testar a nova, deletar a antiga
aws iam delete-access-key --user-name client-manager-dev --access-key-id AKIAOLD...
```

### Verificar Custos

1. Acesse: <https://console.aws.amazon.com/billing/>
2. Configure **"Billing Alerts"**
3. Crie alerta para quando passar $10

---

## 🆘 Problemas Comuns

### "Unable to locate credentials"

**Solução**:

```bash
# Verificar se arquivo existe
cat ~/.aws/credentials

# Reconfigurar
aws configure
```

### "An error occurred (UnauthorizedOperation)"

**Problema**: Usuário não tem permissões necessárias

**Solução**:

1. Acesse IAM Console
2. Adicione políticas necessárias ao usuário

### "The security token included in the request is invalid"

**Problema**: Credenciais inválidas ou expiradas

**Solução**:

```bash
# Obter novas credenciais e reconfigurar
aws configure
```

### Esqueci de salvar Secret Access Key

**Solução**: Você precisa criar uma nova access key

```bash
# Via CLI
aws iam create-access-key --user-name SEU_USUARIO

# Ou via Console:
# IAM → Users → Seu usuário → Security credentials → Create access key
```

---

## 📝 Resumo Rápido

1. **Criar conta**: <https://aws.amazon.com/free/>
2. **Criar IAM User**: Console → IAM → Users → Add user
3. **Salvar credenciais**: Download CSV ou copiar
4. **Configurar CLI**: `aws configure`
5. **Testar**: `aws sts get-caller-identity`
6. **Deploy!**: `./scripts/aws_eb_deploy.sh`

---

## 🔗 Links Úteis

- [AWS Free Tier](https://aws.amazon.com/free/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS Regions](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/)
- [AWS Pricing Calculator](https://calculator.aws/)

---

**Agora você está pronto para fazer deploy na AWS! 🚀**
