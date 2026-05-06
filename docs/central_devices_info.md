# module: central_devices_info

description: This module allows you to retrieve Device(s) in HPE Aruba Networking Central. Provides various subsets to fetch different types of device information.

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
    Retrieve a subset of devices and their information
  type: str
  required: false
  choices:
    - all_devices
    - device_by_serial
    - device_by_id
    - device_by_filter
  default: all_devices
device_serial:
  description: >
    Device serial number to retrieve when using device_by_serial subset
  type: str
  required: false
device_id:
  description: >
    Device scopeId to retrieve when using device_by_id subset
  type: int
  required: false
device_filters:
  description: >
    Filters for retrieving specific devices when using the device_by_filter subset.
    Only the endpoints for which a filter is provided will be called.
    If only monitoring_filter is provided, only the monitoring endpoint is called.
    If only inventory_filter is provided, only the inventory endpoint is called.
    If both filters are provided, both endpoints are called and their results are merged,
    with monitoring data added to matching inventory records and any monitoring-only
    devices appended to the final list.
  type: dict
  required: false
  suboptions:
    inventory_filter:
      description: >
        Filter expression for the /network-monitoring/v1/device-inventory endpoint.
        When provided, only this endpoint is queried with the given filter.
        Example: "deviceType eq SWITCH and siteId eq 12345"
      type: str
    monitoring_filter:
      description: >
        Filter expression for the /network-monitoring/v1/devices endpoint.
        When provided, only this endpoint is queried with the given filter.
        Example: "deviceType eq SWITCH and siteId eq 12345"
      type: str
```

##### EXAMPLES

```YAML
- name: Get all devices in Central
  arubanetworks.hpeanw_central.central_devices_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: devices_result

- name: Get all devices using access token
  arubanetworks.hpeanw_central.central_devices_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: all_devices
  register: devices_result

- name: Get device by serial
  arubanetworks.hpeanw_central.central_devices_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: device_by_serial
    device_serial: "ABC123XYZ"
  register: devices_result

- name: Get device by ID
  arubanetworks.hpeanw_central.central_devices_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: device_by_id
    device_id: 1122334455
  register: devices_result

- name: Get device by Filter
  arubanetworks.hpeanw_central.central_devices_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: device_by_filter
    device_filters:
      inventory_filter: "isProvisioned eq Yes and siteName eq Ansible-Campus"
      monitoring_filter: "siteName eq Ansible-Campus"
  register: devices_result
```

##### RETURNED
```YAML
devices:
  description: List of dictionaries containing details of devices in Central
  returned: always
  type: dict
  contains:
    devices:
      description: Device information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of devices returned in the response
      type: int
      returned: on success
    msg:
      description: Detailed message or error information
      type: str
      returned: always
```