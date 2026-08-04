# module: unified_token

description: This module allows you to generate an OAuth Token using unified credentials. Unified credentials are useful when your workflow needs HPE GreenLake Platform only, or both HPE GreenLake Platform and HPE Aruba Networking Central.

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
workspace_id:
  description: >
    The GreenLake workspace ID associated with your GLP workspace
  type: str
  required: true
```

##### EXAMPLES

```YAML
- name: Create OAuth Token with unified credentials for GLP only
  arubanetworks.hpeanw_central.unified_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: workspace-abc-123
  register: token_result
  no_log: true

- set_fact:
    unified_access_token: "{{ token_result['access_token'] }}"
```

##### RETURNED
```YAML
access_token:
  description: OAuth Token generated using unified credentials
  type: str
  returned: success
```