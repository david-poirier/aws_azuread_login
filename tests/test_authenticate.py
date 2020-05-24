import asyncio
import os

import aws_azuread_login

ENTRY_URL = os.environ['AZUREAD_ENTRY_URL']
USERNAME = os.environ.get('AZUREAD_USERNAME')
PASSWORD = os.environ.get('AZUREAD_PASSWORD')
CODE = os.environ.get('AZUREAD_CODE')

def test_non_interactive_auth():
    roles = asyncio.get_event_loop().run_until_complete(
            aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE))
    assert(len(roles) > 0)

def test_get_credentials():
    roles = asyncio.get_event_loop().run_until_complete(
            aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE))
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
    roles = asyncio.get_event_loop().run_until_complete(
            aws_azuread_login.authenticate(ENTRY_URL))
    assert(len(roles) > 0)


