*** Settings ***
Documentation   
...              Este arquivo centraliza todas as variáveis não sensíveis e configurações
...              que podem variar entre ambientes e entre execuções.
...              As variáveis são definidas usando a sintaxe de ambiente do Robot Framework,
...              permitindo que sejam facilmente sobrescritas por variáveis de ambiente do sistema
...              ou por argumentos de linha de comando durante a execução dos testes.

*** Variables ***
#  Browser Settings Variables
${BROWSER_TYPE}      %{BROWSER=chromium}    # chromium, firefox, webkit
${HEADLESS}          %{HEADLESS=False}
@{ARGS}              --disable-blink-features=AutomationControlled
${VIEWPORT_WIDTH}    %{VIEW_W=1280}
${VIEWPORT_HEIGHT}   %{VIEW_H=720}

#  Environment Variables
${ENVIRONMENT}    %{ENVIRONMENT=PROD}    # PROD, HML

&{BASE_URL}
...    PROD= https://storedemo.testdino.com
...    HML= https://storedemo.hml.testdino.com

&{API_BASE_URL}
...    PROD= https://storedemo-api.testdino.com/api
...    HML= https://storedemo-api.hml.testdino.com/api

#  Timeouts and Retry Settings
${DEFAULT_TIMEOUT}         30s
${API_TIMEOUT}             10s
${RETRY_ATTEMPTS}          3x
${RETRY_INTERVAL}          1s
${LOG_LEVEL}               INFO
