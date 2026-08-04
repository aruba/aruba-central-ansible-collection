# module: central_profiles

description: This module allows you to create and manage configuration profiles in HPE Aruba Networking Central.

##### ARGUMENTS

```YAML
base_url:
  description: >
    The base URL for the Central account including leading https:// ex) https://de3.api.central.arubanetworks.com
  type: str
  required: true
client_id:
  description: >
    The client ID for the Central account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, then this will be the client_id of GreenLake Platform (GLP) and workspace_id must be provided.
  type: str
  required: false
client_secret:
  description: >
    The client secret for the Central account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, then this will be the client_secret of GreenLake Platform (GLP) and workspace_id must be provided.
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
config_dict:
  description: >
    Dictionary containing required data to configure the specified profile path
  type: dict
  required: true
path:
  description: >
    The endpoint or path of the configuration profile to manage, this should be in reference
    to /network-config/v1alpha1/{path} , name will be appended if not already included & provided
  type: str
  required: true
name:
  description: >
    Name or identifier of the configuration profile, profiles require an identifier key/value pair
    typically "name" or "id" or another key is used depending on the profile type.
    For best idempotency results, provide this value.
    This value will be used as the identifier for retrieving, creating, updating, or deleting the specified profile.
  type: str
  required: false
resource:
  description: >
    Resource identifier for the profile, used for assigning LOCAL profiles
    required if local is provided, typically matches the endpoint in path i.e. layer2-vlan
  type: str
  required: false
local:
  description: >
    Dictionary containing scope-id (integer) and device-function (string) values to create a LOCAL profile
    If provided, the profile will be created as a LOCAL profile associated with the specified scope and device-function
    Requires `resource` to be set, will be set automatically when using `category`
  type: dict
  required: false
  suboptions:
    scope-id:
      description:
        - The scope ID to associate with the LOCAL profile
      type: int
      required: true
    device-function:
      description:
        - The device-function to associate with the LOCAL profile
      type: str
      required: true
state:
  description: >
    The state of the configuration after module completion:

    merged - Ansible merges the Central configuration with the provided configuration
    replaced - Ansible replaces the Central configuration with the provided configuration
    deleted - Ansible deletes the Central configuration
  type: str
  choices:
    - merged
    - replaced
    - deleted
  default: merged
```

##### EXAMPLES

```YAML
- name: Create a new VLAN profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: 100
    path: "layer2-vlan"
    config_dict:
      vlan: 100
      name: "Corp-VLAN"
      description: "Corporate VLAN for main office"
    state: merged
  register: profile_result

- name: Create a local profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    path: "system-info"
    state: merged
    local:
      scope-id: 46344420928
      device-function: "ACCESS_SWITCH"
    config_dict:
      hostname: RSVL-L1-Access-ANSIBLE

- name: Create a new ROLE profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: "Student"
    path: "roles"
    config_dict:
      name: "Student"
      description: "Role for student users"

- name: Create a WLAN profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: "Student-WLAN"
    path: "wlan-ssids"
    config_dict:
      opmode: "WPA2_PERSONAL"
      personal-security:
        passphrase-format: "STRING"
        wpa-passphrase: "Aruba321"
      essid:
        name: "student_wpa2"
      ssid: "student_wpa2"
      enable: true
      forward-mode: "FORWARD_MODE_L2"
      default-role: "student"
      vlan-id-range:
        - "42"
      vlan-selector: "VLAN_RANGES"

- name: Create a local profile with a specific path
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: profile-SDK1729KK
    path: local-management
    config_dict:
      name: profile-SDK1729KK
      webservers:
        enabled-vrfs:
          - default
          - mgmt
      ssh-server-global-configs:
        enabled-vrfs:
          - default
          - mgmt
      banner-message:
        message-delimiter: "~"
        text: |
          !
          WARNING - Unauthorized access to this device is strictly prohibited - WARNING
          This network is restricted to authorized users for legitimate business purposes only.
          Unauthorized access is a criminal offense and a violation of federal and state law.
          !

- name: Replace an existing profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: 100
    path: "layer2-vlan"
    config_dict:
      vlan: 100
      name: "New-Corp-VLAN"
      description: "Updated Corporate VLAN"
    state: replaced

- name: Delete a profile
  arubanetworks.hpeanw_central.central_profiles:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    name: "100"
    path: "layer2-vlan"
    state: deleted

- name: Create a VLAN profile using unified credentials
  arubanetworks.hpeanw_central.central_profiles:
    base_url: "{{ central_base_url }}"
    client_id: "{{ glp_client_id }}"
    client_secret: "{{ glp_client_secret }}"
    workspace_id: "{{ glp_workspace_id }}"
    name: 100
    path: "layer2-vlan"
    config_dict:
      vlan: 100
      name: "Corp-VLAN"
      description: "Corporate VLAN for main office"
    state: merged
```

##### RETURNED
```YAML
changed:
  description: True if the profile was created/modified/deleted, False otherwise
  type: bool
  returned: always
  sample: false
msg:
  description: Message indicating success or failure, if operation fails msg
    will contain error details
  type: str
  returned: always
result:
  description: Dictionary containing detailed response & operation details,
      in the case of an update it will include `diff` with the old_value and
      new_value for changed attributes
  returned: always
  type: dict
  contains:
    code:
      description: Response status code from API call
      type: int
    headers:
      description: Dictionary containing the API headers returned
      type: dict
    msg:
      description: Dictionary containing the API response
      type: dict
    diff:
      description: Dictionary containing the found differences between the
        existing configuration and the Ansible provided configuration
      returned: when state is merged and an update occurs
      type: dict
      contains:
        old_value:
          description: List containing the existing configuration(s) in Central
          type: list
        new_value:
          description: List containing the desired configuration(s) from Ansible
          type: list
```