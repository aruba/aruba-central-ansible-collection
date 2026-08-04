#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_devices_info
short_description: Retrieve a list of devices managed in HPE GreenLake Platform.
description:
  - This module allows you to retrieve information about devices managed in HPE GreenLake Platform.
  - Provides various subsets to fetch different types of device information.
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
"""

EXAMPLES = r"""
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

- name: Get all devices using unified credentials
  arubanetworks.hpeanw_central.glp_devices_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: 1234567890
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
        subset=dict(
            type="str",
            default="all_devices",
            choices=[
                "all_devices",
                "device_by_filter",
                "device_by_id",
                "device_by_serial",
            ],
        ),
        device_filter=dict(
            type="str",
            required=False,
        ),
        select=dict(type="str", required=False),
        device_id=dict(type="str", required=False),
        serial_number=dict(type="str", required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    subset = module.params["subset"]
    device_filter = module.params["device_filter"]
    select = module.params["select"]
    device_id = module.params["device_id"]
    serial_number = module.params["serial_number"]

    # Establish a connection to GreenLake Platform using provided credentials or access token
    glp_conn = get_glp_connection(module)

    try:
        d = Devices()
        result = dict()

        if subset == "all_devices":
            # Get all devices in the workspace
            all_devices = d.get_all_devices(conn=glp_conn, select=select)
            result.update({"devices": all_devices})

        elif subset == "device_by_filter":
            # Get devices matching a specific filter
            if not device_filter:
                module.fail_json(
                    msg="device_filter is required when subset is device_by_filter"
                )

            resp = d.get_device(
                conn=glp_conn, filter=device_filter, select=select
            )

            if resp["code"] != 200:
                module.fail_json(
                    msg=f"Error fetching devices by filter: {resp['code']} - {resp['msg']}"
                )

            result.update(
                {"devices": resp["msg"]["items"], "count": resp["msg"]["count"]}
            )

        elif subset == "device_by_id":
            # Get a specific device by ID
            if not device_id:
                module.fail_json(
                    msg="device_id is required when subset is device_by_id"
                )

            # Use filter to get a specific device by ID
            device_filter = f"id eq '{device_id}'"
            resp = d.get_device(
                conn=glp_conn, filter=device_filter, select=select
            )

            if resp["code"] != 200:
                module.fail_json(
                    msg=f"Error fetching device by ID: {resp['code']} - {resp['msg']}"
                )

            if resp["msg"]["count"] == 0:
                # Should we fail if not found?
                result.update({"devices": [], "message": "Device ID not found"})
            else:
                result.update({"devices": resp["msg"]["items"]})

        elif subset == "device_by_serial":
            # Get a device by serial number
            if not serial_number:
                module.fail_json(
                    msg="serial_number is required when subset is device_by_serial"
                )

            # Get device ID from serial
            id_result = d.get_device_id(glp_conn, serial_number)

            if not id_result[0]:
                result.update({"devices": [], "message": id_result[1]})
            else:
                # Use the ID to get full device details
                device_id = id_result[1]
                device_filter = f"id eq '{device_id}'"
                resp = d.get_device(
                    conn=glp_conn, filter=device_filter, select=select
                )

                if resp["code"] != 200:
                    module.fail_json(
                        msg=f"Error fetching device by serial: {resp['code']} - {resp['msg']}"
                    )

                result.update({"devices": resp["msg"]["items"]})

        module.exit_json(msg="success", changed=False, **result)

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
