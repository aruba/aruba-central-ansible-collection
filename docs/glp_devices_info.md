# module: glp_devices_info

description: This module allows you to retrieve information about devices managed in HPE GreenLake Platform. Provides various subsets to fetch different types of device information.

##### ARGUMENTS

```YAML
client_id:
  description: >
    The client ID for the GLP account, used to create OAuth token, required if access_token is not provided
  type: str
  required: false
client_secret:
  description: >
    The client secret for the GLP account, used to create OAuth token, required if access_token is not provided
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
    - device_by_filter
    - device_by_id
    - device_by_serial
  default: all_devices
device_filter:
  description: >
    Filter expression for retrieving specific devices when using device_by_filter subset
  type: str
  required: false
select:
  description: >
    A comma separated list of properties to display in the response
  type: str
  required: false
device_id:
  description: >
    Device ID to retrieve when using device_by_id subset
  type: str
  required: false
serial_number:
  description: >
    Device serial number to lookup when using device_by_serial subset
  type: str
  required: false
```

##### EXAMPLES

```YAML
- name: Get all devices in GLP
  arubanetworks.hpeanw_central.glp_devices_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: devices_result

- name: Get devices with specific fields
  arubanetworks.hpeanw_central.glp_devices_info:
    access_token: AABBCC-111222-333444-555666777888
    subset: all_devices
    select: "id,serialNumber,model,macAddress"
  register: devices_result

- name: Get device by filter
  arubanetworks.hpeanw_central.glp_devices_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: device_by_filter
    device_filter: "serialNumber eq 'ABC123456'"
  register: devices_result

- name: Get device by serial number
  arubanetworks.hpeanw_central.glp_devices_info:
    access_token: AABBCC-111222-333444-555666777888
    subset: device_by_serial
    serial_number: "ABC123456"
  register: devices_result
```

##### RETURNED
```YAML
devices:
  description: List of dictionaries containing details of devices in GLP
  returned: always
  type: dict
  contains:
    devices:
      description: Device information based on requested subset
      type: list
      elements: dict
      returned: on success
    code:
      description: HTTP status code of the request
      type: int
      returned: always
    msg:
      description: Detailed message or error information
      type: str
      returned: always
```