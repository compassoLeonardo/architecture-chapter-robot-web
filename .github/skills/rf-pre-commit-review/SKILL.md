---
name: rf-pre-commit-review
description: 'Code review antes do commit para projetos Robot Framework + Python. Use quando: quiser revisar código antes de commitar; verificar boas práticas, indentação e convenções RF e Python; validar documentação de keywords; checar segurança de dados (credenciais, secrets); verificar reaproveitamento de código e Page Objects; garantir continuidade da arquitetura em camadas (Test → Step → Page); validar pipeline CI/CD. Gera relatório no chat com pontos críticos e de atenção.'
argument-hint: 'Arquivo(s) ou pasta a revisar, ex: resources/pages/checkout_page.resource'
---

# RF Pre-Commit Review

Realiza um code review estruturado de código Robot Framework e Python antes do commit, verificando convenções, segurança, arquitetura e documentação. Ao final, gera um relatório com **Pontos Críticos** e **Pontos de Atenção** diretamente no chat.

---

## Quando Usar

- Antes de fazer `git commit` em qualquer arquivo `.resource`, `.robot` ou `.py`
- Ao adicionar uma nova Page Object, Step ou biblioteca Python
- Ao modificar `config/`, `data/` ou `resources/`
- Ao alterar o pipeline de CI/CD

---

## Procedimento de Revisão

Execute cada etapa sequencialmente. Registre falhas conforme encontradas para montar o relatório final.

### Passo 1 — Identificar Escopo

1. Se o usuário forneceu um argumento, revisar apenas os arquivos indicados
2. Caso contrário, listar arquivos modificados via `git diff --name-only HEAD` ou inspecionar o workspace
3. Classificar cada arquivo por tipo: `tests/`, `resources/pages/`, `resources/steps/`, `data/`, `config/`, `resources/libraries/`

### Passo 2 — Convenções Robot Framework

Para cada arquivo `.resource` ou `.robot`, verificar:

- [ ] Seção `*** Settings ***` presente e com `Documentation` na suíte (obrigatório em steps)
- [ ] Toda keyword possui `[Documentation]`
- [ ] Indentação usa **4 espaços** (nunca tabs); separação de argumentos usa **2 espaços ou mais**
- [ ] Nomes de keywords em **linguagem natural** — sem abreviações crípticas
- [ ] Keywords de pages nomeadas como verbos + substantivo: `Fill Campo`, `Go To Página`, `Verify Elemento`
- [ ] Keywords de steps seguem Gherkin: `Dado`, `Quando`, `Então`, `E`
- [ ] Locators declarados em `*** Variables ***` com nomes em **MAIÚSCULAS** — nunca inline no corpo da keyword
- [ ] Preferência por `data-testid` sobre seletores CSS (`.classe`, `#id`) ou XPath
- [ ] Imports usam `${EXECDIR}` como raiz — sem paths relativos frágeis (`../`)
- [ ] `Wait For Elements State` usa `${DEFAULT_TIMEOUT}` — nunca valores hardcoded como `30s`

Consultar detalhes em [./references/rf-conventions.md](./references/rf-conventions.md).

### Passo 3 — Convenções Python

Para cada arquivo `.py` em `resources/libraries/`:

- [ ] Keywords decoradas com `@keyword("Nome Da Keyword")` do `robot.api.deco`
- [ ] Uso de `logger` do `robot.api` para logs — **nunca `print()`**
- [ ] Exceções tratadas e relançadas como `AssertionError` com mensagem descritiva
- [ ] PEP 8: indentação de 4 espaços, linhas ≤ 120 chars, nomes `snake_case`
- [ ] Docstrings em todas as funções públicas
- [ ] Sem `import *`; imports explícitos e organizados (stdlib → terceiros → locais)

Consultar detalhes em [./references/python-conventions.md](./references/python-conventions.md).

### Passo 4 — Segurança de Dados

- [ ] **Nenhuma credencial, senha, token ou chave** em arquivos `.resource`, `.robot` ou `.py`
- [ ] Secrets recuperados via `AwsParametersLib.Get SSM Parameter` — nunca via variável de ambiente exposta em log
- [ ] `.env` não commitado (verificar `.gitignore`); apenas `example.env` presente no repo
- [ ] `Log` de dados sensíveis usa `level=DEBUG` ou é suprimido — nunca `INFO` para senhas
- [ ] Nenhum dado pessoal real (CPF, cartão, e-mail real de usuário) hardcodado em `data/static.resource`

