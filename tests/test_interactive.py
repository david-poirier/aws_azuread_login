import getpass
import os

import aws_azuread_login

ENTRY_URL = os.environ['AWS_AZUREAD_ENTRY_URL']


def test_auth():
    roles = aws_azuread_login.authenticate(
                ENTRY_URL,
                stay_signed_in=False,
                headless=False)
    assert(len(roles) > 0)

