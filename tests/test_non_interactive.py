import getpass
import os

import aws_azuread_login

ENTRY_URL = os.environ['AWS_AZUREAD_ENTRY_URL']
USERNAME = input('Username: ')
PASSWORD = getpass.getpass('Password: ')
CODE = input('OTP: ')

def test_auth():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False,
                headless=False)
    assert(len(roles) > 0)

def test_get_credentials():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False,
                headless=False)
    assert(len(roles) > 0)

    if len(roles) > 3:
        roles = roles[:3]

    creds = []
    for role in roles]:
        try:
            creds.append(role.get_credentials())
            print('.', end='', flush=True)
        except:
            print('!', end='', flush=True)
    assert(len(creds) > 0)

def test_get_multiple_credentials():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False,
                headless=False)
    assert(len(roles) > 0)
    creds = aws_azuread_login.get_multiple_credentials(roles)
    assert(len(creds) > 0)

def test_roles_on_creds():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False,
                headless=False)
    creds = roles[0].get_credentials()
    assert(creds.role.account != None)

