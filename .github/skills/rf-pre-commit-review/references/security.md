# Security Checklist Reference

Regras de segurança aplicáveis a todos os arquivos do projeto.

## Regras Absolutas (bloqueiam o commit)

### 1. Nenhuma credencial no repositório

Os itens abaixo nunca devem aparecer em nenhum arquivo commitado:

- Senhas, tokens de API, chaves de acesso (AWS, serviços externos)
- Strings de conexão com banco de dados
- Valores reais de `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
- Tokens de autenticação de usuários reais

**Padrão correto:** usar `AwsParametersLib.Get SSM Parameter` para recuperar secrets em runtime.

```robot
# CORRETO
${password}=    AwsParametersLib.Get SSM Parameter    /dinostore/prod/admin/password

# ERRADO — senha hardcoded
${password}=    Set Variable    MinhaS3nhaSecreta!
```

### 2. Arquivo `.env` não commitado

- `.gitignore` deve conter `.env`
- Apenas `example.env` com valores fictícios (`...`, `<value>`) deve estar no repositório
- Verificar: `git ls-files | grep "\.env$"` não deve retornar nada

### 3. Logs de dados sensíveis

- Passwords, tokens e chaves de API nunca aparecem em `logger.info()` ou `Log    level=INFO`
- Dados sensíveis apenas em `level=DEBUG` (não exibidos por padrão no report)

```robot
# CORRETO
Log    Autenticando usuário: ${email}    level=INFO
Log    Token obtido: ${token}            level=DEBUG

# ERRADO
Log    Senha do usuário: ${password}    level=INFO
```

## Boas Práticas (pontos de atenção)

### Dados de Teste

- Dados de teste em `data/static.resource` devem ser **fictícios e não operacionais**
- Não usar CPFs, cartões de crédito, e-mails ou documentos reais de pessoas físicas
- Preferir dados gerados pela `FakerLibrary` ou declarados como claramente fictícios

### Variáveis de Ambiente em CI/CD

- Secrets no pipeline referenciados como `${{ secrets.NOME }}` — nunca literais
- Não logar o valor de secrets em steps de CI (`echo $SECRET` pode expor em logs públicos)

### Permissões AWS

- Roles e policies AWS devem seguir o princípio do menor privilégio
- `AWS_SESSION_TOKEN` indica credenciais temporárias — preferível a credenciais de longa duração

## Verificação Rápida

```bash
# Verificar se .env está no .gitignore
git check-ignore .env

# Verificar se não há credenciais rastreadas
git ls-files | grep "\.env$"

# Verificar padrões suspeitos em arquivos staged
git diff --cached | grep -iE "(password|secret|token|key)\s*=\s*['\"][^$%{]"
```

Se qualquer um dos comandos acima retornar resultado inesperado, o commit deve ser bloqueado.
