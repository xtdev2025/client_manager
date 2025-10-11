# Melhorias no Sistema de Templates

## 📋 Resumo das Alterações

Este documento descreve as melhorias implementadas no sistema de edição de templates do Client Manager.

## 🎯 Funcionalidades Adicionadas

### 1. **Configuração de Header**
- ✅ Habilitar/desabilitar header
- ✅ Upload de logo (URL)
- ✅ Seletor de cor de fundo com preview
- ✅ Editor de conteúdo HTML com Monaco Editor

### 2. **Configuração de Footer**
- ✅ Habilitar/desabilitar footer
- ✅ Seletor de cor de fundo com preview
- ✅ Editor de conteúdo HTML com Monaco Editor

### 3. **Versões Mobile e Desktop**
- ✅ Habilitar/desabilitar versão mobile
- ✅ Habilitar/desabilitar versão desktop
- ✅ CSS customizado para cada versão (com Monaco Editor)
- ✅ JavaScript customizado para cada versão (com Monaco Editor)

### 4. **Gerenciamento de Páginas**
- ✅ Páginas obrigatórias: Home e Splashscreen
- ✅ Adicionar páginas internas personalizadas
- ✅ Remover páginas não obrigatórias
- ✅ Editor de conteúdo HTML para cada página (Monaco Editor)

### 5. **Tipos de Login**
Para páginas do tipo "Login", é possível configurar múltiplos tipos:
- ✅ Login + Senha
- ✅ Agência + Conta + Senha
- ✅ Celular
- ✅ CPF
- ✅ Selfie
- ✅ Documento

### 6. **Monaco Editor**
Integração do Monaco Editor (o mesmo editor do VS Code) para:
- HTML (conteúdo de páginas, header, footer)
- CSS (estilos customizados mobile/desktop)
- JavaScript (scripts customizados mobile/desktop)

**Benefícios:**
- Syntax highlighting
- Auto-complete
- Validação de código em tempo real
- Melhor experiência de desenvolvimento

## 📁 Arquivos Modificados

### Backend
1. **`app/models/template.py`**
   - Adicionada estrutura de dados para header, footer, versions e pages
   - Criação de templates com estrutura padrão

2. **`app/controllers/template.py`**
   - Atualizado método `edit_template` para processar novos campos
   - Suporte para arrays de páginas e configurações aninhadas

### Frontend
3. **`app/templates/templates/edit.html`**
   - Interface com abas (Header, Footer, Versões, Páginas)
   - Sistema de adicionar/remover páginas dinamicamente
   - Integração com Monaco Editor
   - Validação de IDs únicos para páginas

4. **`app/templates/templates/view.html`**
   - Visualização das novas configurações
   - Badges para tipos de login
   - Indicadores de páginas obrigatórias

5. **`app/templates/templates/list.html`**
   - Nova coluna mostrando número de páginas
   - Ícones indicando versões ativas (mobile/desktop)

### Utilitários
6. **`migrate_templates.py`**
   - Script de migração para atualizar templates existentes
   - Adiciona estrutura padrão aos templates antigos

## 🚀 Como Usar

### Editar um Template

1. Acesse `/templates/`
2. Clique em "Editar" em um template
3. Configure as diferentes seções:

#### **Header Tab**
- Marque "Habilitar Header" para ativar
- Adicione URL do logo
- Escolha cor de fundo
- Adicione HTML customizado

#### **Footer Tab**
- Marque "Habilitar Footer" para ativar
- Escolha cor de fundo
- Adicione HTML customizado

#### **Versões Tab**
- Configure CSS e JS específicos para mobile
- Configure CSS e JS específicos para desktop

#### **Páginas Tab**
- Visualize páginas obrigatórias (Home e Splashscreen)
- Clique em "Adicionar Página" para criar novas
- Para páginas de login, selecione os tipos de autenticação
- Remova páginas não obrigatórias se necessário

### Migrar Templates Existentes

```bash
cd /home/rootkit/Apps/xPages/client_manager
python3 migrate_templates.py
```

## 📊 Estrutura de Dados

### Template Object
```javascript
{
  "name": "Nome do Template",
  "description": "Descrição",
  "status": "active|inactive",
  
  "header": {
    "enabled": true,
    "content": "<div>HTML</div>",
    "logo": "https://example.com/logo.png",
    "backgroundColor": "#ffffff"
  },
  
  "footer": {
    "enabled": true,
    "content": "<div>HTML</div>",
    "backgroundColor": "#f8f9fa"
  },
  
  "versions": {
    "mobile": {
      "enabled": true,
      "customCss": "/* CSS */",
      "customJs": "// JavaScript"
    },
    "desktop": {
      "enabled": true,
      "customCss": "/* CSS */",
      "customJs": "// JavaScript"
    }
  },
  
  "pages": [
    {
      "id": "home",
      "name": "Home",
      "type": "home",
      "required": true,
      "content": "<div>HTML</div>"
    },
    {
      "id": "splashscreen",
      "name": "Splashscreen",
      "type": "splashscreen",
      "required": true,
      "duration": 3000,
      "content": "<div>HTML</div>"
    },
    {
      "id": "login",
      "name": "Login",
      "type": "login",
      "loginTypes": ["user_pass", "cpf", "phone"],
      "content": "<div>HTML</div>"
    }
  ]
}
```

## 🔧 Tecnologias Utilizadas

- **Monaco Editor** v0.44.0 - Editor de código avançado
- **Bootstrap 5** - Framework CSS
- **Flask** - Backend Python
- **MongoDB** - Banco de dados
- **Jinja2** - Template engine

## ✅ Validações Implementadas

1. IDs de página únicos
2. Campos obrigatórios (nome, tipo)
3. Páginas obrigatórias não podem ser removidas
4. Validação de estrutura JSON no backend

## 🎨 Melhorias de UX

1. **Abas organizadas** - Separação clara das funcionalidades
2. **Monaco Editor** - Melhor experiência de edição de código
3. **Color Picker** - Seletor visual de cores
4. **Badges informativos** - Status visual claro
5. **Confirmação de exclusão** - Previne remoção acidental
6. **Páginas obrigatórias** - Indicador visual claro

## 📝 Notas de Desenvolvimento

- O Monaco Editor carrega de forma assíncrona
- Os editores são sincronizados com os textareas originais
- A clonagem de páginas utiliza `document.importNode` para compatibilidade
- IDs únicos são gerados para cada novo editor Monaco

## 🔜 Próximos Passos Sugeridos

1. Preview em tempo real do template
2. Biblioteca de componentes reutilizáveis
3. Histórico de versões
4. Importar/exportar templates
5. Temas predefinidos
6. Validação de HTML/CSS/JS
7. Upload de imagens integrado

---

**Data de Implementação:** 11 de Outubro de 2025  
**Versão:** 2.0.0
