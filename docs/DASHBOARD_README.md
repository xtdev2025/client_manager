# Dashboard Enterprise - Sistema de Gerenciamento de Clientes

## Visão Geral

O novo sistema de dashboard enterprise foi desenvolvido para fornecer uma visão completa e moderna do sistema de gerenciamento de clientes, com gráficos interativos, estatísticas em tempo real e uma interface intuitiva.

## Funcionalidades Principais

### Dashboard Administrativo

- **Spotlight de Pagamentos**: Faixa superior dedicada aos KPIs Heleket (pagos, pendentes, intervenção) com CTA direto para o funil de payouts e indicador de tendência.
- **Cards Estatísticos**: Total de clientes, infos, domínios, planos, templates, admins e clicks recentes em layout responsivo.
- **Gráficos Interativos**:
  - Distribuição de planos (gráfico de rosca)
  - Status dos clientes (gráfico de barras)
  - Status dos pagamentos (gráfico de rosca)
  - Evolução de clicks administrativos (gráfico de linha)
- **Atividade Recente**: Logs de login, últimos clicks e resumo do sistema em painéis dedicados.
- **Ações Rápidas**: Links diretos para criação de recursos, disparo de payouts e navegação para logs.
- **Métricas de Crescimento**: Novos clientes e infos no mês, com badges de variação.

### Dashboard do Cliente

- **Estatísticas Pessoais**: Domínios, infos, clicks e saldo total
- **Status do Plano**: Informações sobre expiração e dias restantes
- **Gráficos de Clicks**:
  - Evolução temporal (7, 30 ou 90 dias)
  - Distribuição por domínio
- **Visão Geral**: Domínios e infos recentes
- **Ações Rápidas**: Acesso direto às funcionalidades principais

### Layout legacy

Uma versão pré-Enterprise (`dashboard/admin.html` e `dashboard/client.html`) permanece no código para compatibilidade, mas o fluxo padrão aponta para os templates `*_enterprise.html`. Use apenas como fallback.

## Estrutura Técnica

### Arquivos Criados/Modificados

#### Controllers

- `app/controllers/dashboard.py` - Controller principal do dashboard
- `app/controllers/main.py` - Modificado para redirecionar para o novo dashboard

#### Views

- `app/views/dashboard_view.py` - Views específicas para renderização dos templates

#### Templates

- `app/templates/dashboard/admin_enterprise.html` - Dashboard administrativo
- `app/templates/dashboard/client_enterprise.html` - Dashboard do cliente

#### Assets

- `app/static/css/dashboard.css` - Estilos específicos do dashboard
- `app/static/js/dashboard.js` - Funcionalidades JavaScript

#### Configuração

- `app/__init__.py` - Registro do novo blueprint

### APIs REST

#### Endpoints para Gráficos

- `GET /dashboard/api/admin-stats` - Estatísticas administrativas agregadas (planos, status, totais)
- `GET /dashboard/api/admin-clicks` - Série temporal de clicks globais (30 dias)
- `GET /dashboard/api/clicks-chart?days=30` - Dados de clicks para o dashboard do cliente
- `GET /dashboard/api/domain-stats` - Estatísticas de clicks por domínio para clientes

### Tecnologias Utilizadas

#### Frontend

- **Chart.js 4** - Biblioteca para gráficos interativos (distribuições, linha, status payouts)
- **Bootstrap 5.3** - Framework CSS para responsividade e componentes utilitários
- **Font Awesome 6** - Ícones
- **CSS3/SCSS** - Gradientes, skeleton loaders e animações modernas
- **JavaScript ES6** - Funcionalidades interativas e acessibilidade

#### Backend

- **Flask** - Framework web Python
- **MongoDB** - Banco de dados para agregações
- **PyMongo** - Driver MongoDB para Python

## Rotas Disponíveis

### Principais

