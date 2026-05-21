# Documento de Arquitetura — Automação de Testes Web

> **Aviso:** Este é um documento de exemplo criado como apoio didático para o workshop de arquitetura de automações de testes. Os itens aqui descritos representam boas práticas para projetos reais e devem ser adaptados ao contexto de cada equipe.

---

## 1. Visão Geral

| Item | Descrição |
|---|---|
| **Aplicação sob teste** | Dino Store (`storedemo.testdino.com`) |
| **Tipo de automação** | Testes End-to-End (E2E) Web |
| **Framework principal** | Robot Framework |
| **Engine de browser** | Browser Library (Playwright) |
| **Linguagem de suporte** | Python 3.x |
| **Ambientes suportados** | PROD, HML |

---

## 2. Objetivos da Arquitetura

Em projetos reais, este seção deve responder **por que** as decisões foram tomadas:

- **Manutenibilidade:** separação clara entre lógica de UI, regras de negócio e casos de teste, para que mudanças na interface não impactem os testes
- **Reusabilidade:** keywords encapsuladas e reutilizáveis entre diferentes suítes e cenários
- **Rastreabilidade:** testes legíveis por qualquer membro da equipe (incluindo não-técnicos) via sintaxe Gherkin
- **Estabilidade:** isolamento de dados e ambientes para evitar falhas intermitentes
- **Segurança:** nenhuma credencial ou dado sensível armazenado no repositório

---

## 3. Estrutura de Diretórios

```
config/
  settings.resource   → Imports de bibliotecas e Suite Setup (ponto de entrada do ambiente)
  variables.resource  → Variáveis não sensíveis: browser, timeouts, URLs por ambiente

data/
  static.resource     → Dados de teste fixos e reproduzíveis
  dynamic.resource    → Keywords de geração de dados aleatórios em runtime

resources/
  base.resource       → Keywords utilitárias transversais (Open Browser, Save Screenshot)
  libraries/          → Bibliotecas Python customizadas para integrações externas
  pages/              → Page Objects: locators e ações atômicas de UI
  steps/              → Steps BDD: orquestração de keywords de negócio

tests/                → Casos de teste (.robot): apenas cenários, sem lógica de implementação
```

> **Regra de ouro:** cada camada só conhece a camada imediatamente abaixo dela. Testes chamam Steps; Steps chamam Pages; Pages chamam a biblioteca de browser.

---

## 4. Camadas da Arquitetura

### 4.1 Testes (`tests/`)

Responsabilidade exclusiva: **declarar cenários de negócio**.

**O que NÃO deve conter:**
- Chamadas diretas a `Fill Text`, `Click`, `Go To` ou qualquer keyword de browser
- Locators (seletores CSS, `data-testid`, XPath)
- Lógica de geração de dados
- Blocos `IF`, `FOR` ou manipulação de variáveis complexas

**Exemplo correto:**
```robot
CT_03: Deve registrar um novo usuário
    [Tags]    Gherkin    Regressão
    Dado que possuo dados de usuário aleatórios para cadastro
    E que esteja na página de cadastro
    Quando cadastrar um novo usuário
    Então deverá ser exibido a mensagem de cadastro ser bem-sucedido
```

### 4.2 Steps BDD (`resources/steps/`)

Responsabilidade: **orquestrar o fluxo de negócio** combinando keywords de Pages.

- Nomeados em linguagem natural (Gherkin): `Dado`, `Quando`, `Então`, `E`
- Compartilham estado entre steps via `Set Suite Variable`
- Não interagem diretamente com locators

```robot
Quando cadastrar um novo usuário
    Fill Registration Form
    ...    first_name=${user_data.first_name}
    ...    email=${user_data.email}
    Submit Registration Form
```

### 4.3 Page Objects (`resources/pages/`)

Responsabilidade: **abstrair a UI** — locators e ações atômicas de uma tela.

