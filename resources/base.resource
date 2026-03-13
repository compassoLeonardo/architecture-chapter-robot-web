*** Settings ***
Resource    ${EXECDIR}/config/settings.resource
Resource    ${EXECDIR}/data/static.resource
Resource    ${EXECDIR}/data/dynamic.resource

*** Keywords ***
Open Browser
    [Documentation]    Abre o navegador com configurações padrão
    [Arguments]    ${browser}=${BROWSER_TYPE}    ${headless}=${HEADLESS}   ${args}=${ARGS}
    New Browser    ${browser}    headless=${headless}    args=${args}
    New Context    viewport={'width': ${VIEWPORT_WIDTH}, 'height': ${VIEWPORT_HEIGHT}}
    New Page

Save Screenshot
    [Documentation]    Salva um screenshot da página atual. O nome do arquivo inclui o nome do teste e um timestamp.
    ${time_stamp}=    Get Current Date    result_format=%d%m%Y_%H%M%S
    ${file_name}=    Catenate    SEPARATOR=_    screenshot    ${TEST NAME}    ${time_stamp}
    Take Screenshot    ${file_name}

Wait Until URL Contains
    [Documentation]    Aguarda até que a URL contenha um texto específico
    [Arguments]    ${text}    ${retry_interval}=${RETRY_INTERVAL}    ${retry_attempts}=${RETRY_ATTEMPTS}
    ${current_url}=    Get Url
    Wait Until Keyword Succeeds    ${retry_attempts}    ${retry_interval}    Should Contain    ${current_url}    ${text}