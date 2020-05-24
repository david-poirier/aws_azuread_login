# aws_azuread_login

Python 3.6+ library to enable ADFS auth against AWS

## Usage

```python
import asyncio

import aws_azuread_login

roles = asyncio.get_event_loop().run_until_complete(
    aws_adfs_login.authenticate(
        'https://account.activedirectory.windowsazure.com/applications/signin/Application/00000000-0000-0000-0000-000000000000?tenantId=00000000-0000-0000-0000-000000000000')
for role in roles:
    credentials = role.get_credentials()
    client = credentials.get_client('ec2')
```

