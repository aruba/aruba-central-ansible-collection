# module: classic_sites

description: This module allows you to assign or unassign devices to a site in HPE Aruba Networking Central. It does not handle refresh token or OAuth token generation; you must provide a valid access token.

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
site_name:
  description: >
    The name of the site to which devices will be assigned or unassigned
  type: str
  required: true
device_type:
  description: >
    The type of devices to assign or unassign (e.g., ACCESS_POINT, SWITCH, GATEWAY)
  type: str
  required: true
  choices: ['ACCESS_POINT', 'SWITCH', 'GATEWAY']
devices:
  description:
    - List of device serial numbers to assign or unassign to the site, all devices must be of the same type
  type: list
  elements: str
  required: true
state:
  description: >
    Desired state of the devices with respect to the site
  type: str
  required: false
  choices: ['assigned', 'unassigned']
  default: 'assigned'
```

##### EXAMPLES

```YAML
- name: Assign devices to a site
  arubanetworks.hpeanw_central.classic_sites:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    site_name: "SiteA"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: assigned

- name: Unassign devices from a site
  arubanetworks.hpeanw_central.classic_sites:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    site_name: "SiteA"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: unassigned
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