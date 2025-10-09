# Client Manager - Guia de Contribuição para o GitHub Copilot

## Arquitetura do Projeto

Este projeto segue uma arquitetura MVC (Model-View-Controller) implementada em Flask com MongoDB como banco de dados:

- **Models**: `/app/models/` - Classes que definem a estrutura de dados e operações no MongoDB
- **Views**: `/app/views/` - Classes que gerenciam a renderização de templates
- **Controllers**: `/app/controllers/` - Classes que processam requisições e implementam a lógica de negócios

## Fluxo de Trabalho

O fluxo de trabalho típico para uma requisição HTTP neste aplicativo é:

1. O usuário faz uma requisição HTTP para uma rota
2. O Router direciona a requisição para o Controller apropriado
3. O Controller usa o Model para acessar/modificar dados no MongoDB
4. O Controller passa dados para a View
5. A View renderiza um template HTML com os dados
6. A resposta HTTP é enviada de volta ao usuário

## Principais Componentes

### Autenticação

- Implementada usando Flask-Login
- Diferentes níveis de acesso: super_admin, admin, client
- Controle de acesso baseado em função (RBAC)

### Gerenciamento de Dados

- MongoDB para armazenamento de dados
- PyMongo como biblioteca de acesso
- Estrutura de documentos para usuários, clientes, planos, etc.

### Interface do Usuário

- Templates HTML usando Jinja2
- Bootstrap para estilização
- JavaScript para interações do lado do cliente

## Convenções de Codificação

### Python

```python
def exemplo_de_funcao(parametro1, parametro2):
    """
    Descrição da função.
    
    Args:
        parametro1: Descrição do parâmetro 1
        parametro2: Descrição do parâmetro 2
        
    Returns:
        Descrição do valor retornado
    """
    # Código aqui
    resultado = parametro1 + parametro2
    return resultado
```

### Models

```python
@staticmethod
def create(nome, email):
    """
    Cria um novo registro no banco de dados.
    
    Args:
        nome: Nome do item
        email: Email do item
        
    Returns:
        tuple: (success, message_or_id)
    """
    try:
        # Validações e lógica
        return True, "ID do item criado"
    except Exception as e:
        return False, str(e)
```

### Controllers

```python
@app.route('/rota', methods=['GET', 'POST'])
@login_required
def exemplo_rota():
    """
    Endpoint para uma funcionalidade específica.
    
    Returns:
        Rendered template or redirect
    """
    if request.method == 'POST':
        # Processar formulário
        resultado = Model.create(request.form.get('campo1'), request.form.get('campo2'))
        if resultado[0]:
            flash('Operação realizada com sucesso!', 'success')
        else:
            flash(f'Erro: {resultado[1]}', 'danger')
        return redirect(url_for('outra_rota'))
    
    # Método GET
    dados = Model.get_all()
    return view.render_template('template.html', dados=dados)
```

### Views

```python
def render_template(template_name, **context):
    """
    Renderiza um template com contexto adicional comum.
    
    Args:
        template_name: Nome do arquivo de template
        **context: Variáveis de contexto para o template
        
    Returns:
        Rendered HTML
    """
    # Adicionar variáveis comuns ao contexto
    context['now'] = datetime.now()
    return render_template(template_name, **context)
```

## Testes

- Testes de unidade para Models
- Testes de integração para Controllers
- Mocks para interações com MongoDB

## Segurança

- Hashing de senhas
- Validação de entrada
- Proteção contra CSRF
- Controle de acesso baseado em função

Este guia serve como uma referência para manter a consistência no código gerado pelo GitHub Copilot para este projeto.
