# Client Manager App

Esta é uma aplicação Flask para gerenciamento de clientes com autenticação, controle de acesso baseado em funções (RBAC) e operações CRUD usando MongoDB.

## Funcionalidades

- Autenticação de Usuários (Login, Registro, Logout)
- Controle de Acesso Baseado em Funções (RBAC)
- Operações CRUD para Clientes
- Operações CRUD para Administradores
- Operações CRUD para Planos

## Arquitetura MVC

O projeto segue a arquitetura Model-View-Controller (MVC):

- **Models**: Definição das estruturas de dados e interações com o banco de dados
- **Views**: Camada responsável pela renderização de templates
- **Controllers**: Lógica de negócio e processamento de requisições

## Tecnologias Utilizadas

- Flask (Framework web)
- MongoDB (Banco de dados)
- Flask-Login (Gerenciamento de sessão)
- Jinja2 (Engine de templates)
- Bootstrap (Framework CSS)

## Instruções de Configuração

### Pré-requisitos

- Python 3.9+
- MongoDB
- Node.js (para hooks do Git)

### Instalação

1. Clone o repositório

   ```bash
   git clone https://github.com/rootkitoriginal/client_manager.git
   cd client_manager
   ```

2. Crie um ambiente virtual

   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual

   ```bash
   # No Windows
   venv\Scripts\activate
   
   # No Linux/Mac
   source venv/bin/activate
   ```

4. Instale os pacotes necessários

   ```bash
   pip install -r requirements.txt
   ```

5. Configure o MongoDB e adicione as variáveis de ambiente em um arquivo `.env`

   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=1
   SECRET_KEY=sua_chave_secreta_aqui
   MONGO_URI=mongodb://localhost:27017/client_manager
   ```

6. Execute o script de inicialização para configurar o banco de dados

   ```bash
   python run.py --init
   ```

7. Execute a aplicação

   ```bash
   flask run
   ```

## Uso

- Acesse a aplicação em [http://localhost:5000](http://localhost:5000)
- Crie um superadmin com o comando `python create_superadmin.py`
- Faça login com as credenciais de superadmin para gerenciar usuários e clientes

## Desenvolvimento

### Hooks do Git

Este projeto utiliza Husky para garantir a qualidade do código:

- **pre-commit**: Verifica estilo de código com flake8 antes de cada commit
- **pre-push**: Executa testes antes de enviar código para o repositório remoto

### Estrutura do Projeto

```plaintext
client_manager/
├── app/
│   ├── controllers/   # Lógica de controle
│   ├── models/        # Definições de dados
│   ├── static/        # Arquivos estáticos (CSS, JS)
│   ├── templates/     # Templates HTML
│   ├── utils/         # Utilitários
│   └── views/         # Camada de apresentação
├── .flake8           # Configuração do linter
├── .gitignore        # Arquivos ignorados pelo git
├── config.py         # Configurações da aplicação
├── requirements.txt  # Dependências Python
└── run.py           # Script principal para execução
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
