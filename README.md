# aws_azuread_login

Python 3.6+ library to enable ADFS auth against AWS

## Installation
```
pip install aws-azuread-login 
```

## Usage

```python
import aws_azuread_login
import botocore
import json


# get creds one by one
for role in roles:
    try:
        print(f'Getting credentials for role {role.role_name} in account {role.account}...')
        credentials = role.get_credentials()
        client = credentials.get_client('ec2')
        response = client.describe_instances()
        print(json.dumps(response['Reservations'], indent=2, default=str))
    except botocore.exceptions.ClientError as e:
        print(f'\t 👎 Error getting credentials, skipping: {type(e)}, {str(e)}')


# get them all at once ('sts.AssumeRole' role errors are handled by aws_azuread_login)
multiple_credentials = aws_azuread_login.get_multiple_credentials(roles)
for credentials in multiple_credentials:
    client = credentials.get_client('ec2')
    response = client.describe_instances()
    print(json.dumps(response['Reservations'], indent=2, default=str))


# get clients in different regions
for credentials in multiple_credentials:
    client = credentials.get_client('ec2')
    response = client.describe_regions()
    for region in response['Regions']:
        region_name = region['RegionName']
        print(f'Creating client for region {region_name}...')
        client = credentials.get_client('ec2', region_name=region_name)
        response = client.describe_instances()
        print(json.dumps(response['Reservations'], indent=2, default=str))


# control the session duration, e.g. 12 hours (default is 1 hour)
credentials = roles[0].get_credentials(duration_seconds=60*60*12)
multiple_credentials = aws_azuread_login.get_mutiple_credentials(roles, duration_seconds=60*60*12)

```

