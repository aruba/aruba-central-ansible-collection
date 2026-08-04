# module: glp_api

description: This module allows you to execute API calls to HPE GreenLake Platform. It uses the glp connection plugin to handle authentication and API calls.

##### ARGUMENTS

```YAML
client_id:
  description: >
    The client ID for the GLP account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, workspace_id must be provided.
  type: str
  required: false
client_secret:
  description: >
    The client secret for the GLP account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, workspace_id must be provided.
  type: str
  required: false
access_token:
  description: >
    A generated OAuth token for authenticating API requests
  type: str
  required: false
workspace_id:
  description: >
    GreenLake Platform workspace ID used for unified or MSP authentication
  type: str
  required: false
tenant_name:
  description: >
    Tenant name used to obtain a tenant-scoped connection when workspace_id is provided
  type: str
  required: false
tenant_id:
  description: >
    Tenant ID gathered from GLP used to obtain a tenant-scoped connection when workspace_id is provided
  type: str
  required: false
method:
  description:
    - HTTP method to use for the API call
  type: str
  choices: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
  default: 'GET'
  required: false
path:
  description:
    - API endpoint path without BASE URL (e.g., /subscriptions/v1/subscriptions)
  type: str
  required: true
data:
  description:
    - Data to be sent in the request body for POST, PUT, or PATCH requests
  type: dict
  required: false
  default: {}
params:
  description:
    - URL query parameters
  type: dict
  required: false
  default: {}
```

##### EXAMPLES

```YAML
- name: Get list of all subscriptions
  arubanetworks.hpeanw_central.glp_api:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    method: GET
    path: " /subscriptions/v1/subscriptions"
  register: subscriptions_result

- name: Get list of all subscriptions using unified credentials
  arubanetworks.hpeanw_central.glp_api:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: 1234567890
    method: GET
    path: " /subscriptions/v1/subscriptions"
  register: subscriptions_result
```

##### RETURNED
```YAML
result:
  description: Result of the API call
  returned: always
  type: dict
  contains:
    code:
      description: HTTP response status code
      type: int
      returned: always
      sample: 200
    msg:
      description: Response body (can be dict or str depending on API response)
      type: raw
      returned: always
    headers:
      description: Response headers
      type: dict
      returned: always
```