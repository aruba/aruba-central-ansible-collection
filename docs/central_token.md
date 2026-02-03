# module: central_token

description: This module allows you to generate an OAuth Token for HPE Aruba Networking Central.

##### ARGUMENTS

```YAML
base_url:
  description: >
    The base URL for the Central account including leading https:// ex) https://de3.api.central.arubanetworks.com
  type: str
  required: true
client_id:
  description: >
    The client ID for the Central account, used to create OAuth token
  type: str
  required: true
client_secret:
  description: >
    The client secret for the Central account, used to create OAuth token
  type: str
  required: true
```

##### EXAMPLES

```YAML
- name: Create OAuth Token from Central
  arubanetworks.hpeanw_central.central_token:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: token_result

- set_fact:
    central_access_token: "{{ token_result['access_token'] }}"
```

##### RETURNED
```YAML
access_token:
  description: OAuth Token generated from Central
  type: str
  returned: success
```