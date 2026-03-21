# module: glp_inventory

description: This module allows for adding devices to the inventory in HPE GreenLake Platform.

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
devices:
  description: >
    List of device serial numbers and MAC addresses to add to GLP inventory, keys should be "serial_number" and "mac_address"
  type: list
  elements: dict
  required: true
  suboptions:
    serial_number:
      description: >
        Serial number of the device to add to GLP inventory
      type: str
    mac_address:
      description: >
        MAC address of the device to add to GLP inventory, will be sanitized to be in format XX:XX:XX:XX:XX:XX lowercase
      type: str
state:
  description: >
    Desired state of the devices
  type: str
  required: false
  choices: ['merged']
  default: 'merged'
```

##### EXAMPLES

```YAML
- name: Add Network Devices to GLP Device Inventory
  arubanetworks.hpeanw_central.glp_inventory:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    devices:
      - serial_number: "SN123456789"
        mac_address: "00:11:22:33:44:55"
      - serial_number: "SN987654321"
        mac_address: "66:77:88:99:AA:BB"
    state: "merged"
  register: devices_result

- name: Add Network Devices to GLP Device Inventory
  arubanetworks.hpeanw_central.glp_inventory:
    access_token: "AABBCC-111222-333444-555666777888"
    devices:
      - serial_number: "SN123456789"
        mac_address: "00:11:22:33:44:55"
      - serial_number: "SN987654321"
        mac_address: "66:77:88:99:AA:BB"
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