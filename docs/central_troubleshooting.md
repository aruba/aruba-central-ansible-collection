# module: central_troubleshooting

description: This module allows you to execute troubleshooting commands on one or more devices in HPE Aruba Networking Central using the pycentral library. Supports a wide range of actions including ping, traceroute, reboot, show commands, disconnect operations, port tests, and more. Troubleshooting tasks are executed asynchronously on the Central platform, and the module polls for results until completion. Results are returned per device serial number, if one or more devices fail the module will return a failed status with details.

##### ARGUMENTS

```YAML
base_url:
  description: >
    The base URL for the Central account including leading https://
    ex) https://de3.api.central.arubanetworks.com
  type: str
  required: true
client_id:
  description: >
    The client ID for the Central account, used to create OAuth token,
    required if access_token is not provided
  type: str
  required: false
client_secret:
  description: >
    The client secret for the Central account, used to create OAuth token,
    required if access_token is not provided
  type: str
  required: false
access_token:
  description: >
    A generated OAuth token for authenticating API requests
  type: str
  required: false
devices:
  description: >
    List of device serial numbers to run the troubleshooting action on. For 
    efficiency it's recommended to provide a list of serial numbers rather 
    than a single serial number and repeat the task multiple times.
  type: list
  elements: str
  required: true
action:
  description: >
    The troubleshooting action to perform on the specified devices.
    See the options parameter for action-specific required fields.
  type: str
  required: true
  choices:
    - ping_test
    - traceroute_test
    - reboot
    - locate_test
    - disconnect_all_clients
    - disconnect_all_users
    - disconnect_client_mac_addr
    - disconnect_user_mac_addr
    - disconnect_all_users_ssid
    - http_test
    - https_test
    - port_bounce_test
    - poe_bounce_test
    - arp_test
    - nslookup_test
    - speedtest_test
    - tcp_test
    - aaa_test
    - cable_test
    - iperf_test
    - list_show_commands
    - run_show_commands
options:
  description: >
    Action-specific parameters. Required fields vary by action.
    See the following table for which fields are required per action.

    - ping_test - destination (str)
    - traceroute_test - destination (str)
    - reboot - no options required
    - locate_test - no options required
    - disconnect_all_clients - no options required
    - disconnect_all_users - no options required
    - disconnect_client_mac_addr - mac_address (str)
    - disconnect_user_mac_addr - mac_address (str)
    - disconnect_all_users_ssid - network (str)
    - http_test - destination (str)
    - https_test - destination (str)
    - port_bounce_test - ports (list)
    - poe_bounce_test - ports (list)
    - arp_test - no options required
    - nslookup_test - host (str)
    - speedtest_test - iperf_server_address (str)
    - tcp_test - host (str), port (int)
    - aaa_test - radius_server_ip (str), username (str), password (str)
    - cable_test - ports (list)
    - iperf_test - server_address (str)
    - list_show_commands - no options required
    - run_show_commands - commands (list or str)

    Note - The password field in aaa_test options is sensitive and should be vaulted.
    Any additional kwargs supported by the underlying pycentral methods may also be passed here.
  type: dict
  required: false
  default: {}
```

##### EXAMPLES

```YAML
- name: Ping test on multiple devices
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - PNWJKLJKLW
      - SNA121B212
    action: ping_test
    options:
      destination: 8.8.8.8
  register: ping_result

- name: Run show commands on a list of APs
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices: "{{ aps_serials }}"
    action: run_show_commands
    options:
      commands:
        - show running-config
        - show version
  register: running_config_output

- name: PoE bounce specific ports on switches
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - PNWJKLJKLW
      - SNA121B212
    action: poe_bounce_test
    options:
      ports:
        - 1/1/1
        - 1/2/1
  register: poe_result

- name: Reboot devices
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    client_id: "{{ central_client_id }}"
    client_secret: "{{ central_client_secret }}"
    devices:
      - PNWJKLJKLW
    action: reboot
  register: reboot_result

- name: Disconnect a client by MAC address from a gateway
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - GG08KW8075
    action: disconnect_client_mac_addr
    options:
      mac_address: "aa:bb:cc:dd:ee:ff"
  register: disconnect_result

- name: AAA test on an AP
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - VNQ7KZE4JB
    action: aaa_test
    options:
      radius_server_ip: 192.168.1.10
      username: testuser
      password: "{{ vault_radius_password }}"
  register: aaa_result

- name: TCP test from an AP
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - VNQ722D4JB
    action: tcp_test
    options:
      host: 10.0.0.1
      port: 443
  register: tcp_result

- name: List supported show commands on a device
  arubanetworks.hpeanw_central.central_troubleshooting:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    devices:
      - SG08KW807501
    action: list_show_commands
  register: show_commands_list
```

##### RETURNED
```YAML
msg:
  description: Status message describing the outcome of the module execution
  returned: always
  type: str
  sample: "success"
changed:
  description: >
    True if the action performed an operational change on the device
    (e.g., reboot, disconnect, port bounce). False for read-only tests.
  returned: always
  type: bool
  sample: false
success:
  description: >
    List of result objects for devices on which the action succeeded.
    The structure of each result varies by action, but common fields are shown below.
  returned: when one or more devices succeed
  type: list
  elements: dict
  contains:
    status:
      description: Status of the troubleshooting task (e.g., COMPLETED, FAILED)
      type: str
      sample: "COMPLETED"
    startTime:
      description: ISO timestamp when the task started
      type: str
      sample: "2026-03-29T01:21:57.840207113Z"
    endTime:
      description: ISO timestamp when the task ended
      type: str
      sample: "2026-03-29T01:21:57.925886647Z"
    progressPercent:
      description: Completion percentage of the task
      type: int
      sample: 100
    failReason:
      description: Reason for failure if the task did not complete successfully, otherwise null
      type: str
      sample: null
    output:
      description: >
        Action-specific output. For run_show_commands, contains the commands run and their output.
        Structure varies by action.
      type: dict
      sample:
        commands:
          - "show running-config"
        results:
          - command: "show running-config"
            output: "version 10.6.0.0-10.6.0\n..."
    rawOutput:
      description: Raw string output returned by some actions (e.g., ping_test)
      type: str
      sample: "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n64 bytes from 8.8.8.8..."
fail:
  description: >
    List of error objects for devices on which the action failed.
    Present only when at least one device encounters an error.
  returned: when one or more devices fail
  type: list
  elements: dict
  contains:
    error:
      description: Error message string describing what went wrong
      type: str
      sample: "'NoneType' object has no attribute 'run_show_commands'"
    traceback:
      description: Full Python traceback of the exception for debugging
      type: str
      sample: "Traceback (most recent call last):\n  File ...\nAttributeError: ..."
```