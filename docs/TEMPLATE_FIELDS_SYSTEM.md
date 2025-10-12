# Sistema de Templates

## Visão Geral

O sistema de templates do Client Manager permite criar e gerenciar páginas personalizadas para clientes. Cada template possui páginas com conteúdo HTML personalizado que pode ser acessado publicamente via URLs amigáveis.

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

### 3. **Rotas Públicas** ✅

O sistema expõe rotas públicas para acesso aos templates:

```
GET  /template/<slug>/<page_id>        # Visualizar página
POST /template/<slug>/<page_id>/submit # Submeter formulário
```

**Exemplos:**

```
http://127.0.0.1:5000/template/basic_template/home
http://127.0.0.1:5000/template/professional_template/login
http://127.0.0.1:5000/template/ecommerce/contact
```

### 4. **Templates Públicos Responsivos** ✅

- Página simplificada para renderização pública
- Suporte a HTML customizado
- Design responsivo
- Página de sucesso após submissão de formulários

### 5. **Auditoria de Acessos** ✅

- Registro de todas as visualizações de páginas
- Captura de IP do visitante
- Logs detalhados com timestamp
- Rastreamento de slug e page_id acessados

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

Copie a URL pública da página:

```
http://127.0.0.1:5000/template/<slug>/<page_id>
```

Substitua:

- `<slug>` pelo slug do template
- `<page_id>` pelo ID da página

### 4. Submeter Formulário

Se a página contiver um formulário, ele pode ser submetido via POST para:

```
/template/<slug>/<page_id>/submit
```

Após submissão, o usuário é redirecionado para uma página de sucesso.

## Arquivos do Sistema

### Modelos

- ✅ `app/models/template.py` - Modelo de templates com slugs e operações CRUD

### Controllers

- ✅ `app/controllers/template.py` - Gerenciamento de templates (admin)
- ✅ `app/controllers/public_template.py` - Rotas públicas para visualização

### Views

- ✅ `app/views/template_view.py` - Views administrativas de templates

### Templates HTML

- ✅ `app/templates/templates/` - Interface administrativa
  - `list.html` - Listagem de templates
  - `create.html` - Criação de templates
  - `edit.html` - Edição de templates
  - `view.html` - Visualização de templates
- ✅ `app/templates/public/` - Templates públicos
  - `template_page.html` - Renderização de página (completa)
  - `template_page_simple.html` - Renderização de página (simplificada)
  - `submit_success.html` - Página de sucesso

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
   - SMS para notificações urgentes
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

3. **Acessar página pública:**

   ```
   http://127.0.0.1:5000/template/<slug>/<page_id>
   ```

4. **Verificar logs de auditoria:**
   - Verifique o banco de dados na collection `audit_logs`

### Exemplos de URLs Públicas

```bash
# Template básico - página home
http://127.0.0.1:5000/template/basic_template/home

# Template profissional - página login
http://127.0.0.1:5000/template/professional_template/login

# Template e-commerce - página de contato
http://127.0.0.1:5000/template/ecommerce_template/contact
```

## Compatibilidade

- ✅ Totalmente compatível com estrutura atual
- ✅ Slugs gerados automaticamente para templates novos
- ✅ Sistema de páginas com conteúdo HTML personalizado
- ✅ Suporte a múltiplas páginas por template
- ✅ Páginas públicas acessíveis via URLs amigáveis

## Suporte

Para questões ou problemas:

1. Verifique os logs da aplicação
2. Consulte o `README.md` principal
3. Verifique a documentação de arquitetura em `ARCHITECTURE.md`
