# Deployment Playbook

> Atualizado em 14/10/2025 para refletir a integração Heleket.

## 1. Variáveis de ambiente críticas

As credenciais e endpoints Heleket devem ser mantidos fora do repositório. Crie o arquivo `/etc/client-manager/env` (referenciado em `deploy/xpages.service`) com:

```ini
HELEKET_PROJECT_URL=https://api.heleket.sandbox
HELEKET_MERCHANT_ID=seu-merchant-id
HELEKET_API_KEY=chave-api
HELEKET_WEBHOOK_SECRET=segredo-webhook
```

Sempre que um segredo for rotacionado:

1. Atualize o valor correspondente no cofre (ex.: AWS Secrets Manager ou Parameter Store).
2. Atualize `/etc/client-manager/env` no host (`sudo nano /etc/client-manager/env`).
3. Execute `sudo systemctl daemon-reload && sudo systemctl restart xpages.service`.
4. Valide o novo segredo executando o health-check: `curl -fsS http://localhost:5000/payouts/webhook/health`.

> Sugestão: automatize a etapa 2 com `aws secretsmanager get-secret-value` e um script de atualização para reduzir erros manuais.

## 2. Docker Compose (ambiente local/staging)

O serviço `app` agora exporta as mesmas variáveis Heleket. Defina-as em um `.env` local ou exporte-as antes de subir o stack:

```bash
export HELEKET_PROJECT_URL=https://api.heleket.sandbox
export HELEKET_MERCHANT_ID=dev-merchant
export HELEKET_API_KEY=dev-api-key
export HELEKET_WEBHOOK_SECRET=dev-webhook-secret
docker compose up --build
```

O health-check do container executa duas sondagens:

- `GET /health` — status geral da aplicação.
- `GET /payouts/webhook/health` — confirma presença do `HELEKET_WEBHOOK_SECRET`.

## 3. Checklist pós-deploy

1. `curl -fsS http://localhost:5000/health`
2. `curl -fsS http://localhost:5000/payouts/webhook/health`
3. Disparar um payout manual de teste (sandbox) e confirmar auditoria.
4. Verificar logs do serviço: `journalctl -u xpages.service -n 200 -f`.

Se qualquer chamada de health retornar código diferente de 200, revise as credenciais e reinicie o serviço.
