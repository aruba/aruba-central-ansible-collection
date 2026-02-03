# module: central_device_groups_info

description: This module allows you to retrieve Device Group(s) in HPE Aruba Networking Central. Provides various subsets to fetch different types of device group information.

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
subset:
  description: >
    Retrieve a subset of device groups and their information
  type: str
  required: false
  choices:
    - all_device_groups
    - device_group_by_name
    - device_group_by_id
  default: all_device_groups
device_group_name:
  description: >
    Device Group name to retrieve when using device_group_by_name subset
  type: str
  required: false
device_group_id:
  description: >
    Device Group ID to retrieve when using device_group_by_id subset
  type: int
  required: false
```

##### EXAMPLES

```YAML
- name: Get all device groups in Central
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: device_groups_result

- name: Get all device groups using access token
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: all_device_groups
  register: device_groups_result

- name: Get device group by name
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: device_group_by_name
    device_group_name: "Data Center Switches"
  register: device_groups_result

- name: Get device group by ID
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: device_group_by_id
    device_group_id: 1122334455
  register: device_groups_result
```

##### RETURNED
```YAML
device_groups:
  description: List of dictionaries containing details of device groups in Central
  returned: always
  type: dict
  contains:
    device_groups:
      description: Device group information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of device groups returned in the response
      type: int
      returned: on success
    msg:
      description: Detailed message or error information
      type: str
      returned: always
```