# module: glp_token

description: This module allows you to generate an OAuth Token for HPE GreenLake.

##### ARGUMENTS

```YAML
client_id:
  description: >
    The client ID for the GLP account, used to create OAuth token
  type: str
  required: true
client_secret:
  description: >
    The client secret for the GLP account, used to create OAuth token
  type: str
  required: true
```

##### EXAMPLES

```YAML
- name: Create OAuth Token for GLP
  arubanetworks.hpeanw_central.glp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    register: token_result
    no_log: True

- set_fact:
    oauth_token: "{{ token_result['access_token'] }}"
```

##### RETURNED
```YAML
access_token:
  description: OAuth Token generated from GLP
  type: str
  returned: success
```