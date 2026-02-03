#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_devices_info
short_description: Retrieve Device(s) information in HPE Aruba Networking Central
description:
  - This module allows you to retrieve Device(s) in HPE Aruba Networking Central.
  - Provides various subsets to fetch different types of device information.
author: "HPE Aruba Networking"
version_added: "1.0.0"
options:
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
  device_filter:
    description: >
      Filter expression for retrieving specific devices when using device_by_filter subset
    type: str
    required: false       
"""

EXAMPLES = r"""
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
    device_filter: "deviceType eq SWITCH"
  register: devices_result  
"""

RETURN = r"""
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
"""

from ansible.module_utils.basic import AnsibleModule
from pycentral.new_monitoring import MonitoringDevices
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleCentralConnection,
    central_base_argument_spec,
)

import traceback


def main():
    module_args = dict(
        **central_base_argument_spec(),  # Includes base_url, client_id, client_secret, access_token
        subset=dict(
            type="str",
            default="all_devices",
            choices=[
                "all_devices",
                "device_by_serial",
                "device_by_id",
                "device_by_filter",
            ],
        ),
        device_serial=dict(type="str", required=False),
        device_id=dict(type="int", required=False),
        device_filter=dict(type="str", required=False),
    )

    # Initialize the Ansible module with argument spec
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Extract module parameters
    subset = module.params["subset"]
    device_serial = module.params["device_serial"]
    device_id = module.params["device_id"]
    device_filter = module.params["device_filter"]

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
        result = dict()

        if subset == "all_devices" or subset == "device_by_filter":
            # Combining both all_devices and device_by_filter since they have similar logic
            if subset == "device_by_filter" and not device_filter:
                module.fail_json(
                    msg="device_filter is required when subset is device_by_filter"
                )

            # Get all devices in the Central account using MonitoringDevices class
            # endpoints called:
            # /network-monitoring/v1alpha1/device-inventory
            # /network-monitoring/v1alpha1/devices
            monitoring_devices = MonitoringDevices.get_all_devices(
                central_conn=central_conn, filter_str=device_filter
            )

            monitoring_devices_dict = {
                device["id"]: device for device in monitoring_devices
            }
            inventory = MonitoringDevices.get_all_device_inventory(
                central_conn=central_conn, filter_str=device_filter
            )
            inventory_devices_dict = {
                device["id"]: device for device in inventory
            }
            for device in inventory_devices_dict.keys():
                if device in monitoring_devices_dict:
                    inventory_devices_dict[device].update(
                        monitoring_devices_dict[device]
                    )

            result.update(
                {
                    "devices": list(inventory_devices_dict.values()),
                    "count": len(inventory_devices_dict.keys()),
                }
            )

        elif subset == "device_by_serial" or subset == "device_by_id":
            # Combining both device_by_serial and device_by_id since they have similar logic
            if subset == "device_by_serial" and not device_serial:
                module.fail_json(
                    msg="device_serial is required when subset is device_by_serial"
                )

            if subset == "device_by_id" and not device_id:
                module.fail_json(
                    msg="device_id is required when subset is device_by_id"
                )

            # Get all devices in the Central account using MonitoringDevices class
            # endpoints called:
            # /network-monitoring/v1alpha1/device-inventory
            # /network-monitoring/v1alpha1/devices
            monitoring_devices = MonitoringDevices.get_all_devices(
                central_conn=central_conn
            )

            monitoring_devices_dict = {
                device["id"]: device for device in monitoring_devices
            }
            inventory = MonitoringDevices.get_all_device_inventory(
                central_conn=central_conn
            )
            inventory_devices_dict = {
                device["id"]: device for device in inventory
            }

            device_info = None
            for device in inventory_devices_dict.keys():
                if (
                    device_serial
                    and device == device_serial
                    and device in monitoring_devices_dict
                ) or (
                    device_id
                    and inventory_devices_dict[device]["scopeId"]
                    == str(device_id)
                ):
                    inventory_devices_dict[device].update(
                        monitoring_devices_dict[device]
                    )
                    device_info = inventory_devices_dict[device]
                    break

            if device_info:
                result.update({"devices": [device_info], "count": 1})
            else:
                if subset == "device_by_serial":
                    module.fail_json(
                        msg=f"Get device by serial number failed - {device_serial} not found",
                    )
                else:
                    module.fail_json(
                        msg=f"Get device by ID failed - {device_id} not found",
                    )

        module.exit_json(msg="success", changed=False, **result)

    except Exception as e:
        # Handle any unexpected errors during devices retrieval
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
