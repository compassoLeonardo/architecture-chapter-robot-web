"""
Mail.tm Temporary Email Library for Robot Framework
Provides temporary email functionality for testing email verification flows.

API Documentation: https://docs.mail.tm/
"""

import requests
import time
import re
import random
import string
from robot.api import logger
from robot.api.deco import keyword


# Global configuration
BASE_URL = 'https://api.mail.tm'
SESSION = requests.Session()
SESSION.headers.update({
    'Accept': 'application/json',
    'Content-Type': 'application/json'
})
EMAIL_ACCOUNTS = {}  # Store created emails: {email: {token, id, password}}


@keyword("Create Temp Email")
def create_temp_email(custom_username=None):
    """Create a new temporary email address using mail.tm.
    
    Arguments:
        - custom_username: Optional custom username (the part before @)
        
    Returns:
        Dictionary with 'email', 'token', 'id', 'password' keys
        
    Examples:
        | ${email_data}= | Create Temp Email |
        | ${email}= | Set Variable | ${email_data['email']} |
        | ${token}= | Set Variable | ${email_data['token']} |
        
        | ${email_data}= | Create Temp Email | custom_username=mytest |
    """
    try:
        # Get available domains
        logger.info("Getting available domains from mail.tm")
        response = SESSION.get(f"{BASE_URL}/domains")
        response.raise_for_status()
        domains_data = response.json()
        
        logger.debug(f"Domains data type: {type(domains_data)}")
        logger.debug(f"Domains data: {domains_data}")
        
        # Handle both dict and list responses
        if isinstance(domains_data, dict):
            domains_list = domains_data.get('hydra:member', [])
        elif isinstance(domains_data, list):
            domains_list = domains_data
        else:
            raise AssertionError(f"Unexpected domains data type: {type(domains_data)}")
        
        if not domains_list:
            raise AssertionError("No domains available from mail.tm API")
        
        # Get first active domain
        domain = domains_list[0]['domain']
        
        # Generate or use custom username
        if custom_username:
            username = custom_username
        else:
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        email = f"{username}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + '!A1'
        
        # Create account
        account_data = {
            'address': email,
            'password': password
        }
        
        logger.info(f"Creating account for: {email}")
        response = SESSION.post(f"{BASE_URL}/accounts", json=account_data)
        response.raise_for_status()
        account_info = response.json()
        account_id = account_info['id']
        
        # Get auth token
        auth_data = {
            'address': email,
            'password': password
        }
        
        logger.info("Getting authentication token")
        response = SESSION.post(f"{BASE_URL}/token", json=auth_data)
        response.raise_for_status()
        token_info = response.json()
        token = token_info['token']
        
        # Store for later use
        EMAIL_ACCOUNTS[email] = {
            'token': token,
            'id': account_id,
            'password': password
        }
        
        result = {
            'email': email,
            'token': token,
            'id': account_id,
            'password': password
        }
        
        logger.info(f"Created temporary email: {email}")
        return result
        
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Failed to create temporary email: {e}")
    except Exception as e:
        raise AssertionError(f"Error creating temporary email: {e}")
    
