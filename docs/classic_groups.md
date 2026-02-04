# module: classic_groups

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
group_name:
  description: >
    The name of the device group to which devices will be assigned or unassigned
  type: str
  required: true
group_attributes:
  description: >
    Dictionary containing required data to configure the specified device group, required when state is 'merged'
  type: dict
  required: false
device_type:
  description: >
    The type of devices to assign or unassign (e.g., ACCESS_POINT, SWITCH, GATEWAY)
  type: str
  required: true
  choices: ['ACCESS_POINT', 'SWITCH', 'GATEWAY']
devices:
  description: >
    List of device serial numbers to assign or unassign to the device group,
    state must be set to 'assigned' or 'unassigned'. All devices must be of the same type.
  type: list
  elements: str
  required: true
state:
  description: >
    Desired state of the group whether it should be merged, deleted, or devices assigned/unassigned.
    - 'merged': Create the device group or update an existing group of the same name.
    - 'deleted': Delete the device group, devices will be assigned to the default group.
    - 'assigned': Assign the specified devices to the device group.
    - 'unassigned': Unassign the specified devices from the device group, devices will be assigned to the default group.
  type: str
  required: false
  choices: ['merged', 'deleted', 'assigned', 'unassigned']
  default: 'assigned'
```

##### EXAMPLES

```YAML
- name: Create a device group
  arubanetworks.hpeanw_central.classic_groups:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    group_name: "Chicago-Campus"
    group_attributes:
      template_info:
        Wired: false
      group_properties:
        AllowedDevTypes:
          - AccessPoints
          - Gateways
          - Switches
        Architecture: AOS10
        ApNetworkRole: Standard
        GwNetworkRole: BranchGateway
        AllowedSwitchTypes:
          - AOS_CX
        NewCentral: true
    device_type: "ACCESS_POINT"
    devices: []
    state: merged

- name: Create a device group for Switches
  arubanetworks.hpeanw_central.classic_groups:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    group_name: "Fabric2-Switches"
    group_attributes:
      template_info:
        Wired: false
      group_properties:
        AllowedDevTypes:
          - Switches
        AllowedSwitchTypes:
          - AOS_CX
        NewCentral: true
    device_type: "SWITCH"
    devices: []
    state: merged

- name: Assign devices to a group
  arubanetworks.hpeanw_central.classic_groups:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    group_name: "MyDeviceGroup"
    device_type: "SWITCH"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: assigned

- name: Unassign devices from a group
  arubanetworks.hpeanw_central.classic_groups:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    group_name: "MyDeviceGroup"
    device_type: "GATEWAY"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: unassigned

- name: Delete a device group
  arubanetworks.hpeanw_central.classic_groups:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    group_name: "MyDeviceGroup"
    device_type: "ACCESS_POINT"
    state: deleted
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