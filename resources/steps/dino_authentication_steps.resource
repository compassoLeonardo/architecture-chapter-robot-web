*** Settings ***
Documentation    Keywords de negócio (BDD/Gherkin) para cenários de autenticação na aplicação Dino.
Resource         ${EXECDIR}/resources/base.resource
Resource         ${EXECDIR}/resources/pages/dino_register_page.resource

*** Keywords ***
Dado que possuo dados de usuário aleatórios para cadastro
    [Documentation]    Gera dados de usuário aleatórios usando a biblioteca FakerLibrary e os armazena em uma variável de dicionário.
    ${user_data}=    Generate Random User Data
    Set Suite Variable    ${user_data}
    
E que esteja na página de cadastro
    Go To Registration Page

Quando cadastrar um novo usuário
    Fill Registration Form    
    ...    first_name=${user_data.first_name}    
    ...    last_name=${user_data.last_name}    
    ...    email=${user_data.email}    
    ...    password=${user_data.password}
    Submit Registration Form

Então deverá ser exibido a mensagem de cadastro ser bem-sucedido 
    Verify Message Of Registration Success

E deverá ser redirecionado para a página de login
    Verify Redirect To Login Page