- Um arquivo por feature/página: `<feature>_page.resource`
- Todos os locators declarados em `*** Variables ***` com nomes em MAIÚSCULAS
- Preferência por `data-testid` sobre CSS ou XPath
- Uma keyword por ação atômica

```robot
*** Variables ***
${EMAIL_INPUT}    data-testid=signup-email-input

*** Keywords ***
Fill Registration Form
    [Documentation]    Preenche o formulário de registro com os dados fornecidos.
    [Arguments]    ${first_name}    ${last_name}    ${email}    ${password}
    Fill Text    ${FIRST_NAME_INPUT}    ${first_name}
    Fill Text    ${EMAIL_INPUT}         ${email}
```

### 4.4 Dados de Teste (`data/`)

| Arquivo | Quando usar |
|---|---|
| `static.resource` | Dados fixos e reproduzíveis (CPFs de teste, perfis predefinidos) |
| `dynamic.resource` | Dados gerados em runtime com `FakerLibrary` |
| `Generate User Data With Temp Email` | Quando o fluxo exige recebimento real de e-mail |

**Nunca hardcodar** dados sensíveis (senhas, tokens, chaves de API) em arquivos `.resource`.

---

## 5. Gestão de Ambientes

O ambiente é controlado pela variável `${ENVIRONMENT}` com fallback para `PROD`.

**Formas de configurar:**
```bash
# Via variável de ambiente no sistema operacional ou .env
ENVIRONMENT=HML

# Via argumento CLI
robot --variable ENVIRONMENT:HML tests/

# Via arquivo .env (somente local, nunca commitado)
ENVIRONMENT=HML
```

As URLs são resolvidas dinamicamente em `config/variables.resource`:
```robot
&{BASE_URL}
...    PROD= https://storedemo.testdino.com
...    HML= https://storedemo.hml.testdino.com
```

---

## 6. Gestão de Segredos e Credenciais

| O que | Como |
|---|---|
| Senhas e tokens de teste | AWS SSM Parameter Store via `AwsParametersLib` |
| Credenciais AWS | Variáveis de ambiente ou secrets do CI/CD |
| Configurações locais | Arquivo `.env` (nunca commitado) |
| Referência para novos membros | `example.env` (sem valores reais) |

```python
# Exemplo de uso em biblioteca Python
from robot.api.deco import keyword

@keyword("Get SSM Parameter")
def get_ssm_parameter(self, parameter_name: str) -> str:
    # Recupera o parâmetro do AWS SSM de forma segura
    ...
```

> Em projetos reais, documentar aqui quais parâmetros existem no SSM, qual perfil IAM é necessário e como configurar acesso local.

---

## 7. Bibliotecas e Dependências

### 7.1 Bibliotecas Robot Framework

| Biblioteca | Propósito |
|---|---|
| `Browser` (Playwright) | Interação com UI web |
| `FakerLibrary` | Geração de dados falsos realistas |
| `RequestsLibrary` | Chamadas HTTP / validações de API |
| `Collections`, `String`, `DateTime` | Utilitários nativos do Robot |

### 7.2 Bibliotecas Python Customizadas

Criadas apenas quando a funcionalidade **não existe** nas bibliotecas disponíveis.

| Arquivo | Alias | Responsabilidade |
|---|---|---|
| `temp_email.py` | `TempEmailLib` | Criação de e-mails temporários reais (mail.tm) |
| `aws_parameters.py` | `AwsParametersLib` | Leitura de parâmetros do AWS SSM |

**Padrão obrigatório para bibliotecas Python:**
```python
from robot.api.deco import keyword
from robot.api import logger

@keyword("Nome Da Keyword")
def minha_funcao(param: str) -> str:
    logger.info(f"Executando com: {param}")  # usar logger, nunca print()
    try:
        # lógica
    except Exception as e:
        raise AssertionError(f"Falha ao executar: {e}") from e
```

### 7.3 Instalação de Dependências

```bash
pip install -r requirements.txt
rfbrowser init
```