@keyword("Get Email Inbox")
def get_email_inbox(email_address):
    """Get all emails from inbox.
    
    Arguments:
        - email_address: The temporary email address
        
    Returns:
        List of email dictionaries with 'id', 'from', 'subject', 'intro' keys
        
    Examples:
        | ${inbox}= | Get Email Inbox | ${email} |
        | Length Should Be | ${inbox} | 1 |
    """
    try:
        if email_address not in EMAIL_ACCOUNTS:
            raise AssertionError(f"Email {email_address} not found in stored accounts")
        
        token = EMAIL_ACCOUNTS[email_address]['token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = SESSION.get(f"{BASE_URL}/messages", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        emails = data.get('hydra:member', [])
        
        logger.info(f"Retrieved {len(emails)} email(s) from {email_address}")
        return emails
        
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Failed to get inbox for {email_address}: {e}")
    except Exception as e:
        raise AssertionError(f"Error getting inbox: {e}")

@keyword("Get Email Content")
def get_email_content(email_address, email_id):
    """Get full content of a specific email.
    
    Arguments:
        - email_address: The temporary email address
        - email_id: The ID of the email to retrieve
        
    Returns:
        Dictionary with full email details including 'text', 'html' body
        
    Examples:
        | ${inbox}= | Get Email Inbox | ${email} |
        | ${email_id}= | Set Variable | ${inbox[0]['id']} |
        | ${content}= | Get Email Content | ${email} | ${email_id} |
    """
    try:
        if email_address not in EMAIL_ACCOUNTS:
            raise AssertionError(f"Email {email_address} not found in stored accounts")
        
        token = EMAIL_ACCOUNTS[email_address]['token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = SESSION.get(f"{BASE_URL}/messages/{email_id}", headers=headers)
        response.raise_for_status()
        
        content = response.json()
        logger.info(f"Retrieved email content for ID {email_id}")
        return content
        
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Failed to get email content: {e}")
    except Exception as e:
        raise AssertionError(f"Error getting email content: {e}")

@keyword("Get Latest Email")
def get_latest_email(email_address, timeout=60, poll_interval=3):
    """Wait for and retrieve the latest email from inbox with full content.
    
    Arguments:
        - email_address: The temporary email address
        - timeout: Maximum time to wait in seconds (default: 60)
        - poll_interval: Time between checks in seconds (default: 3)
        
    Returns:
        Dictionary with full email details or None if timeout reached
        
    Examples:
        | ${email}= | Get Latest Email | ${email_address} |
        | Should Not Be Equal | ${email} | ${None} |
        | Log | Subject: ${email['subject']} |
        
        | ${email}= | Get Latest Email | ${email_address} | timeout=30 |
    """
    logger.info(f"Waiting for email at {email_address} (timeout: {timeout}s)")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        inbox = get_email_inbox(email_address)
        
        if inbox and len(inbox) > 0:
            latest_info = inbox[0]  # Most recent email
            email_id = latest_info.get('id')
            
            # Get full content
            full_email = get_email_content(email_address, email_id)
            logger.info(f"Email received! Subject: {full_email.get('subject', 'N/A')}")
            return full_email
        
        time.sleep(poll_interval)
        logger.debug(f"No emails yet, waiting... ({int(time.time() - start_time)}s elapsed)")
    
    logger.warn(f"Timeout reached ({timeout}s) - no emails received at {email_address}")
    return None

@keyword("Get Email By Subject")
def get_email_by_subject(email_address, subject_pattern, timeout=60, poll_interval=3):
    """Wait for and retrieve email matching subject pattern with full content.
    
    Arguments:
        - email_address: The temporary email address
        - subject_pattern: Text or regex pattern to match in subject
        - timeout: Maximum time to wait in seconds (default: 60)
        - poll_interval: Time between checks in seconds (default: 3)
        
    Returns:
        Dictionary with full email details or None if not found
        
    Examples:
        | ${email}= | Get Email By Subject | ${email_address} | Verification Code |
        | ${email}= | Get Email By Subject | ${email_address} | Welcome.*Account |
    """
    logger.info(f"Waiting for email with subject matching '{subject_pattern}' at {email_address}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        inbox = get_email_inbox(email_address)
        
        for email_info in inbox:
            subject = email_info.get('subject', '')
            if re.search(subject_pattern, subject, re.IGNORECASE):
                # Get full content
                email_id = email_info.get('id')
                full_email = get_email_content(email_address, email_id)
                logger.info(f"Found matching email! Subject: {subject}")
                return full_email
        
        time.sleep(poll_interval)
        logger.debug(f"No matching emails yet... ({int(time.time() - start_time)}s elapsed)")
    
    logger.warn(f"Timeout reached ({timeout}s) - no email matching '{subject_pattern}'")
    return None

@keyword("Get Verification Code From Email")
def get_verification_code_from_email(email_data, pattern=r'\b\d{4,8}\b'):
    """Extract verification code from email body.
    
    Arguments:
        - email_data: Email dictionary returned from Get Latest Email or Get Email By Subject
        - pattern: Regex pattern to extract code (default: 4-8 digit numbers)
        
    Returns:
        The extracted verification code as string, or None if not found
        
    Examples:
        | ${email}= | Get Latest Email | ${email_address} |
        | ${code}= | Get Verification Code From Email | ${email} |
        | Should Not Be Equal | ${code} | ${None} |
        | Log | Verification code: ${code} |
        
        | ${code}= | Get Verification Code From Email | ${email} | pattern=[A-Z0-9]{6} |
    """
    if not email_data:
        logger.warn("No email data provided")
        return None
    
    # Try to extract from both text and HTML body (mail.tm uses 'text' and 'html')
    body_text = email_data.get('text', email_data.get('intro', ''))
    body_html = email_data.get('html', [])
    if isinstance(body_html, list):
        body_html = ' '.join(body_html)
    
    combined_body = f"{body_text} {body_html}"
    
    match = re.search(pattern, combined_body)
    
    if match:
        code = match.group(0)
        logger.info(f"Extracted verification code: {code}")
        return code
    
    logger.warn(f"No verification code found matching pattern: {pattern}")
    return None

@keyword("Delete Temp Email")
def delete_temp_email(email_address):
    """Delete temporary email address from internal storage and mail.tm server.
    
    Arguments:
        - email_address: The temporary email address to remove
        
    Examples:
        | Delete Temp Email | ${email_address} |
    """
    if email_address in EMAIL_ACCOUNTS:
        try:
            token = EMAIL_ACCOUNTS[email_address]['token']
            account_id = EMAIL_ACCOUNTS[email_address]['id']
            
            headers = {'Authorization': f'Bearer {token}'}
            SESSION.delete(f"{BASE_URL}/accounts/{account_id}", headers=headers)
            
            del EMAIL_ACCOUNTS[email_address]
            logger.info(f"Deleted {email_address} from server and internal storage")
        except Exception as e:
            logger.warn(f"Error deleting {email_address}: {e}")
    else:
        logger.debug(f"Email {email_address} not found in internal storage")

@keyword("Get Email From Address")
def get_email_from_address(email_data):
    """Extract sender's email address from email data.
    
    Arguments:
        - email_data: Email dictionary returned from Get Latest Email or Get Email By Subject
        
    Returns:
        Sender's email address as string
        
    Examples:
        | ${email}= | Get Latest Email | ${email_address} | ${token} |
        | ${sender}= | Get Email From Address | ${email} |
        | Should Contain | ${sender} | @example.com |
    """
    if not email_data:
        return None
    return email_data.get('from', '')

@keyword("Get Email Subject")
def get_email_subject(email_data):
    """Extract subject from email data.
    
    Arguments:
        - email_data: Email dictionary returned from Get Latest Email or Get Email By Subject
        
    Returns:
        Email subject as string
        
    Examples:
        | ${email}= | Get Latest Email | ${email_address} | ${token} |
        | ${subject}= | Get Email Subject | ${email} |
        | Should Be Equal | ${subject} | Welcome to Our Service |
    """
    if not email_data:
        return None
    return email_data.get('subject', '')

@keyword("Get Email Body Text")
def get_email_body_text(email_data):
    """Extract plain text body from email data.
    
    Arguments:
        - email_data: Email dictionary returned from Get Latest Email or Get Email By Subject
        
    Returns:
        Email body as plain text string
        
    Examples:
        | ${email}= | Get Latest Email | ${email_address} |
        | ${body}= | Get Email Body Text | ${email} |
        | Should Contain | ${body} | verification code |
    """
    if not email_data:
        return None
    return email_data.get('text', email_data.get('intro', ''))