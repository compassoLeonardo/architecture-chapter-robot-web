# RF Conventions Reference

Regras de convenção específicas para Robot Framework neste projeto.

## Indentação

- **4 espaços** por nível de indentação — nunca tabs
- Separador entre keyword e argumentos: **2 espaços ou mais** (o editor pode usar alinhamento)
- Continuação de linha longa: `...` com 4 espaços de indentação na linha seguinte

```robot
# CORRETO
Fill Registration Form
    [Documentation]    Preenche o formulário de registro.
    [Arguments]    ${first_name}    ${last_name}    ${email}    ${password}
    Fill Text    ${FIRST_NAME_INPUT}    ${first_name}
    Fill Text    ${LAST_NAME_INPUT}     ${last_name}

# ERRADO — tab e separador de 1 espaço
Fill Registration Form
	Fill Text ${FIRST_NAME_INPUT} ${first_name}
```

## Documentação

- Toda keyword deve ter `[Documentation]`
- Suítes em `resources/steps/` exigem `Documentation` na seção `*** Settings ***`
- Para documentações longas, usar continuação com `...`:

```robot
Generate User Data With Temp Email
    [Documentation]
    ...    Gera dados de usuário com e-mail temporário real.
    ...
    ...    Returns:
    ...        Dicionário com: email, password, email_token
```

## Locators

| Preferência | Exemplo | Uso |
|---|---|---|
| 1º | `data-testid=signup-email-input` | Sempre que disponível |
| 2º | Role ARIA | `role=button[name="Submit"]` |
| 3º | Texto visível | `text=Account created` |
| Evitar | CSS class/ID | `.btn-primary`, `#email` |
| Nunca | XPath complexo | `//div[@class='form']//input[2]` |

- Locators **sempre** em `*** Variables ***` com nome em MAIÚSCULAS
- **Nunca** inline no corpo da keyword

```robot
# CORRETO
*** Variables ***
${EMAIL_INPUT}    data-testid=signup-email-input

*** Keywords ***
Fill Email Field
    Fill Text    ${EMAIL_INPUT}    ${email}

# ERRADO — locator inline
Fill Email Field
    Fill Text    data-testid=signup-email-input    ${email}
```

## Timeouts

- Usar sempre `${DEFAULT_TIMEOUT}` de `config/variables.resource`
- **Nunca** hardcodar valores como `30s`, `10s`, `timeout=5000`

```robot
# CORRETO
Wait For Elements State    ${ELEMENT}    visible    timeout=${DEFAULT_TIMEOUT}

# ERRADO
Wait For Elements State    ${ELEMENT}    visible    timeout=30s
```

## Imports

- Sempre usar `${EXECDIR}` como raiz dos imports
- Nunca usar paths relativos (`../config/settings.resource`)
- Ordem: `settings.resource` → `base.resource` → pages/steps específicos

```robot
*** Settings ***
Resource    ${EXECDIR}/config/settings.resource
Resource    ${EXECDIR}/resources/base.resource
Resource    ${EXECDIR}/resources/pages/checkout_page.resource
```

## Nomenclatura

| Camada | Padrão | Exemplo |
|---|---|---|
| Page keyword | `Verbo + Substantivo` | `Fill Email Field`, `Go To Login Page`, `Verify Success Message` |
| Step Dado | `Dado que ...` | `Dado que esteja autenticado` |
| Step Quando | `Quando ...` | `Quando submeter o formulário` |
| Step Então | `Então deverá ...` | `Então deverá ser redirecionado` |
| Locator var | `MAIÚSCULAS_COM_UNDERLINE` | `${EMAIL_INPUT}`, `${SUBMIT_BUTTON}` |
| Page file | `<feature>_page.resource` | `checkout_page.resource` |
| Step file | `<feature>_steps.resource` | `checkout_steps.resource` |
