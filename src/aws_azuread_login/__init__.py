import asyncio
import base64
import getpass
import json
import os
import sys
import urllib
import xml.etree.ElementTree

import boto3
import bs4
import keyring
import pyppeteer


class AwsRole:
    def __init__(self, saml_assertion, role_arn, principal_arn):
        self.saml_assertion = saml_assertion
        self.role_arn = role_arn
        self.principal_arn = principal_arn

        # arn:aws:iam::12345:role/Example_Role_Name
        role_parts = role_arn.split(':')
        self.account = role_parts[4]
        self.role_name = role_parts[5].split('/')[-1]

    def get_credentials(self, duration_seconds=60*60):
        client = boto3.client('sts')
        result = client.assume_role_with_saml(
                RoleArn=self.role_arn,
                PrincipalArn=self.principal_arn,
                SAMLAssertion=self.saml_assertion,
                DurationSeconds=duration_seconds)

        key_id = result['Credentials']['AccessKeyId']
        secret = result['Credentials']['SecretAccessKey']
        session_token = result['Credentials']['SessionToken']
        expiry = result['Credentials']['Expiration']

        credentials = AwsCredentials(
                key_id, secret, session_token, expiry)
        return credentials


class AwsCredentials:
    def __init__(self, key_id, secret, session_token, expiry):
        self.key_id = key_id
        self.secret = secret
        self.session_token = session_token
        self.expiry = expiry

    def get_client(self, service, region_name='us-east-1'):
        client = boto3.client(
                service,
                region_name=region_name,
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.secret,
                aws_session_token=self.session_token)
        return client


async def _get_roles(page):
    roles = []
    content = await page.content()

    soup = bs4.BeautifulSoup(content, 'html.parser')
    assertion = soup.find('input', {'name': 'SAMLResponse'}).get('value')
    assertion_xml = xml.etree.ElementTree.fromstring(base64.b64decode(assertion))
    for saml2attribute in assertion_xml.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role':
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                role = saml2attributevalue.text
                role_parts = role.split(',')
                if 'saml-provider' in role_parts[0]:
                    principal_arn = role_parts[0]
                    role_arn = role_parts[1]
                else:
                    role_arn = role_parts[0]
                    principal_arn = role_parts[1]
                roles.append(AwsRole(assertion, role_arn, principal_arn))
    return roles


async def _load_entry(entry_url, headless, stay_signed_in):
    launch_options = { 'headless': headless }
    if stay_signed_in:
        user_data_dir = os.path.expanduser('~/.aws-azuread-login/chromium-user-data')
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        launch_options['userDataDir'] = user_data_dir

    browser = await pyppeteer.launch(options=launch_options)
    page = await browser.newPage()
    await page.goto(entry_url, options={'waitUntil': ['load','domcontentloaded','networkidle0','networkidle2']})
    return browser, page


def _get_default_username():
    filepath = os.path.expanduser('~/.aws-azuread-login/default-username')
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath) as f:
            return f.read()


def _set_default_username(username):
    dirpath = os.path.expanduser('~/.aws-azuread-login')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    filepath = os.path.expanduser('~/.aws-azuread-login/default-username')
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(filepath, 'w') as f:
        f.write(username)


def _get_keyring_password_for_username(username):
    return keyring.get_password('aws-azuread-login', username)


def _set_keyring_password_for_username(username, password):
    keyring.set_password('aws-azuread-login', username, password)


async def _input_username(page, username):
    input_selector = 'input[type="email"][name="loginfmt"]'
    submit_selector = 'input[type="submit"][value="Next"]'
    error_selector = '#usernameError'

    # Username
    if username is None:
        default_username = _get_default_username()
        if default_username:
            username = input(f'Username ({default_username}): ')
            if username in [None, '']:
                username = default_username
        else:
            while username in [None, '']:
                username = input('Username: ')

    while True:
        while username in [None, '']:
            username = input('Username: ')

        await page.type(input_selector, username)
        await page.click(submit_selector)
        
        while True:
            if not await _check_for_visible_element(page, input_selector):
                _set_default_username(username)
                return
            elif await _check_for_visible_element(page, error_selector):
                username = None
                await page.evaluate(f'() => document.querySelector(\'{input_selector}\').value = \'\'')
                print('Unknown username, try again')
                break
            # wait for one of the above to appear
            await asyncio.sleep(0.25)