Consultar detalhes em [./references/security.md](./references/security.md).

### Passo 5 — Reaproveitamento e Camadas

- [ ] **Tests** (`tests/`): zero chamadas a `Fill Text`, `Click`, `Go To`, locators ou `FakerLibrary` diretamente
- [ ] **Steps** (`resources/steps/`): zero locators; apenas orquestração de keywords de pages
- [ ] **Pages** (`resources/pages/`): zero lógica de negócio; apenas ações atômicas de UI
- [ ] Nenhuma keyword duplicada entre arquivos — verificar se a lógica já existe em `base.resource` ou em outro page
- [ ] Estado compartilhado entre steps usa `Set Suite Variable` — nunca variáveis globais Python
- [ ] Screenshots capturados via `Save Screenshot` de `base.resource` — nunca `Take Screenshot` diretamente nos testes

### Passo 6 — Continuidade da Arquitetura

- [ ] Novo page object segue o padrão `<feature>_page.resource` com a estrutura: `Settings → Variables → Keywords`
- [ ] Novo step file segue o padrão `<feature>_steps.resource`
- [ ] Dados fixos em `data/static.resource`; dados gerados em runtime em `data/dynamic.resource`
- [ ] Nenhuma nova biblioteca Python criada para funcionalidade já disponível nas libs do projeto
- [ ] Configurações de ambiente (URLs, timeouts) em `config/variables.resource` — nunca espalhadas nos testes
- [ ] Imports em novos arquivos seguem o mesmo padrão dos existentes (`settings.resource` → `base.resource` → pages/steps)

### Passo 7 — Pipeline CI/CD

Se arquivos de pipeline foram modificados (`.yml`, `.yaml`, `.json` em `.github/workflows/`):

- [ ] Secrets referenciados como `${{ secrets.NOME }}` — nunca valores literais
- [ ] `ENVIRONMENT` parametrizável via `workflow_dispatch` ou matrix
- [ ] Etapa de `rfbrowser init` presente antes da execução dos testes
- [ ] Artefatos de resultado (`output.xml`, `log.html`, `report.html`) publicados via `actions/upload-artifact`
- [ ] Falha de teste não silenciada — `robot` retorna exit code não-zero em falha

---

## Relatório Final

Após completar todos os passos, gerar a seguinte mensagem **diretamente no chat**:

```
## 🔍 RF Pre-Commit Review — Resultado

### 🔴 Pontos Críticos (bloqueiam o commit)
> Itens que violam regras de segurança, quebram a arquitetura ou causarão falhas em runtime.

- [arquivo:linha] Descrição objetiva do problema e como corrigir

### 🟡 Pontos de Atenção (devem ser corrigidos antes do merge)
> Itens que violam convenções, reduzem manutenibilidade ou introduzem débito técnico.

- [arquivo:linha] Descrição objetiva do problema e como corrigir

### ✅ Aprovado sem ressalvas
> (Exibir apenas se não houver nenhum item acima)
Todos os critérios foram atendidos. Código pronto para commit.
```

**Regras do relatório:**
- Cada item deve citar o **arquivo e número de linha** quando aplicável
- Cada item deve incluir **como corrigir**, não apenas o que está errado
- Pontos Críticos: credenciais expostas, violação de camadas (locator em teste), timeout hardcoded em prod, `.env` commitado
- Pontos de Atenção: keyword sem `[Documentation]`, seletor CSS em vez de `data-testid`, keyword duplicada, `print()` em lib Python
- Se não houver itens em nenhuma categoria, exibir apenas a mensagem de aprovação

---

## Referências

- [RF Conventions](./references/rf-conventions.md) — indentação, locators, timeouts, imports
- [Python Conventions](./references/python-conventions.md) — decorators, logging, exceções, PEP 8
- [Security Checklist](./references/security.md) — secrets, dados sensíveis, .gitignore
- [Copilot Instructions](../../../.github/copilot-instructions.md) — convenções gerais do projeto
