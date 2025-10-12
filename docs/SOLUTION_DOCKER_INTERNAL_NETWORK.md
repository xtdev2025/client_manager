# 🎯 Solução: Rede Interna do Docker para CI/CD

## 📋 Resumo Executivo

**Problema**: O workflow de CI/CD com `act` falhava porque tentava expor MongoDB na porta 27017, que já estava em uso pelo MongoDB local do desenvolvedor.

**Solução**: Configurar os services do GitHub Actions para usar a **rede interna do Docker**, sem expor portas no host.

**Resultado**: MongoDB e outros services ficam isolados na rede privada do container, acessíveis via hostname (ex: `mongodb:27017`), sem conflitos com serviços locais.

---

## 🐛 Problema Original

```bash
[Tests/test] failed to start container: Error response from daemon: 
failed to set up container networking: driver failed programming 
external connectivity on endpoint [...]: failed to bind host port 
for 0.0.0.0:27017:172.21.0.2:27017/tcp: address already in use
```

**Causa**:
- O workflow tinha `ports: - 27017:27017` no service MongoDB
- Isso tentava expor a porta 27017 do container no host
- Conflitava com o MongoDB local rodando na mesma porta

---

## ✅ Solução Implementada

### 1. Remover Exposição de Portas

**ANTES** (❌ Conflito):
```yaml
services:
  mongodb:
    image: mongo:5.0
    ports:
      - 27017:27017  # ❌ Expõe no host
```

**DEPOIS** (✅ Rede interna):
```yaml
services:
  mongodb:
    image: mongo:5.0
    # Sem ports - usa rede interna do Docker
    # Acessível via hostname 'mongodb' dentro dos containers
```

### 2. Usar Hostname ao invés de localhost

**ANTES** (❌):
```yaml
- name: Verify MongoDB connection
  run: |
    mongosh localhost:27017  # ❌ Tenta host local
```

**DEPOIS** (✅):
```yaml
- name: Verify MongoDB connection
  run: |
    mongosh mongodb:27017  # ✅ Usa hostname do container
```

### 3. Atualizar Todas as Referências

**Mudanças aplicadas em 6 lugares**:

1. ✅ Verify MongoDB connection: `localhost` → `mongodb`
2. ✅ Create .env: `MONGO_URI=mongodb://localhost` → `mongodb://mongodb`
3. ✅ Initialize test database: `localhost:27017` → `mongodb:27017`
4. ✅ Run tests: `MONGO_URI: mongodb://localhost` → `mongodb://mongodb`
5. ✅ Cleanup: `'mongodb://localhost:27017/'` → `'mongodb://mongodb:27017/'`
6. ✅ Service definition: removido `ports: - 27017:27017`

---

## 🎉 Benefícios

### 1. Sem Conflitos de Porta
- MongoDB do CI/CD não tenta usar porta 27017 do host
- Desenvolvedor pode manter MongoDB local rodando
- Pode rodar `act` localmente sem parar serviços

### 2. Isolamento
- Services do CI/CD ficam isolados na rede privada do Docker
- Não há "vazamento" de serviços para o host
- Melhor segurança

### 3. Portabilidade
- Funciona igualmente no GitHub Actions e localmente com `act`
- Não depende de configuração do host
- Comportamento consistente

### 4. Simplicidade
- Não precisa parar/reiniciar serviços locais
- Não precisa configurar portas alternativas
- "Just works" ✨

---

## 🏗️ Como Funciona

```
┌─────────────────────────────────────────────────┐
│          GitHub Actions Runner (ubuntu-latest)  │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  Job Container                          │    │
│  │                                          │    │
│  │  - Código da aplicação                   │    │
│  │  - Pytest                                │    │
│  │  - Conecta: mongodb:27017               │    │
│  └────────────────────────────────────────┘    │
│             │                                    │
│             │ (rede interna do Docker)           │
│             ↓                                    │
│  ┌────────────────────────────────────────┐    │
│  │  Service Container: MongoDB            │    │
│  │                                          │    │
│  │  - Image: mongo:5.0                     │    │
│  │  - Hostname: mongodb                    │    │
│  │  - Porta interna: 27017                 │    │
│  │  - NÃO exposto no host                  │    │
│  └────────────────────────────────────────┘    │
│                                                  │
└─────────────────────────────────────────────────┘

Host (desenvolvedor):
├─ MongoDB local: 127.0.0.1:27017 ✅ (sem conflito!)
└─ act rodando containers acima ✅ (isolados!)
```

---

## 🧪 Como Testar

### Opção 1: Localmente com act (RECOMENDADO)

```bash
# Agora funciona sem parar serviços!
cd /home/rootkit/Apps/xPages/client_manager
act -j test --container-architecture linux/amd64

# MongoDB local continua rodando
sudo systemctl status mongod  # ✅ Active (running)
```

### Opção 2: GitHub Actions

```bash
# Push automático dispara workflow
git push origin main

# Monitorar em:
https://github.com/rootkitoriginal/client_manager/actions
```

### Opção 3: Manual

```bash
# Testes locais tradicionais (usa MongoDB local)
pytest tests/ -v --cov=app
```

---

## 📊 Comparação

| Aspecto | ANTES (localhost) | DEPOIS (hostname) |
|---------|-------------------|-------------------|
| **Exposição de porta** | ✅ Sim (27017:27017) | ❌ Não (rede interna) |
| **Conflito com local** | ❌ Sim (falha se porta ocupada) | ✅ Não (isolado) |
| **Precisa parar serviços** | ❌ Sim (stop mongod) | ✅ Não |
| **Funciona com act** | ❌ Não (porta ocupada) | ✅ Sim |
| **Segurança** | ⚠️ Service exposto | ✅ Isolado |
| **Portabilidade** | ⚠️ Depende do host | ✅ Consistente |

---

## 🔗 Referências

- [GitHub Actions - Service Containers](https://docs.github.com/en/actions/using-containerized-services/about-service-containers)
- [Docker Networking](https://docs.docker.com/network/)
- [MongoDB Connection Strings](https://www.mongodb.com/docs/manual/reference/connection-string/)

---

## 📝 Commits Relacionados

- **15003a1**: `fix(ci): use Docker internal network for MongoDB`
  - Remove port exposure (27017:27017)
  - Use hostname 'mongodb' instead of 'localhost'
  - Prevents conflict with local MongoDB

---

## 💡 Lições Aprendidas

1. **Services do GitHub Actions não precisam expor portas no host**
   - Use hostnames diretamente (`mongodb`, `redis`, `postgres`)
   - Reserve `ports:` apenas quando realmente precisar expor

2. **Rede interna do Docker é suficiente para CI/CD**
   - Containers podem se comunicar via hostnames
   - Isolamento = menos conflitos + mais segurança

3. **`act` funciona melhor com rede interna**
   - Não precisa "preparar ambiente" antes
   - Mais parecido com GitHub Actions real

4. **Sempre prefira isolamento**
   - CI/CD não deve interferir com ambiente de desenvolvimento
   - Containers devem ser auto-suficientes

---

**Data**: 12 de outubro de 2025  
**Autor**: Sistema xPages  
**Status**: ✅ Implementado e testado
