*** Settings ***
Resource    ${EXECDIR}/config/settings.resource

*** Keywords ***
Generate Random User Data
    [Documentation]    Generates random user data for testing
    ${random_first_name}=    FakerLibrary.First Name
    ${random_last_name}=    FakerLibrary.Last Name
    ${random_email}=    FakerLibrary.Email
    ${random_password}=    FakerLibrary.Password    length=10

    ${user_data}=    Create Dictionary    
    ...    first_name=${random_first_name}
    ...    last_name=${random_last_name}
    ...    email=${random_email}
    ...    password=${random_password}
    RETURN    ${user_data}

Generate User Data With Temp Email
    [Documentation]    
    ...    Generates random user data with a real temporary email address from TempMail.lol.
    ...    Returns a dictionary with user data and email credentials (token).
    ...
    ...    Returns:
    ...        Dictionary with keys: nome, email, password, administrador, email_token
    ...
    ...    Example:
    ...        | ${user_data}= | Generate User Data With Temp Email |
    ...        | ${email}= | Set Variable | ${user_data['email']} |
    ...        | ${token}= | Set Variable | ${user_data['email_token']} |
    
    ${user_data}=    Generate Random User Data
    
    # Criar e-mail temporário real
    ${email_data}=    TempEmailLib.Create Temp Email
    ${temp_email}=    Set Variable    ${email_data['email']}
    ${email_token}=    Set Variable    ${email_data['token']}
    ${email_id}=    Set Variable    ${email_data['id']}
    
    # Criar dicionário com dados do usuário
    ${user_data}=    Create Dictionary    
    ...    first_name=${user_data['first_name']}
    ...    last_name=${user_data['last_name']}
    ...    password=${user_data['password']}
    ...    email=${temp_email}
    ...    email_token=${email_token}
    ...    email_id=${email_id}
    
    RETURN    ${user_data}