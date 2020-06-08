import asyncio
import getpass
import os

import aws_azuread_login

ENTRY_URL = input('Entry URL: ')
USERNAME = input('Username: ')
PASSWORD = getpass.getpass('Password: ')
CODE = input('OTP: ')

def test_non_interactive_auth():
    roles = asyncio.get_event_loop().run_until_complete(
            aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False))
    assert(len(roles) > 0)

def test_get_credentials():
    roles = asyncio.get_event_loop().run_until_complete(
            aws_azuread_login.authenticate(
                ENTRY_URL,
                username=USERNAME,
                password=PASSWORD,
                code=CODE,
                stay_signed_in=False))
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
            aws_azuread_login.authenticate(
                ENTRY_URL,
                stay_signed_in=False))
    assert(len(roles) > 0)