---

## 8. Convenções de Código

| Convenção | Regra |
|---|---|
| Toda keyword nova | Deve ter `[Documentation]` |
| Timeouts | Sempre via variável (`${DEFAULT_TIMEOUT}`), nunca hardcoded |
| Screenshots | Sempre via `Save Screenshot` (base.resource), nunca `Take Screenshot` diretamente |
| Seletores | Preferir `data-testid` > ARIA roles > CSS > XPath |
| Nomes de arquivos | `snake_case` para `.resource` e `.py` |
| Nomes de keywords de Page | Ação + Elemento: `Fill Email Input`, `Click Submit Button` |
| Nomes de keywords de Step | Linguagem natural: `Dado que esteja na página de login` |
| Imports | Sempre usando `${EXECDIR}` como raiz absoluta |

---

## 9. Estratégia de Execução

### Tags

Usar tags para controlar quais testes são executados em cada contexto:

| Tag | Quando executar |
|---|---|
| `Regressão` | A cada deploy em HML e PROD |
| `Smoke` | Pipeline rápido pós-deploy |
| `Gherkin` | Demonstração / validação de cenários BDD |
| `Encapsulamento` | Exemplos didáticos (não executar em CI) |

```bash
# Executar apenas testes de regressão em HML
robot --variable ENVIRONMENT:HML --include Regressão tests/

# Executar smoke test ignorando exemplos didáticos
robot --include Smoke --exclude Encapsulamento tests/
```

### Paralelismo

> Em projetos reais, documentar aqui a estratégia de paralelismo (ex: `pabot`, partição por suíte, limites de concorrência).

---

## 10. Integração Contínua (CI/CD)

> Em projetos reais, detalhar aqui o pipeline. Este documento deve cobrir:

- **Gatilhos:** push em `main`, PRs, agendamento noturno
- **Ambientes de execução:** container Docker com dependências pré-instaladas
- **Armazenamento de resultados:** relatórios Robot (`log.html`, `report.html`) publicados como artefatos
- **Notificações:** Slack, Teams ou e-mail em caso de falha
- **Secrets:** nunca em variáveis de texto plano; usar secrets do CI/CD (GitHub Actions Secrets, Azure Key Vault, etc.)

**Exemplo de estrutura mínima para GitHub Actions:**
```yaml
- name: Executar testes
  run: robot --variable ENVIRONMENT:HML --include Regressão tests/
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 11. Decisões Arquiteturais Registradas (ADR)

> Em projetos reais, registrar as principais decisões com justificativa. Exemplo:

| # | Decisão | Alternativas consideradas | Motivo da escolha |
|---|---|---|---|
| 01 | Browser Library (Playwright) sobre SeleniumLibrary | SeleniumLibrary, Appium | Suporte nativo a auto-wait, traces e múltiplos contextos |
| 02 | Dados sensíveis via AWS SSM | `.env` criptografado, Vault | Centralização e auditoria de acesso a segredos |
| 03 | `data-testid` como seletor padrão | XPath, CSS class | Estabilidade frente a refatorações de estilo e estrutura |
| 04 | E-mails temporários via mail.tm | Mailinator, mailosaur | Gratuito, sem rate limit e com API estável |

---

## 12. Onboarding para Novos Membros

Checklist mínimo para um novo membro começar a contribuir:

- [ ] Instalar Python 3.x e dependências: `pip install -r requirements.txt`
- [ ] Inicializar o Browser Library: `rfbrowser init`
- [ ] Copiar `example.env` para `.env` e preencher as variáveis necessárias
- [ ] Configurar credenciais AWS (perfil local ou variáveis de ambiente)
- [ ] Executar a suíte de smoke test para validar o ambiente: `robot --include Smoke tests/`
- [ ] Ler este documento e o `README.md` antes de criar novos arquivos

---

*Documento mantido pela equipe de qualidade. Atualizar sempre que uma decisão arquitetural for alterada.*
