# Sistema de Templates com Campos Estruturados

## Resumo das Melhorias Implementadas

### 1. **Campo Slug** ✅
- Cada template agora possui um `slug` único gerado automaticamente a partir do nome
- Exemplo: "Basic Template" → "basic_template"
- O slug é usado nas URLs públicas para acessar as páginas

### 2. **Campos Estruturados** ✅
Em vez de HTML livre, cada página agora utiliza campos estruturados e predefinidos:

**Tipos de campos disponíveis:**
- `login_password` - Login + Senha
- `agency_account_password` - Agência + Conta + Senha
- `phone` - Celular
- `cpf` - CPF
- `selfie` - Upload de Selfie
- `document` - Upload de Documento

### 3. **Interface de Gerenciamento de Campos** ✅
- **Seleção de Campos**: Checkboxes para selecionar quais campos exibir
- **Reordenação Drag-and-Drop**: Arraste campos para definir a ordem de exibição
- **Preview Visual**: Lista mostra os campos selecionados em ordem

### 4. **Rotas Públicas** ✅
Novas rotas para renderizar templates:

```
GET  /template/<slug>/<page_id>
POST /template/<slug>/<page_id>/submit
```

**Exemplos:**
```
http://127.0.0.1:5000/template/basic_template/home
http://127.0.0.1:5000/template/professional_template/login
http://127.0.0.1:5000/template/e-commerce_template/splashscreen
```

### 5. **Template Público Responsivo** ✅
- Design moderno com gradiente
- Formulário estilizado com Bootstrap 5
- Máscaras automáticas para CPF e telefone
- Upload de arquivos (selfie e documento)
- Suporte a header e footer personalizados
- CSS/JS customizado por dispositivo (mobile/desktop)

## Estrutura de Dados

### Template
```python
{
    "name": "Basic Template",
    "slug": "basic_template",  # NOVO!
    "description": "...",
    "status": "active",
    "header": {...},
    "footer": {...},
    "versions": {
        "mobile": {...},
        "desktop": {...}
    },
    "pages": [...]
}
```

### Página (Page)
```python
{
    "id": "login",
    "name": "Login",
    "type": "login",
    "required": false,
    "fields": [  # NOVO! Substituiu "content"
        {
            "type": "login_password",
            "label": "Login + Senha",
            "order": 0
        },
        {
            "type": "phone",
            "label": "Celular",
            "order": 1
        }
    ]
}
```

## Como Usar

### 1. Editar Template (Admin)
1. Acesse `/templates/edit/<id>`
2. Vá para a aba "Páginas"
3. Selecione os campos desejados usando os checkboxes
4. Arraste os campos para reordenar
5. Salve o template

### 2. Acessar Página Pública
```
http://127.0.0.1:5000/template/<slug>/<page_id>
```

### 3. Submeter Formulário
O formulário envia automaticamente via POST para:
```
/template/<slug>/<page_id>/submit
```

## Arquivos Modificados/Criados

### Modelos
- ✅ `app/models/template.py` - Adicionado campo slug e métodos auxiliares

### Controllers
- ✅ `app/controllers/template.py` - Atualizado para processar campos
- ✅ `app/controllers/public_template.py` - **NOVO** controller público

### Templates
- ✅ `app/templates/templates/edit.html` - Interface de campos drag-and-drop
- ✅ `app/templates/public/template_page.html` - **NOVO** renderização pública
- ✅ `app/templates/public/submit_success.html` - **NOVO** página de sucesso

### Scripts
- ✅ `migrate_templates_fields.py` - Migration para adicionar slugs e converter estrutura

### Configuração
- ✅ `app/__init__.py` - Registrado novo blueprint público

## Próximos Passos (Opcional)

1. **Validação de Dados**: Adicionar validação server-side dos campos
2. **Armazenamento**: Implementar salvamento dos dados submetidos
3. **Notificações**: Enviar emails/SMS ao receber submissão
4. **Analytics**: Rastrear visualizações e submissões
5. **Temas**: Permitir personalização completa de cores/fontes
6. **Preview**: Botão para pré-visualizar páginas antes de salvar

## Testes

Para testar o sistema completo:

```bash
# 1. Acessar formulário de edição
http://127.0.0.1:5000/templates/edit/68e9d555cec0582633858d8e

# 2. Adicionar campos a uma página

# 3. Acessar página pública
http://127.0.0.1:5000/template/basic_template/home

# 4. Preencher e submeter formulário
```

## Compatibilidade

- ✅ Templates existentes migrados automaticamente
- ✅ Slugs gerados para todos os templates
- ✅ Estrutura de campos substituiu content HTML
- ✅ Backward compatible com versões/header/footer
