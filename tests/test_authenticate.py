import getpass
import os

import aws_azuread_login

ENTRY_URL = input('Entry URL: ')
USERNAME = input('Username: ')
PASSWORD = getpass.getpass('Password: ')
CODE = input('OTP: ')

def test_non_interactive_auth():
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
    creds = []
    for role in roles:
        try:
            creds.append(role.get_credentials())
            print('.', end='', flush=True)
        except:
            print('!', end='', flush=True)
    assert(len(creds) > 0)

def test_interactive_auth():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                stay_signed_in=False,
                headless=False)
    assert(len(roles) > 0)

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


