#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_inventory
short_description: Allows devices to be added to the inventory in HPE GreenLake Platform.
description:
  - This module allows for adding devices to the inventory in HPE GreenLake Platform.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "1.0.0"
options:
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
"""

EXAMPLES = r"""
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

- name: Add Network Devices using unified credentials
  arubanetworks.hpeanw_central.glp_inventory:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    workspace_id: 1234567890
    devices:
      - serial_number: "SN123456789"
        mac_address: "00:11:22:33:44:55"
  register: devices_result
"""

RETURN = r"""
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
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    glp_base_argument_spec,
    get_glp_connection,
)
import traceback
from pycentral.glp import Devices


def main():
    module_args = dict(
        **glp_base_argument_spec(),
        workspace_id=dict(type="str", required=False),
        tenant_id=dict(type="str", required=False),
        tenant_name=dict(type="str", required=False),
        devices=dict(type="list", elements="dict", required=True),
        state=dict(
            type="str",
            required=False,
            choices=["merged"],
            default="merged",
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    state = module.params["state"]
    devices = module.params["devices"]

    devices_sanitized = [
        {
            "macAddress": device["mac_address"]
            .lower()
            .replace("-", ":")
            .replace(".", ":"),
            "serialNumber": device["serial_number"],
        }
        for device in devices
    ]

    add_devices = []

    # Establish a connection to GreenLake Platform using provided credentials or access token
    glp_conn = get_glp_connection(module)

    try:
        d = Devices()

        result = dict()

        # Get all devices in the workspace
        all_devices = d.get_all_devices(
            conn=glp_conn,
            select="macAddress",
        )

        # Create a Dict of mac_address to device information for easy lookup
        # Based on list of devices retrieved
        devices_macs = [
            device["macAddress"].lower().replace("-", ":").replace(".", ":")
            for device in all_devices
        ]

        # Check existing state for idempotency
        for device in devices_sanitized:
            if device["macAddress"] not in devices_macs:
                add_devices.append(device)

        # Application Assignment/Unassignment
        if add_devices:
            if module.check_mode:
                result = dict(
                    changed=True,
                    msg="Devices would be added in check mode",
                    devices_added=add_devices,
                )
                module.exit_json(**result)

            response = d.add_devices(conn=glp_conn, network=add_devices)

            if len(response) > 0 and isinstance(response, list):
                # If multiple devices added, check if any failed
                failed_devices = [
                    res for res in response if res.get("code") != 202
                ]
                if failed_devices:
                    module.fail_json(
                        msg=f"Failed to add some devices in inventory: {failed_devices}",
                        result=response,
                    )

            result["changed"] = True
            result["msg"] = "success"
            result["devices_added"] = add_devices
        else:
            result["changed"] = False
            result["msg"] = "Devices already in desired state, no changes made"
            result["devices_added"] = []

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
