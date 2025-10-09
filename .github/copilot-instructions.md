# Instruções para o GitHub Copilot

Este arquivo contém instruções específicas para o GitHub Copilot ajudar no desenvolvimento do projeto Client Manager, uma aplicação Flask com MongoDB que implementa um sistema MVC para gerenciamento de clientes.

## Convenções de Código

Ao sugerir código, o GitHub Copilot deve seguir estas convenções:

1. **Estrutura MVC**:
   - Models: `/app/models/` - Para classes que interagem com o banco de dados MongoDB
   - Views: `/app/views/` - Para classes que renderizam templates
   - Controllers: `/app/controllers/` - Para lógica de negócios e processamento de requisições

2. **Formatação Python**:
   - Seguir PEP 8
   - Indentação de 4 espaços
   - Linhas com máximo de 100 caracteres
   - Docstrings para todas as funções e classes

3. **MongoDB**:
   - Usar modelo de documento para coleções
   - Implementar validação de esquema quando possível
   - Organizar consultas em métodos estáticos dentro dos Models

4. **Segurança**:
   - Sempre usar hashing para senhas (como já implementado)
   - Nunca armazenar credenciais no código
   - Validar todas as entradas de usuário

## Tarefas Comuns

### Criar Novo Endpoint

Para criar um novo endpoint, seguir este padrão:

1. Adicionar método no controller apropriado em `/app/controllers/`
2. Criar método na view correspondente em `/app/views/`
3. Implementar template em `/app/templates/`
4. Se necessário, adicionar métodos no model em `/app/models/`

### Adicionar Nova Funcionalidade

Quando adicionar uma nova funcionalidade:

1. Considerar o controle de acesso baseado em função (RBAC)
2. Implementar validações de formulário
3. Adicionar mensagens flash para feedback ao usuário
4. Atualizar a navegação no arquivo `/app/templates/navbar.html` se necessário

### Padrão para Interações com MongoDB

```python
@staticmethod
def create(param1, param2, ...):
    """
    Cria um novo objeto no banco de dados.
    
    Args:
        param1: Descrição do parâmetro
        param2: Descrição do parâmetro
        
    Returns:
        tuple: (success, message_or_object)
    """
    try:
        # Validações
        if not param1:
            return False, "Parâmetro inválido"
            
        # Processamento
        new_object = {
            'field1': param1,
            'field2': param2,
            'created_at': datetime.now()
        }
        
        # Inserção no banco
        result = mongo.db.collection.insert_one(new_object)
        
        return True, str(result.inserted_id)
    except Exception as e:
        return False, str(e)
```

## Bibliotecas Principais

O projeto utiliza as seguintes bibliotecas principais:

- Flask - Framework web
- PyMongo - Integração com MongoDB
- Flask-Login - Gerenciamento de autenticação
- python-dotenv - Gerenciamento de variáveis de ambiente

Ao sugerir código que utiliza estas bibliotecas, siga os padrões já existentes no projeto.

## Estrutura de Templates

Os templates HTML seguem este padrão:

1. Extensão de `layout.html`
2. Uso de blocos Jinja2: `{% block content %}{% endblock %}`
3. Inclusão de elementos de navegação via `navbar.html`
4. Uso de classes Bootstrap para estilização

## Testes e Qualidade de Código

Ao sugerir novas implementações, considere:

1. Código que passe pelas verificações do flake8 configuradas no hook pre-commit
2. Implementações que sigam os princípios de responsabilidade única
3. Funções testáveis com parâmetros e retornos bem definidos

## Fluxo Git

Para trabalhar com o repositório:

1. Crie branches específicas para features: `feature/nome-da-feature`
2. Use mensagens de commit descritivas seguindo o padrão: `[Área]: Descrição da alteração`
3. Certifique-se de que o código passa pelos hooks do Husky antes do commit

---

Estas instruções devem ajudar o GitHub Copilot a gerar sugestões mais alinhadas com a arquitetura e padrões do projeto.