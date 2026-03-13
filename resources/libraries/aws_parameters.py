"""
AWS SSM Parameter Store Library for Robot Framework
Provides keywords to retrieve parameters from AWS Systems Manager Parameter Store.

Credentials are resolved through the AWS default credential provider chain.
The .env file is loaded only to help local development when desired.

Supported authentication sources include:
- GitHub Actions OIDC credentials (via aws-actions/configure-aws-credentials)
- Environment variables from .env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
- Local AWS profile (AWS_PROFILE / ~/.aws/credentials)
"""

import os
import boto3
import botocore.exceptions
from dotenv import load_dotenv, find_dotenv
from robot.api import logger
from robot.api.deco import keyword


load_dotenv(find_dotenv(usecwd=True), override=False)


@keyword("Get SSM Parameter")
def get_ssm_parameter(parameter_name, with_decryption=True):
    """Retrieve a single parameter value from AWS SSM Parameter Store.

    Arguments:
        - parameter_name: Full name or path of the SSM parameter (e.g. /myapp/db/password)
        - with_decryption: Decrypt SecureString values (default: True)

    Returns:
        The parameter value as a string

    Examples:
        | ${value}=    | Get SSM Parameter | /myapp/prod/db_password |
        | ${value}=    | Get SSM Parameter | /myapp/prod/api_key | with_decryption=False |
    """
    try:
        ssm = _create_ssm_client()
        logger.info(f"Fetching SSM parameter: {parameter_name}")
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=with_decryption)
        value = response['Parameter']['Value']
        logger.info(f"Successfully retrieved parameter: {parameter_name}")
        return value
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        raise AssertionError(f"Failed to get SSM parameter '{parameter_name}' [{error_code}]: {e}")
    except Exception as e:
        raise AssertionError(f"Error retrieving SSM parameter '{parameter_name}': {e}")


@keyword("Get SSM Parameters By Path")
def get_ssm_parameters_by_path(path, with_decryption=True):
    """Retrieve all parameters under a given path from AWS SSM Parameter Store.

    Handles pagination automatically and returns all matching parameters.

    Arguments:
        - path: The SSM path prefix to search (e.g. /myapp/prod/)
        - with_decryption: Decrypt SecureString values (default: True)

    Returns:
        Dictionary mapping parameter names to their values: {name: value}

    Examples:
        | &{params}=    | Get SSM Parameters By Path | /myapp/prod/ |
        | Log           | DB password: ${params}[/myapp/prod/db_password] |

        | &{params}=    | Get SSM Parameters By Path | /myapp/prod/ | with_decryption=False |
    """
    try:
        ssm = _create_ssm_client()
        logger.info(f"Fetching SSM parameters by path: {path}")

        parameters = {}
        kwargs = {
            'Path': path,
            'WithDecryption': with_decryption,
            'Recursive': True
        }

        while True:
            response = ssm.get_parameters_by_path(**kwargs)
            for param in response.get('Parameters', []):
                parameters[param['Name']] = param['Value']

            next_token = response.get('NextToken')
            if not next_token:
                break
            kwargs['NextToken'] = next_token

        logger.info(f"Retrieved {len(parameters)} parameter(s) from path: {path}")
        return parameters
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        raise AssertionError(f"Failed to get SSM parameters by path '{path}' [{error_code}]: {e}")
    except Exception as e:
        raise AssertionError(f"Error retrieving SSM parameters by path '{path}': {e}")


def _create_ssm_client():
    """Create and return an SSM client using AWS default credential resolution."""
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
    profile = os.environ.get('AWS_PROFILE')

    if profile:
        logger.info(f"Creating AWS session using profile '{profile}' in region '{region}'")
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        logger.info(f"Creating AWS session using default provider chain in region '{region}'")
        session = boto3.Session(region_name=region)

    return session.client('ssm')
