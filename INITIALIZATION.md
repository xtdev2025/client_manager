# Client Manager - Instruções de Inicialização

Este documento contém instruções sobre como iniciar o sistema pela primeira vez e configurar os dados iniciais.

## Inicialização Automática

Quando o aplicativo é iniciado pela primeira vez, ele verifica automaticamente se existem dados iniciais no banco de dados:

1. Se não existir nenhum usuário admin, um super_admin padrão será criado:
   - Username: `superadmin`
   - Senha: `Admin@123`
   **IMPORTANTE**: Por segurança, você deve fazer login e alterar esta senha imediatamente!

2. Se não existirem planos cadastrados, três planos padrão serão criados:
   - Basic Plan: R$29,99/mês
   - Standard Plan: R$59,99/mês
   - Premium Plan: R$99,99/mês

## Criação Manual de Super Admin

Se você precisar criar um super_admin manualmente (por exemplo, se o superadmin padrão for excluído), use o script `create_superadmin.py`:

```bash
python create_superadmin.py <username> <password>
```

Exemplo:

```bash
python create_superadmin.py admin SenhaSegura123
```

## Acessando o Sistema

1. Inicie o aplicativo:

   ```bash
   flask run
   ```

2. Acesse o sistema em seu navegador: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

3. Faça login com o usuário super_admin padrão ou o usuário que você criou manualmente.

4. Navegue para a seção de admins para criar novos administradores conforme necessário.

## Níveis de Acesso

O sistema possui dois níveis de acesso de administrador:

1. **super_admin**: Pode criar, editar e excluir outros administradores, além de todas as funcionalidades do sistema.

2. **admin**: Pode gerenciar clientes e planos, mas não pode gerenciar outros administradores.

Todos os clientes criados têm o nível de acesso **client** e podem acessar apenas suas próprias informações.
