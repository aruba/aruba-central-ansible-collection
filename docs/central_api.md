# module: central_api

description: This module allows you to execute API calls to HPE Aruba Networking Central. It uses the central connection plugin to handle authentication and API calls.

##### ARGUMENTS

```YAML
base_url:
  description: >
    The base URL for the Central account including leading https:// ex) https://de3.api.central.arubanetworks.com
  type: str
  required: true
client_id:
  description: >
    The client ID for the Central account, used to create OAuth token, required if access_token is not provided
  type: str
  required: false
client_secret:
  description: >
    The client secret for the Central account, used to create OAuth token, required if access_token is not provided
  type: str
  required: false
access_token:
  description: >
    A generated OAuth token for authenticating API requests
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
    - API endpoint path without BASE URL (e.g., /network-monitoring/v1alpha1/devices)
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
- name: Get list of all devices
  arubanetworks.hpeanw_central.central_api:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    method: GET
    path: "/network-monitoring/v1alpha1/devices"
  register: devices_result

- name: Assign Library Profile to Scope with Token
  arubanetworks.hpeanw_central.central_api:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: "{{central_access_token}}"
    method: POST
    path: "/network-config/v1alpha1/scope-maps"
    data:
      scope-map:
        - scope-name: "1234567897"
          persona: ACCESS_SWITCH
          resource: "layer2-vlan/404"
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