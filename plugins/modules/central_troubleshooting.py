#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_troubleshooting
short_description: Execute troubleshooting commands on devices in HPE Aruba Networking Central
description:
  - This module allows you to execute troubleshooting commands on one or more devices
    in HPE Aruba Networking Central using the pycentral library.
  - Supports a wide range of actions including ping, traceroute, reboot, show commands,
    disconnect operations, port tests, and more.
  - Troubleshooting tasks are executed asynchronously on the Central platform,
    and the module polls for results until completion.
  - Results are returned per device serial number, if one or more devices fail
    the module will return a failed status with details.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "2.0.0"
options:
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
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
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
"""

from ansible.module_utils.basic import AnsibleModule
from pycentral.scopes import Scopes
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleCentralConnection,
    central_base_argument_spec,
)

import traceback


# Required options per action - empty list means no options required
REQUIRED_OPTIONS = {
    "ping_test": ["destination"],
    "traceroute_test": ["destination"],
    "reboot": [],
    "locate_test": [],
    "disconnect_all_clients": [],
    "disconnect_all_users": [],
    "disconnect_client_mac_addr": ["mac_address"],
    "disconnect_user_mac_addr": ["mac_address"],
    "disconnect_all_users_ssid": ["network"],
    "http_test": ["destination"],
    "https_test": ["destination"],
    "port_bounce_test": ["ports"],
    "poe_bounce_test": ["ports"],
    "arp_test": [],
    "nslookup_test": ["host"],
    "speedtest_test": ["iperf_server_address"],
    "tcp_test": ["host", "port"],
    "aaa_test": ["radius_server_ip", "username", "password"],
    "cable_test": ["ports"],
    "iperf_test": ["server_address"],
    "list_show_commands": [],
    "run_show_commands": ["commands"],
}

# Actions that perform an operational change on the device
CHANGED_ACTIONS = {
    "reboot",
    "locate_test",
    "disconnect_all_clients",
    "disconnect_all_users",
    "disconnect_client_mac_addr",
    "disconnect_user_mac_addr",
    "disconnect_all_users_ssid",
    "port_bounce_test",
    "poe_bounce_test",
}


def validate_options(module, action, options):
    """Validate that all required options for the given action are present."""
    required = REQUIRED_OPTIONS.get(action, [])
    missing = [
        opt for opt in required if opt not in options or options[opt] is None
    ]
    if missing:
        module.fail_json(
            msg=f"The following options are required for action '{action}': {missing}"
        )


def main():
    module_args = dict(
        **central_base_argument_spec(),
        devices=dict(type="list", elements="str", required=True),
        action=dict(
            type="str",
            required=True,
            choices=list(REQUIRED_OPTIONS.keys()),
        ),
        options=dict(type="dict", required=False, default={}),
    )

    # Initialize the Ansible module with argument spec
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Extract module parameters
    devices = module.params["devices"]
    action = module.params["action"]
    options = module.params["options"] or {}

    # Validate required options for the chosen action
    validate_options(module, action, options)

    # Establish connection to HPE Aruba Networking Central
    try:
        central_obj = ModuleCentralConnection(module)
        central_conn = central_obj.get_central_conn()

        # Verify connection was established successfully
        if central_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE Aruba Networking Central"
            )
    except Exception as e:
        # Handle connection plugin loading errors
        module.fail_json(
            msg=f"Failed to load 'arubanetworks.hpeanw_central.central' connection plugin: {e}"
        )

    try:
        action_results = {}

        # Initialize Scopes object to interact with Central's devices
        scopes = Scopes(central_conn)

        fail = {}
        success = {}

        for serial in devices:
            try:
                device = scopes.find_device(device_serials=serial)
                action_method = getattr(device, action)
                result = action_method(**options)
                result["results"] = (
                    result["output"]["results"]
                    if "output" in result and "results" in result["output"]
                    else None
                )
                result.pop(
                    "output", None
                )  # Remove layered output to avoid redundancy
                action_results[serial] = result
                success[serial] = action_results[serial].copy()
            except Exception as e:
                action_results[serial] = {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                fail[serial] = action_results[serial].copy()

        changed = action in CHANGED_ACTIONS

        if fail:
            module.fail_json(
                msg=f"Action '{action}' failed on {len(fail)}/{len(devices)} devices",
                fail=fail,
                success=success,
            )

        module.exit_json(
            msg="success",
            changed=changed,
            success=success,
        )

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
