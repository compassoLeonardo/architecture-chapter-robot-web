# Python Conventions Reference

Regras de convenção para bibliotecas Python customizadas em `resources/libraries/`.

## Estrutura de Arquivo

```python
# 1. Imports: stdlib → terceiros → locais
import os
from typing import Optional

import boto3
from robot.api import logger
from robot.api.deco import keyword

# 2. Classe com nome em PascalCase
class MyCustomLib:

    # 3. ROBOT_LIBRARY_SCOPE define o ciclo de vida
    ROBOT_LIBRARY_SCOPE = "SUITE"

    # 4. Toda função pública tem docstring
    @keyword("Get My Data")
    def get_my_data(self, param: str) -> dict:
        """Descrição concisa do que a keyword faz.

        Args:
            param: Descrição do parâmetro.

        Returns:
            Dicionário com os dados obtidos.

        Raises:
            AssertionError: Se os dados não puderem ser obtidos.
        """
        ...
```

## Logging

- **Sempre** usar `logger` do `robot.api` — nunca `print()`
- Dados sensíveis apenas em `logger.debug()` — nunca `logger.info()` ou `logger.warn()`

```python
# CORRETO
from robot.api import logger

logger.info(f"Conectando ao SSM na região {region}")
logger.debug(f"Token obtido: {token}")  # só aparece com --loglevel DEBUG

# ERRADO
print(f"Token: {token}")
```

## Tratamento de Exceções

- Capturar exceções específicas — nunca `except Exception` genérico sem necessidade
- Relançar como `AssertionError` com mensagem descritiva para o Robot Framework

```python
# CORRETO
try:
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]
except ssm.exceptions.ParameterNotFound:
    raise AssertionError(f"Parâmetro SSM não encontrado: '{name}'")
except Exception as e:
    raise AssertionError(f"Erro ao obter parâmetro SSM '{name}': {e}")

# ERRADO — engole o erro
try:
    return ssm.get_parameter(Name=name)["Parameter"]["Value"]
except:
    return None
```

## Decorators de Keyword

- Todo método exposto ao Robot Framework deve ter `@keyword("Nome Em Linguagem Natural")`
- Nome em inglês ou português — **consistente com o padrão do projeto**
- Métodos auxiliares internos (não expostos) **não** recebem `@keyword`

```python
from robot.api.deco import keyword

@keyword("Get SSM Parameter")
def get_ssm_parameter(self, name: str) -> str:
    return self._fetch_from_ssm(name)   # método auxiliar, sem @keyword

def _fetch_from_ssm(self, name: str) -> str:
    ...
```

## PEP 8 — Resumo dos Pontos Críticos

| Regra | Valor |
|---|---|
| Indentação | 4 espaços |
| Comprimento máximo de linha | 120 caracteres |
| Nomes de funções/variáveis | `snake_case` |
| Nomes de classes | `PascalCase` |
| Constantes de módulo | `UPPER_SNAKE_CASE` |
| Imports `*` | **Proibido** |
| Linha em branco entre métodos | 1 linha; 2 entre classes de topo |

## Type Hints

Recomendado em funções públicas para melhor documentação:

```python
def create_temp_email(self) -> dict[str, str]:
    ...

def get_ssm_parameter(self, name: str, decrypt: bool = True) -> str:
    ...
```
