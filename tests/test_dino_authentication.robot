*** Settings ***
Resource         ${EXECDIR}/resources/base.resource
Resource         ${EXECDIR}/resources/pages/dino_register_page.resource
Resource         ${EXECDIR}/resources/steps/dino_authentication_steps.resource

Suite Setup      Suite Setup Load Environment
Test Setup       Open Browser
Test Teardown    Close Browser

*** Test Cases ***

CT_01: MAL EXEMPLO - Deve registrar um novo usuário preenchendo o formulário diretamente no teste
    # Gerar dados de usuário aleatórios
    ${random_first_name}=    FakerLibrary.First Name
    ${random_last_name}=    FakerLibrary.Last Name
    ${random_email}=    FakerLibrary.Email
    ${random_password}=    FakerLibrary.Password    length=10
    # Acessar a página de registro
    Go To    ${BASE_URL}/signup
    # Preencher o formulário de registro
    Fill Text    data-testid=signup-firstname-input    ${random_first_name}
    Fill Text    data-testid=signup-lastname-input     ${random_last_name}
    Fill Text    data-testid=signup-email-input        ${random_email}
    Fill Text    data-testid=signup-password-input     ${random_password}
    # Submeter o formulário de registro
    Click    data-testid=signup-submit-button
    # Verificar se o registro foi bem-sucedido
    Wait For Elements State    text=Account created successfully! Please login to continue.    visible    timeout=10s
    # Verificar se a URL contém "/login" após o registro
    Wait For Navigation    url=${BASE_URL}/login    timeout=10s

    #! O problema surge quando precisamos executar vários testes que envolvem o registro de usuários
    #! Isso leva à duplicação de código, tornando a manutenção difícil e aumentando o risco de erros.

CT_02: EXEMPLO COM ENCAPSULAMENTO - Deve registrar um novo usuário usando palavras-chave reutilizáveis
    ${user_data}=    Generate Random User Data
    
    Go To Registration Page
    Fill Registration Form    
    ...    first_name=${user_data.first_name}    
    ...    last_name=${user_data.last_name}    
    ...    email=${user_data.email}    
    ...    password=${user_data.password}
    Submit Registration Form
    Verify Message Of Registration Success
    Verify Redirect To Login Page

    #* Este exemplo é uma melhoria significativa em relação ao primeiro, pois encapsula a lógica de geração de dados e 
    #* interação com a página em palavras-chave reutilizáveis. Isso torna os testes mais limpos, fáceis de ler e manter.

CT_03: EXEMPLO COM GHERKIN - Deve registrar um novo usuário usando Gherkin
    Dado que possuo dados de usuário aleatórios para cadastro
    E que esteja na página de cadastro
    Quando cadastrar um novo usuário
    Então deverá ser exibido a mensagem de cadastro ser bem-sucedido 
    E deverá ser redirecionado para a página de login

CT_04: Busca de parâmetros no AWS Parameter
    ${parameter_name}=    Set Variable    example_secure_string
    ${parameter_value}=    Get SSM Parameter    ${parameter_name}
    Log    O valor do parâmetro '${parameter_name}' é: ${parameter_value}    level=DEBUG