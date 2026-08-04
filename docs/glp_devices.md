# module: glp_devices

description: This module allows for application & subscription assignment of devices in HPE GreenLake Platform.

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
devices:
  description: >
    List of device serial numbers to assign/unassign to the application and/or subscription
  type: list
  elements: str
  required: true
application:
  description: >
    Retrieve a subset of devices and their information
  type: dict
  required: false
  suboptions:
    id:
      description: >
        ID of application to assign devices to
      type: str
    name:
      description: >
        Name of application to assign devices to
      type: str
    region:
      description: >
        Region of application to assign devices to
      type: str
subscription_key:
  description: >
    Key of subscription to assign devices to
  type: str
  required: false
state:
  description: >
    Desired state of the devices
  type: str
  required: false
  choices: ['assigned', 'unassigned']
  default: 'assigned'
```

##### EXAMPLES

```YAML
- name: Assign devices to application and subscription with client credentials
  arubanetworks.hpeanw_central.glp_devices:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    application:
      name: HPE Aruba Networking Central
      region: "US West"
    subscription_key: "sub-key-123"
    devices:
      - "SN123456789"
      - "SN987654321"
    state: "assigned"
  register: devices_result

- name: Assign devices to application and subscription
  glp_devices:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    application:
      name: "MyApp"
      region: "eu-central"
    subscription_key: "sub-key-456"
    state: "assigned"
  register: devices_result

- name: Unassign devices from application and subscription
  glp_devices:
    access_token: "AABBCC-111222-333444-555666777888"
    application:
      name: "MyApp"
    subscription_key: "sub-key-789"
    state: "unassigned"
  register: devices_result

- name: Assign devices using unified credentials
  arubanetworks.hpeanw_central.glp_devices:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    workspace_id: 1234567890
    application:
      name: HPE Aruba Networking Central
      region: "US West"
    subscription_key: "sub-key-123"
    devices:
      - "SN123456789"
    state: "assigned"
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