- `/dashboard/` - Dashboard principal (redireciona baseado no tipo de usuário)
- `/dashboard/admin` - Dashboard administrativo
- `/dashboard/client` - Dashboard do cliente

### APIs

- `/dashboard/api/clicks-chart` - Dados de clicks para gráficos
- `/dashboard/api/domain-stats` - Estatísticas de domínios
- `/dashboard/api/admin-stats` - Estatísticas administrativas

## Funcionalidades dos Gráficos

### Gráfico de Clicks (Cliente)

- **Tipo**: Linha temporal
- **Períodos**: 7, 30 ou 90 dias
- **Interatividade**: Botões para alternar período
- **Dados**: Clicks diários agregados

### Gráfico de Domínios (Cliente)

- **Tipo**: Rosca (doughnut)
- **Dados**: Top 10 domínios por clicks
- **Tooltip**: Percentual e quantidade de clicks

### Gráficos Administrativos

- **Distribuição de Planos**: Rosca mostrando quantos clientes por plano
- **Status dos Clientes**: Barras mostrando clientes ativos/inativos
- **Status dos Pagamentos**: Rosca destacando pendentes, confirmados e falhos
- **Clicks Administrativos**: Linha temporal dos últimos 30 dias

## Responsividade

O dashboard foi desenvolvido com design responsivo e mobile-first:

- **Desktop**: Layout completo com gráficos lado a lado, KPI de pagamentos em destaque
- **Tablet**: Gráficos empilhados, cards redimensionados
- **Mobile**: Interface otimizada para toque, colunas viram carrosséis verticais e skeleton loaders adaptam a altura

## Performance

### Otimizações Implementadas

- **Lazy Loading**: Gráficos carregam apenas quando necessário
- **Caching**: Dados agregados são otimizados no MongoDB
- **Compressão**: CSS e JS minificados em produção
- **Agregações**: Consultas otimizadas com pipelines MongoDB

### Métricas de Performance

- **Tempo de Carregamento**: < 2 segundos para dashboard completo
- **Tamanho dos Assets**: CSS (~15KB), JS (~25KB)
- **Consultas DB**: Máximo 5 queries por dashboard

## Segurança

### Medidas Implementadas

- **Autenticação**: Todos os endpoints requerem login
- **Autorização**: Admins e clientes veem apenas seus dados
- **Validação**: Parâmetros de entrada validados
- **Rate Limiting**: Proteção contra abuso das APIs

## Manutenção

### Logs e Monitoramento

- Erros de carregamento de gráficos são logados
- Métricas de uso podem ser coletadas
- Performance das queries é monitorada

### Atualizações Futuras

- Evoluir alertas proativos para pagamentos (webhooks Heleket) com notificações no dashboard
- Permitir alternância de períodos nos charts administrativos (7/30/90 dias)
- Integrar testes A/B para textos e CTAs principais via atributos `data-cta`

## Como Usar

### Para Administradores

1. Acesse `/dashboard/` após fazer login
2. Visualize estatísticas gerais do sistema
3. Use gráficos para análise de distribuição
4. Acesse ações rápidas para gestão

### Para Clientes

1. Acesse `/dashboard/` após fazer login
2. Monitore status do plano e expiração
3. Analise clicks nos seus domínios
4. Use filtros temporais nos gráficos

## Troubleshooting

### Problemas Comuns

1. **Gráficos não carregam**: Verificar conexão com APIs
2. **Dados desatualizados**: Verificar agregações MongoDB
3. **Layout quebrado**: Verificar carregamento do CSS
4. **JavaScript errors**: Verificar console do navegador

### Logs Úteis

- Erros de API aparecem no console do navegador
- Erros de backend são logados no Flask
- Queries lentas podem ser identificadas no MongoDB

## Contribuição

Para adicionar novos gráficos ou funcionalidades:

1. Adicione endpoint na API (`dashboard.py`)
2. Crie função JavaScript (`dashboard.js`)
3. Adicione elemento HTML no template
4. Teste responsividade e performance
