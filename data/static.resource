*** Settings ***
Resource    ${EXECDIR}/config/settings.resource

*** Keywords ***
Get Static User Data
    [Documentation]    Retorna um dicionário com dados de usuário estáticos para testes.
    ${user_data}=    Create Dictionary    
    ...    first_name=User
    ...    last_name=Test
    ...    email=user.test@qa.com
    ...    password=password123