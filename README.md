# Architecture Chapter — Robot Framework Web

> **Chapter Técnico · iStudio Quality Engineer · AI/R Company**
> 21 de maio de 2026

Repositório de apoio ao Chapter Técnico sobre **arquitetura de automação de testes web** com Robot Framework e Browser Library (Playwright). O projeto demonstra, de forma progressiva, a evolução de um teste sem estrutura até uma solução em camadas, manutenível e escalável. Possui exemplos de bibliotecas para parametrização de dados na AWS e e-mail temporário, além de exemplos de documentações e agentes para ferramentas de Inteligência Artificial.

A aplicação sob teste é a **Dino Store** — `storedemo.testdino.com`.

---

## Estrutura do Projeto

```
config/
  settings.resource   → Libraries, Suite Setup e inicialização de ambiente
  variables.resource  → Variáveis não sensíveis (browser, timeouts, URLs por ambiente)

data/
  static.resource     → Dados de teste fixos e reproduzíveis
  dynamic.resource    → Keywords de geração de dados aleatórios em runtime (FakerLibrary, TempEmail)

resources/
  base.resource       → Keywords utilitárias globais (Open Browser, Save Screenshot)
  libraries/          → Bibliotecas Python customizadas para integrações externas
  pages/              → Page Objects: locators e ações atômicas de UI
  steps/              → Steps BDD: orquestração do fluxo de negócio

tests/                → Casos de teste (.robot): apenas cenários, sem lógica de implementação
```

> **Regra de ouro:** cada camada conhece apenas a imediatamente abaixo. Testes → Steps → Pages → Browser Library.

---

## Pré-requisitos

| Ferramenta | Versão mínima                                 |
| ---------- | ----------------------------------------------- |
| Python     | 3.9+                                            |
| Node.js    | 18+ (exigido pelo Browser Library / Playwright) |
| pip        | qualquer recente                                |

---

## Instalação

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd architecture-chapter-robot-web
```

**2. Crie e ative um ambiente virtual**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

**3. Instale as dependências Python**

```bash
pip install -r requirements.txt
```

**4. Inicialize o Browser Library (Playwright)**

```bash
rfbrowser init
```

**5. Configure as variáveis de ambiente**

Copie o arquivo de exemplo e preencha com suas credenciais AWS:

```bash
cp example.env .env
```

O arquivo `.env` nunca deve ser commitado. Ele é usado localmente para autenticação com o AWS SSM Parameter Store.

---

## Executando os Testes

**Executar todos os testes (ambiente PROD, browser padrão):**

```bash
robot tests/
```

**Executar com browser e headless configuráveis:**

```bash
robot --variable BROWSER:chrome --variable HEADLESS:True tests/
```

**Executar por tag (ex: apenas exemplos com Gherkin):**

```bash
robot --include Gherkin tests/
```

**Selecionar ambiente:**

```bash
robot --variable ENVIRONMENT:HML tests/
```

**Executar em paralelo com pabot:**

```bash
pabot --processes 4 tests/
```

---

## Variáveis de Ambiente Suportadas

| Variável       | Padrão      | Descrição                                               |
| --------------- | ------------ | --------------------------------------------------------- |
| `ENVIRONMENT` | `PROD`     | Ambiente alvo (`PROD` ou `HML`)                       |
| `BROWSER`     | `chromium` | Engine do browser (`chromium`, `firefox`, `webkit`) |
| `HEADLESS`    | `False`    | Executar sem interface gráfica                           |
| `VIEW_W`      | `1280`     | Largura do viewport em pixels                             |
| `VIEW_H`      | `720`      | Altura do viewport em pixels                              |

Variáveis sensíveis (credenciais AWS) são carregadas via arquivo `.env` local ou secrets de CI/CD — nunca hardcodadas no repositório.

---

## Casos de Teste — Evolução Didática

| Caso      | Tag                    | Descrição                                             |
| --------- | ---------------------- | ------------------------------------------------------- |
| `CT_01` | `Sem Encapsulamento` | Mau exemplo: lógica de UI e dados diretamente no teste |
| `CT_02` | `Encapsulamento`     | Uso de Page Objects e keywords reutilizáveis           |
| `CT_03` | `Gherkin`            | Sintaxe BDD com Steps em linguagem natural              |

---

## Leitura Complementar

- [ABOUT_ARCHITECTURE.md](ABOUT_ARCHITECTURE.md) — documento de arquitetura completo com decisões de design e exemplos por camada
- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Browser Library Docs](https://marketsquare.github.io/robotframework-browser/Browser.html)

---

## Licença

Distribuído sob a licença descrita em [LICENSE](LICENSE).
