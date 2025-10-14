# Mapeamento de Pagamentos Heleket (Cripto)

> Última atualização: 2025-10-15
>
> Objetivo: identificar quais dados de `clients` já suportam a criação de pagamentos Heleket (gateway cripto), definir a estrutura de payouts baseada em ativos digitais e destacar lacunas antes da implementação.

## Inventário Atual

| Origem | Campo | Uso na Integração | Observações |
|--------|-------|-------------------|-------------|
| `clients` | `_id` | `beneficiary_id` / chave primária de relacionamento | Gravar como string na coleção de pagamentos.
| `clients` | `username` | Identificador exibido para administradores | Não atende requisitos legais — falta nome completo.
| `clients` | `email` (quando presente) | Contato para confirmações | Campo opcional; não padronizado.
| `clients` | `status` | Bloquear pagamentos para clientes inativos | Hoje aceita `active`/`inactive`.
| `clients` | `plan_id` | Determinar regras de negócio por plano | Usar para aplicar limites de valor/recorrência.
| `clients` | `createdAt`, `updatedAt` | Auditoria mínima do lifecycle | Pode preencher metadados de criação do pagamento.
| `plans` | `_id`, `name`, `price`, `duration_days` | Feed para cálculo de valores e cadência de pagamento | Necessário ao definir pagamentos recorrentes.
| `audit_logs` | `entity_type="client"` | Registro de ações administrativas | Apoia trilha de auditoria dos pagamentos.

## Estrutura Sugerida

### 1. `client_wallet_profile`

Coleção (ou subdocumento em `clients`) responsável por armazenar dados de recebimento cripto do beneficiário:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `client_id` | ObjectId | Sim | Referência ao cliente.
| `display_name` | string | Sim | Nome que será exibido para conferência.
| `preferred_asset` | string | Sim | Moeda digital (`USDT`, `BTC`, etc.).
| `network` | string | Sim | Rede suportada pelo Heleket (`TRON`, `ETH`, etc.).
| `wallet_address` | string | Sim | Endereço para saque cripto.
| `memo_tag` | string | Não | Tag/Memo quando a rede exigir (ex.: XRP, XLM).
| `metadata` | dict | Não | Campos adicionais (ex.: limite diário, contato).
| `status` | enum | Sim | `active`, `blocked`, `archived`.
| `createdAt`/`updatedAt` | datetime | Sim | Auditoria.

### 2. `client_crypto_payouts`

Coleção responsável por registrar solicitações enviadas ao Heleket:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `_id` | ObjectId | Identificador interno.
| `client_id` | ObjectId | Relacionamento direto com `clients`.
| `wallet_profile_id` | ObjectId | Perfil de carteira usado (pode ser nulo se inline).
| `heleket_transaction_id` | string | ID retornado pela API Heleket.
| `status` | enum | `pending`, `broadcast`, `confirmed`, `failed`, `cancelled`.
| `asset` | string | Moeda digital enviada.
| `amount` | decimal | Quantidade transferida.
| `network` | string | Rede blockchain utilizada.
| `origin` | enum | `manual`, `scheduled`, `bonus`.
| `trigger_metadata` | dict | Informações sobre a origem do pagamento (plano, campanha, etc.).
| `idempotency_key` | string | Gerado a partir de `client_id` + timestamp + `asset`.
| `requestedAt` | datetime | Quando o pagamento foi criado no sistema.
| `confirmedAt` | datetime | Quando Heleket sinalizou confirmação on-chain.
| `heleketPayload` | dict | Snapshot sanitizado do payload enviado.
| `responseLogs` | list | Histórico de callbacks e atualizações de status.
| `createdBy` | ObjectId | Admin responsável (quando manual).

## Gatilhos Propostos (Somente Clientes)

1. **Manual via painel do cliente**  
   - Adicionar botão "Gerar pagamento" na página detalhada de `client`.  
   - Pré-validar se existe `client_wallet_profile` ativo e se regras do plano permitem.
2. **Rotina agendada por plano**  
   - Job diário busca clientes com planos elegíveis (`plan_id` + `status == "active"`).  
   - Calcula `amount` com base em regras por plano (ex.: comissão fixa ou percentual).
3. **Bônus de ativação**  
   - Ao chamar `Client.create` ou `Client.update` com mudança de plano para tier premium, enfileira pagamento inicial.

## Lacunas Identificadas

| Requisito | Impacto | Ação Sugerida |
|-----------|---------|---------------|
| Carteira cripto não cadastrada em `clients` | Sem endereço não é possível iniciar payouts. | Implementar `client_wallet_profile` conforme tabela acima.
| Definição de ativo/rede por plano | Necessário para automatizar payouts. | Documentar regra de seleção (`USDT-TRON` por padrão, exceções por plano?).
| Política de cálculo de montante | Não há métrica consolidada. | Definir regra por plano (valor fixo, percentual, minimo/máximo).
| Rastreamento on-chain | Falta trilha para reconciliação. | Persistir hash da transação na coleção `client_crypto_payouts` e armazenar callbacks.
| Idempotência | Risco de duplicidade em reenvios. | Gerar chave determinística (`client_id + asset + ISO8601`).

## Próximos Passos

1. Validar o desenho das coleções (`client_wallet_profile`, `client_crypto_payouts`) com Produto e Compliance.
2. Definir esquema de cálculo de valor por plano (documentar no backlog Sprint 1).
3. Atualizar backlog para incluir criação de formulário/admin UI para perfis de carteira cripto.
4. Planejar migração inicial para cadastrar carteiras de clientes existentes.

### Agenda sugerida para alinhamento com Produto/Compliance

| Tópico | Objetivo | Perguntas-chave |
|--------|----------|-----------------|
| Escopo de planos | Confirmar quais planos geram pagamento Heleket | Quais planos atuais distribuem recompensas cripto? Existe sazonalidade? |
| Ativos e redes suportados | Garantir compatibilidade com Heleket | Quais moedas e redes estão habilitadas? Há limites por ativo? |
| Gestão de carteiras | Definir responsabilidades | Quem cadastra/valida endereços? Há verificação automática (test transfer)? |
| Política de valor | Definir fórmula de cálculo | Valor fixo por plano? Percentual sobre vendas? Existe mínimo/máximo por período? |
| Idempotência e auditoria | Evitar duplicidade e atender compliance | Como registrar hashes on-chain? Precisamos armazenar recibos do Heleket? |
| SLA e notificações | Alinhar expectativas operacionais | Quem é acionado em falhas? Qual canal de comunicação (email, Slack)? |

> Preparar respostas preliminares antes da reunião e anexar logs de decisões conforme avanço das sprints.

---

_Este documento será atualizado novamente após a implementação do cliente Heleket e dos serviços de pagamento._

