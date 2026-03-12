*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    OperatingSystem
Library    String
Library    Browser
Library    DateTime
Library    dotenv
Library    FakerLibrary

Library    ${EXECDIR}/resources/libraries/temp_email.py    WITH NAME    TempEmailLib
Resource   ${EXECDIR}/config/variables.resource

*** Keywords ***
Suite Setup Load Environment
    Load Dotenv    dotenv_path=${EXECDIR}/.env
    Log    Loaded Environment: ${ENVIRONMENT}    level=DEBUG
    Set Base URL For Environment

Set Base URL For Environment
    [Documentation]
    ...    Define as URLs base para a aplicação e API com base no ambiente selecionado.

    ${environment_upper}=    Convert To Uppercase    ${ENVIRONMENT}
    ${base_url}=    Get From Dictionary    ${BASE_URL}    ${environment_upper}
    Set Global Variable    ${BASE_URL}    ${base_url}
    ${api_base_url}=    Get From Dictionary    ${API_BASE_URL}    ${environment_upper}
    Set Global Variable    ${API_BASE_URL}    ${api_base_url}
    Log    Base URL set to: ${BASE_URL}    level=DEBUG
    Log    API Base URL set to: ${API_BASE_URL}    level=DEBUG