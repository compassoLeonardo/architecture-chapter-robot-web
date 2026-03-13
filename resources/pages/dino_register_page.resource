*** Settings ***
Resource    ${EXECDIR}/config/settings.resource
Resource    ${EXECDIR}/resources/base.resource

*** Variables ***
${FIRST_NAME_INPUT}              data-testid=signup-firstname-input
${LAST_NAME_INPUT}               data-testid=signup-lastname-input
${EMAIL_INPUT}                   data-testid=signup-email-input
${PASSWORD_INPUT}                data-testid=signup-password-input
${SUBMIT_BUTTON}                data-testid=signup-submit-button
${REGISTER_SUCCESS_MESSAGE}      text=Account created successfully! Please login to continue.

*** Keywords ***
Go To Registration Page
    [Documentation]    Navega para a página de registro da aplicação.
    Go To    ${BASE_URL}/signup

Fill Registration Form
    [Documentation]    Preenche o formulário de registro com os dados fornecidos.
    [Arguments]    ${first_name}    ${last_name}    ${email}    ${password}
    Fill Text    ${FIRST_NAME_INPUT}    ${first_name}
    Fill Text    ${LAST_NAME_INPUT}     ${last_name}
    Fill Text    ${EMAIL_INPUT}         ${email}
    Fill Text    ${PASSWORD_INPUT}      ${password}

Submit Registration Form
    [Documentation]    Submete o formulário de registro.
    Click    ${SUBMIT_BUTTON}

Verify Message Of Registration Success
    [Documentation]    Verifica se o registro foi bem-sucedido, aguardando a mensagem de sucesso e a navegação para a página de login.
    Wait For Elements State    ${REGISTER_SUCCESS_MESSAGE}    visible    timeout=${DEFAULT_TIMEOUT}

Verify Redirect To Login Page
    Wait For Navigation    url=${BASE_URL}/login    timeout=${DEFAULT_TIMEOUT}