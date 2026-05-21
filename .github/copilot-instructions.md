# Copilot Instructions — Robot Framework Test Architecture

## Visão Geral do Projeto
Projeto de automação de testes web usando Robot Framework com Browser Library (Playwright).
A aplicação sob teste é a **Dino Store** (`storedemo.testdino.com`).

---

## Estrutura de Diretórios e Responsabilidades

```
config/
  settings.resource   → Libraries, Suite Setup e keywords de inicialização de ambiente
  variables.resource  → Todas as variáveis não sensíveis (browser, timeouts, URLs por ambiente)
data/
  static.resource     → Dados de teste fixos e reproduzíveis
  dynamic.resource    → Keywords que geram dados aleatórios em tempo de execução (FakerLibrary, TempEmail)
resources/
  base.resource       → Keywords utilitárias globais (Open Browser, Save Screenshot, Wait Until URL Contains)
  libraries/          → Bibliotecas Python customizadas para integrações externas
  pages/              → Page Objects: locators e keywords de interação com a UI
  steps/              → Keywords de negócio (BDD/Gherkin): orquestram keywords de pages
tests/                → Arquivos de teste (.robot): apenas casos de teste, sem lógica de implementação
```

---

## Convenções Obrigatórias

### Testes (`tests/*.robot`)
- Casos de teste **nunca** interagem diretamente com locators ou chamam `Fill Text`, `Click`, etc.
- Toda lógica de UI deve ser delegada a keywords em `resources/pages/`
- Toda lógica de negócio (fluxo) deve ser delegada a keywords em `resources/steps/`
- Imports sempre usando `${EXECDIR}` como raiz

### Page Objects (`resources/pages/*.resource`)
- Nome do arquivo: `<feature>_page.resource` (ex: `dino_register_page.resource`)
- Todas as variáveis de locator declaradas em `*** Variables ***` com nomes descritivos em maiúsculas
- Locators usam `data-testid` preferencialmente (ex: `data-testid=signup-email-input`)
- Uma keyword por ação atômica: Fill, Click, Verify, Go To
- Toda keyword deve ter `[Documentation]`
- Verificações usam `Wait For Elements State` com `${DEFAULT_TIMEOUT}`

Exemplo de estrutura de Page Object:
```robot
*** Settings ***
Resource    ${EXECDIR}/config/settings.resource
Resource    ${EXECDIR}/resources/base.resource

*** Variables ***
${NOME_ELEMENTO}    data-testid=nome-do-elemento

*** Keywords ***
Go To Página
    [Documentation]    Navega para a página X.
    Go To    ${BASE_URL}/rota

Fill Campo
    [Documentation]    Preenche o campo X com o valor fornecido.
    [Arguments]    ${valor}
    Fill Text    ${NOME_ELEMENTO}    ${valor}

Verify Elemento Visível
    [Documentation]    Verifica que o elemento X está visível.
    Wait For Elements State    ${NOME_ELEMENTO}    visible    timeout=${DEFAULT_TIMEOUT}
```

### Steps BDD (`resources/steps/*.resource`)
- Nome do arquivo: `<feature>_steps.resource`
- Keywords nomeadas em linguagem natural / Gherkin (ex: `Dado que esteja na página de login`)
- Steps apenas orquestram keywords de pages — sem lógica de UI direta
- Variáveis de contexto compartilhadas entre steps usam `Set Suite Variable`

### Dados de Teste (`data/`)
- Dados fixos e reproduzíveis → `static.resource`
- Dados gerados em runtime → `dynamic.resource` usando `FakerLibrary`
- Dados que exigem e-mail real recebível → `Generate User Data With Temp Email` (usa mail.tm via `TempEmailLib`)
- **Nunca** hardcodar dados sensíveis (senhas, tokens, chaves) nos arquivos `.resource`

### Segredos e Credenciais
- Segredos são recuperados do **AWS SSM Parameter Store** via `AwsParametersLib.Get SSM Parameter`
- Credenciais AWS carregadas via variáveis de ambiente (`.env` local ou CI/CD secrets)
- O arquivo `.env` **nunca** é commitado — usar `example.env` como referência

### Configuração de Ambiente
- Ambiente controlado pela variável `${ENVIRONMENT}` (padrão: `PROD`, opções: `PROD`, `HML`)
- URLs definidas como dicionários em `variables.resource` indexados pelo ambiente
- Override via variável de ambiente: `%{ENVIRONMENT=PROD}` ou argumento CLI: `--variable ENVIRONMENT:HML`

### Bibliotecas Python (`resources/libraries/`)
- Criadas apenas quando a funcionalidade não existe em bibliotecas Robot Framework disponíveis
- Decorar keywords com `@keyword("Nome Da Keyword")` do `robot.api.deco`
- Usar `logger` do `robot.api` para logs (não `print`)
- Tratar exceções e relançar como `AssertionError` com mensagem descritiva

---

## Bibliotecas Disponíveis

| Biblioteca | Alias | Uso |
|---|---|---|
| `Browser` | — | Interação com UI web (Playwright) |
| `FakerLibrary` | — | Geração de dados aleatórios |
| `RequestsLibrary` | — | Chamadas HTTP / API REST |
| `dotenv` | — | Carregamento de variáveis do `.env` |
| `boto3` | — | SDK AWS (usado em `aws_parameters.py`) |
| `temp_email.py` | `TempEmailLib` | Criação de e-mails temporários reais |
| `aws_parameters.py` | `AwsParametersLib` | Leitura de parâmetros do AWS SSM |

---

## Padrões de Qualidade

- Toda keyword nova deve ter `[Documentation]`
- Screenshots são salvos via `Save Screenshot` (keyword em `base.resource`) — não chamar `Take Screenshot` diretamente nos testes
- Timeouts e retry settings vêm de `variables.resource` — não hardcodar valores como `30s` nos testes
- Seletores CSS diretos (`.classe`, `#id`) são evitados — preferir `data-testid` ou roles ARIA