async def _input_password(page, username, password):
    input_selector = 'input[type="password"][name="passwd"]'
    submit_selector = 'input[type="submit"][value="Sign in"]'
    error_selector = '#passwordError'
    
    # Password
    if password is None:
        keyring_password = _get_keyring_password_for_username(username)
        if keyring_password and keyring_password != '':
            password = getpass.getpass('Password (*****): ')
            if password in [None, '']:
                password = keyring_password
        else:
            while password in [None, '']:
                password = getpass.getpass('Password: ')

    while True:
        while password in [None, '']:
            password = getpass.getpass('Password: ')

        await page.type(input_selector, password)
        await page.click(submit_selector)
        await asyncio.sleep(1)

        while True:
            if not await _check_for_visible_element(page, input_selector):
                _set_keyring_password_for_username(username, password)
                return
            elif await _check_for_visible_element(page, error_selector):
                password = None
                await page.evaluate(f'() => document.querySelector(\'{input_selector}\').value = \'\'')
                print('Incorrect password, try again')
                break
            # wait for one of the above to appear
            await asyncio.sleep(0.25)


async def _input_code(page, code):
    input_selector = 'input[type="tel"][name="otc"]'
    checkbox_selector = 'input[type="checkbox"][name="rememberMFA"]'
    submit_selector = 'input[type="submit"][value="Verify"]'
    error_selector = '#idSpan_SAOTCC_Error_OTC'
    
    while True:
        while code is None:
            code = input('One-time code: ')

        await page.type(input_selector, code)
        await page.click(checkbox_selector)
        await page.click(submit_selector)

        while True:
            if not await _check_for_visible_element(page, input_selector):
                return
            elif await _check_for_visible_element(page, error_selector):
                code = None
                await page.evaluate(f'() => document.querySelector(\'{input_selector}\').value = \'\'')
                await page.click(checkbox_selector)
                print('Incorrect code, try again')
                break
            # wait for one of the above to appear
            await asyncio.sleep(0.25)


async def _input_stay_signed_in(page, stay_signed_in):
    if stay_signed_in:
        await page.click('input[type="checkbox"][name="DontShowAgain"]')
        await page.click('input[type="submit"][value="Yes"]')
    else:
        await page.click('input[type="button"][value="No"]')


async def _check_for_visible_element(page, selector):
    try:
        element = await page.J(selector)
        return element and await element.isIntersectingViewport()
    except pyppeteer.errors.NetworkError:
        return False

async def authenticate(entry_url, *, username=None, password=None, code=None, headless=True, stay_signed_in=True):
    print('Loading entry url...')
    browser, page = await _load_entry(entry_url, headless, stay_signed_in)
    # we can't really be sure whether we'll get prompted for OTC, 
    # stay logged in, etc or if the process will go straight thru to role selection
    # so we'll just take it as it comes
    while True:
        if await _check_for_visible_element(page, 'input[type="email"][name="loginfmt"]'):
            await _input_username(page, username)
        elif await _check_for_visible_element(page, 'input[type="password"][name="passwd"]'):
            await _input_password(page, username, password)
        elif await _check_for_visible_element(page, 'input[type="tel"][name="otc"]'):
            await _input_code(page, code)
        elif await _check_for_visible_element(page, 'input[type="checkbox"][name="DontShowAgain"]'):
            await _input_stay_signed_in(page, stay_signed_in)
        elif await page.J('#signin_button'):
            roles = await _get_roles(page)
            await browser.close()
            return roles
        else:
            # wait for a known option to appear
            await asyncio.sleep(0.25)


if __name__ == '__main__':
    entry_url = sys.argv[1]
    username = None
    if len(sys.argv) > 2:
        username = sys.argv[2]
    password = None
    if len(sys.argv) > 3:
        password = sys.argv[3]
    code = None
    if len(sys.argv) > 4:
        code = sys.argv[4]

    roles = asyncio.get_event_loop().run_until_complete(
            authenticate(
                entry_url, username=username, password=password, code=code, headless=True, stay_signed_in=False))
    print(roles)
    input('!')

