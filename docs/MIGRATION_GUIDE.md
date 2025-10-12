# 🔄 Guia de Migração - Shell para Python

**Para usuários que já usavam os scripts shell (.sh)**

---

## ⚡ Mudanças Rápidas

### Comandos Atualizados

| Comando Antigo | Comando Novo | Funcionalidade |
|---------------|--------------|----------------|
| `./startup.sh` | `python scripts/startup.py` | Inicialização produção |
| `./test-workflows.sh` | `python scripts/test_workflows.py` | Teste workflows |
| `./test-all-workflows.sh` | `python scripts/test_all_workflows.py` | Teste completo |
| `./scripts/azure_deploy.sh` | `python scripts/azure_deploy.py` | Deploy Azure |
| `./scripts/aws_eb_deploy.sh` | `python scripts/aws_eb_deploy.py` | Deploy AWS EB |
| `./scripts/aws_ec2_deploy.sh` | `python scripts/aws_ec2_deploy.py` | Deploy AWS EC2 |

---

## 🚀 Migração em 3 Passos

### 1. Atualizar Repositório
```bash
git pull origin main
```

### 2. Verificar Permissões
```bash
chmod +x scripts/*.py
```

### 3. Usar Novos Comandos
```bash
# Exemplo: Deploy Azure
python scripts/azure_deploy.py
```

---

## ✅ Vantagens da Migração

- 🌍 **Multiplataforma**: Funciona no Windows
- 🔧 **Melhor debug**: Mensagens de erro claras
- 📊 **Logs visuais**: Progresso com emojis
- 🛡️ **Mais robusto**: Tratamento de erros melhorado

---

## 🆘 Problemas Comuns

### "python: command not found"
```bash
# Use python3 em sistemas mais antigos
python3 scripts/azure_deploy.py
```

### "Permission denied"
```bash
# Torne o script executável
chmod +x scripts/azure_deploy.py
./scripts/azure_deploy.py
```

### Scripts não funcionam no Windows
```bash
# Use explicitamente o python
python scripts/azure_deploy.py
```

---

## 📚 Documentação

- **Scripts**: [docs/SCRIPTS_DOCUMENTATION.md](docs/SCRIPTS_DOCUMENTATION.md)
- **Migração Técnica**: [docs/MIGRATION_SHELL_TO_PYTHON.md](docs/MIGRATION_SHELL_TO_PYTHON.md)
- **Resumo**: [MODERNIZATION_SUMMARY.md](MODERNIZATION_SUMMARY.md)

---

## 🤝 Suporte

**Problemas?** Abra uma [issue no GitHub](https://github.com/rootkitoriginal/client_manager/issues)

**Dúvidas?** Consulte a [documentação completa](docs/)

---

<div align="center">

**✅ Migração Simples e Rápida**

**Mesma funcionalidade, melhor experiência**

</div>