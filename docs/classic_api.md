# module: classic_api

description: This module allows you to execute API calls to Classic HPE Aruba Networking Central. It uses the classic connection plugin to handle authentication and API calls. It does not handle refresh token or OAuth token generation; you must provide a valid access token.

##### ARGUMENTS

```YAML
base_url:
  description: >
    The base URL for the Central account including leading https:// ex) https://apigw-eucentral2.central.arubanetworks.com
  type: str
  required: true
access_token:
  description: >
    A generated OAuth token for authenticating API requests
  type: str
  required: true
method:
  description:
    - HTTP method to use for the API call
  type: str
  choices: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
  default: 'GET'
  required: false
path:
  description:
    - API endpoint path without BASE URL (e.g., /monitoring/v2/network)
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
- name: Get Sites from Classic Central
  arubanetworks.hpeanw_central.classic_api:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    method: GET
    path: "/central/v2/sites"
  register: sites_result
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