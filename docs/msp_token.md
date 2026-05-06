# module: msp_token

description: This module allows you to generate an OAuth Token for HPE Aruba Networking Central MSP. Supports generating both workspace-level and tenant-level tokens. When tenant_id or tenant_name is provided, a tenant-scoped token is returned.

##### ARGUMENTS

```YAML
client_id:
  description: >
    The client ID for the MSP workspace ID, used to create OAuth token
  type: str
  required: true
client_secret:
  description: >
    The client secret for the MSP workspace ID, used to create OAuth token
  type: str
  required: true
  no_log: true
workspace_id:
  description: >
    The GreenLake workspace ID associated with the MSP workspace
  type: str
  required: true
tenant_id:
  description: >
    The tenant ID to generate a tenant-scoped token for, can be with or without dashes
    If provided, the module returns a token scoped to this tenant
  type: str
  required: false
tenant_name:
  description: >
    The tenant name to generate a tenant-scoped token for
    If provided, the module returns a token scoped to this tenant
  type: str
  required: false
```

##### EXAMPLES

```YAML
- name: Create MSP workspace-level OAuth Token
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: workspace-abc-123
  register: token_result
  no_log: true

- set_fact:
    msp_access_token: "{{ token_result['msp_access_token'] }}"

- name: Create tenant-scoped OAuth Token by tenant ID
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: workspace-abc-123
    tenant_id: tenant-abc-123
  register: tenant_token_result
  no_log: true

- name: Create tenant-scoped OAuth Token by tenant name
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: workspace-abc-123
    tenant_name: MyTenant
  register: tenant_token_result
  no_log: true

- set_fact:
    tenant_access_token: "{{ tenant_token_result['tenant_access_token'] }}"

- set_fact:
    msp_access_token: "{{ tenant_token_result['msp_access_token'] }}"
```

##### RETURNED
```YAML
msp_access_token:
  description: OAuth Token generated for the MSP workspace or tenant
  type: str
  returned: success
tenant_access_token:
  description: OAuth Token generated for the MSP workspace or tenant
  type: str
  returned: success
```