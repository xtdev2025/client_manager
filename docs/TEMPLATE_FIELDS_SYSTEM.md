# Sistema de Templates

## Visão Geral

O sistema de templates do Client Manager permite criar e gerenciar páginas personalizadas para clientes. Cada template possui páginas com conteúdo HTML personalizado que **antes** podia ser acessado publicamente via URLs amigáveis.

> ⚠️ **Importante:** A partir de outubro de 2025 as rotas públicas de template e o fluxo de submissão associado foram descontinuados. Este documento mantém as referências apenas para histórico e eventual reimplementação.

## Funcionalidades Implementadas

### 1. **Campo Slug** ✅

- Cada template possui um `slug` único gerado automaticamente a partir do nome
- Exemplo: "Basic Template" → "basic_template"
- O slug é usado nas URLs públicas para acessar as páginas
- Se o slug já existir, um sufixo numérico é adicionado automaticamente

### 2. **Páginas Personalizadas** ✅

Cada template contém uma ou mais páginas com:

- **ID único**: identificador da página (ex: 'home', 'login', 'contact')
- **Nome**: nome descritivo da página
- **Tipo**: categoria da página (home, login, form, etc)
- **Conteúdo HTML**: HTML personalizado para renderização
- **Ordem**: ordem de exibição das páginas

### 3. **Rotas Públicas** *(removidas)*

As rotas públicas `GET /template/<slug>/<page_id>` e `POST /template/<slug>/<page_id>/submit` foram descontinuadas. Os exemplos e instruções anteriores foram mantidos apenas como referência histórica.

### 4. **Templates Públicos Responsivos** *(removidos)*

O conjunto de templates voltados para visualização pública não faz mais parte da aplicação.

### 5. **Auditoria de Acessos** *(ajustada)*

O serviço de auditoria continua disponível para rotas internas. Logs específicos das páginas públicas foram desativados com a remoção das rotas.

## Estrutura de Dados

### Template

```json
{
  "_id": ObjectId("..."),
  "name": "Basic Template",
  "slug": "basic_template",
  "description": "Template básico para websites",
  "status": "active",
  "pages": [
    {
      "id": "home",
      "name": "Home",
      "type": "home",
      "content": "<h1>Bem-vindo</h1><p>Conteúdo da página inicial</p>",
      "order": 1
    },
    {
      "id": "login",
      "name": "Login",
      "type": "login",
      "content": "<form>...</form>",
      "order": 2
    }
  ],
  "createdAt": ISODate("..."),
  "updatedAt": ISODate("...")
}
```

### Página (Page)

```json
{
  "id": "login",
  "name": "Login",
  "type": "login",
  "content": "<div class='login-form'>...</div>",
  "order": 1
}
```

## Como Usar

### 1. Criar um Template (Admin)

1. Acesse `/templates/create`
2. Preencha nome e descrição
3. Salve o template
4. Um slug será gerado automaticamente

### 2. Editar Páginas do Template

1. Acesse `/templates/edit/<id>`
2. Vá para a seção de páginas
3. Adicione novas páginas ou edite existentes
4. Personalize o conteúdo HTML de cada página
5. Defina a ordem das páginas
6. Salve as alterações

### 3. Acessar Página Pública

> ℹ️ **Histórico:** As instruções abaixo descrevem o fluxo antigo de URLs públicas. Elas foram mantidas apenas como referência para equipes que precisam migrar integrações existentes.

- URL base anterior: `http://127.0.0.1:5000/template/<slug>/<page_id>`
- Endpoint de submissão anterior: `/template/<slug>/<page_id>/submit`

Ambos deixaram de existir na aplicação atual.

## Arquivos do Sistema

### Modelos

- ✅ `app/models/template.py` - Modelo de templates com slugs e operações CRUD

### Controllers

- ✅ `app/controllers/template.py` - Gerenciamento de templates (admin)
- ~~`app/controllers/public_template.py` - Rotas públicas para visualização~~ *(removido)*

### Views

- ✅ `app/views/template_view.py` - Views administrativas de templates

### Templates HTML

- ✅ `app/templates/templates/` - Interface administrativa
  - `list.html` - Listagem de templates
  - `create.html` - Criação de templates
  - `edit.html` - Edição de templates
  - `view.html` - Visualização de templates
- ✅ `app/templates/public/` - Templates públicos *(arquivos mantidos apenas como placeholder informativo)*
   - `template_page.html` - Mensagem informando descontinuação
   - `template_page_simple.html` - Mensagem informando descontinuação
   - `submit_success.html` - Mensagem informando descontinuação

### Services

- ✅ `app/services/audit_service.py` - Serviço de auditoria para logs

## Recursos de Segurança

- ✅ **Validação de Slug**: Slugs únicos gerados automaticamente
- ✅ **Escape de HTML**: Proteção contra XSS (quando necessário)
- ✅ **Auditoria**: Logs de todos os acessos públicos
- ✅ **Status Control**: Templates podem ser ativados/desativados

## Próximos Passos (Roadmap)

### Melhorias Planejadas

1. **Sistema de Campos Estruturados**
   - Campos predefinidos (login, password, CPF, phone, etc)
   - Drag-and-drop para reordenação
   - Validação automática de campos

2. **Armazenamento de Submissões**
   - Salvar dados submetidos no banco de dados
   - Painel de visualização de submissões
   - Exportação de dados (CSV, JSON)

3. **Notificações**
   - Email ao receber nova submissão
   - TELEGRAM/DISCORD para notificações urgentes
   - Webhooks para integrações

4. **Temas e Personalização**
   - Editor visual de templates
   - Biblioteca de temas predefinidos
   - Customização de cores e fontes
   - Upload de logo e imagens

5. **Analytics**
   - Dashboard de visualizações
   - Taxa de conversão de formulários
   - Tempo médio na página
   - Origem dos visitantes

6. **Preview e Versionamento**
   - Preview de páginas antes de publicar
   - Histórico de versões
   - Rollback de alterações

7. **Suporte a Header e Footer**
   - Header customizado por template
   - Footer customizado por template
   - CSS/JS customizado por dispositivo (mobile/desktop)

8. **Multi-idioma**
   - Suporte a múltiplos idiomas
   - Tradução de páginas
   - Detecção automática de idioma

## Testes

### Testar o Sistema Completo

1. **Criar template:**

   ```
   http://127.0.0.1:5000/templates/create
   ```

2. **Editar páginas:**

   ```
   http://127.0.0.1:5000/templates/edit/<id>
   ```

3. **Acessar página pública:** *(historicamente disponível)*

   `http://127.0.0.1:5000/template/<slug>/<page_id>`

4. **Verificar logs de auditoria:**
   - Verifique o banco de dados na collection `audit_logs`

### Exemplos de URLs Públicas *(histórico)*

```bash
# Template básico - página home (rotas removidas)
http://127.0.0.1:5000/template/basic_template/home

# Template profissional - página login (rotas removidas)
http://127.0.0.1:5000/template/professional_template/login

# Template e-commerce - página de contato (rotas removidas)
http://127.0.0.1:5000/template/ecommerce_template/contact
```

## Compatibilidade

- ✅ Totalmente compatível com estrutura atual
- ✅ Slugs gerados automaticamente para templates novos
- ✅ Sistema de páginas com conteúdo HTML personalizado
- ✅ Suporte a múltiplas páginas por template
- ~~✅ Páginas públicas acessíveis via URLs amigáveis~~ *(removido)*

## Suporte

Para questões ou problemas:

1. Verifique os logs da aplicação
2. Consulte o `README.md` principal
3. Verifique a documentação de arquitetura em `ARCHITECTURE.md`
