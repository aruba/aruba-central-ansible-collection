#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_device_groups_info
short_description: Retrieve Device Group(s) information in HPE Aruba Networking Central
description:
  - This module allows you to retrieve Device Group(s) in HPE Aruba Networking Central.
  - Provides various subsets to fetch different types of device group information.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
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
      Retrieve a subset of device groups and their information
    type: str
    required: false
    choices:
      - all_device_groups
      - device_group_by_name
      - device_group_by_id
    default: all_device_groups
  device_group_name:
    description: >
      Device Group name to retrieve when using device_group_by_name subset
    type: str
    required: false
  device_group_id:
    description: >
      Device Group ID to retrieve when using device_group_by_id subset
    type: int
    required: false
"""

EXAMPLES = r"""
- name: Get all device groups in Central
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: device_groups_result

- name: Get all device groups using access token
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: all_device_groups
  register: device_groups_result

- name: Get device group by name
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: device_group_by_name
    device_group_name: "Data Center Switches"
  register: device_groups_result

- name: Get device group by ID
  arubanetworks.hpeanw_central.central_device_groups_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: device_group_by_id
    device_group_id: 1122334455
  register: device_groups_result
"""

RETURN = r"""
device_groups:
  description: List of dictionaries containing details of device groups in Central
  returned: always
  type: dict
  contains:
    device_groups:
      description: Device group information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of device groups returned in the response
      type: int
      returned: on success
    msg:
      description: Detailed message or error information
      type: str
      returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from pycentral.scopes import Scopes
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleCentralConnection,
    central_base_argument_spec,
)

import traceback


def main():
    # Define module arguments combining base Central connection args with device group specific args
    module_args = dict(
        **central_base_argument_spec(),  # Includes base_url, client_id, client_secret, access_token
        subset=dict(
            type="str",
            default="all_device_groups",
            choices=[
                "all_device_groups",
                "device_group_by_name",
                "device_group_by_id",
            ],
        ),
        device_group_name=dict(type="str", required=False),
        device_group_id=dict(type="int", required=False),
    )

    # Initialize the Ansible module with argument spec
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Extract module parameters
    subset = module.params["subset"]
    device_group_name = module.params["device_group_name"]
    device_group_id = module.params["device_group_id"]

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
        # Initialize Scopes object to interact with Central's device group API
        scopes = Scopes(central_conn)
        result = dict()

        if subset == "all_device_groups":
            # Get all device groups in the Central account
            device_groups = scopes.device_groups

            # Convert device group objects to dictionaries for JSON serialization
            device_groups_list = []
            for device_group in device_groups:
                device_group_dict = {
                    "id": device_group.id,
                    "name": device_group.name,
                    "description": device_group.description,
                    "device_count": device_group.device_count,
                    "assigned_profiles": device_group.assigned_profiles,
                    "devices": device_group.devices,
                }
                device_groups_list.append(device_group_dict)

            result.update(
                {
                    "device_groups": device_groups_list,
                    "count": len(device_groups_list),
                }
            )

        elif subset == "device_group_by_name":
            # Get a specific device group by name
            if not device_group_name:
                module.fail_json(
                    msg="device_group_name is required when subset is device_group_by_name"
                )

            device_group_object = scopes.find_device_group(
                device_group_names=device_group_name
            )

            if device_group_object:
                device_group_dict = {
                    "id": device_group_object.id,
                    "name": device_group_object.name,
                    "description": device_group_object.description,
                    "device_count": device_group_object.device_count,
                    "assigned_profiles": device_group_object.assigned_profiles,
                    "devices": device_group_object.devices,
                }

                result.update(
                    {"device_groups": [device_group_dict], "count": 1}
                )
            else:
                module.fail_json(
                    msg=f"Get device group by name failed - {device_group_name} not found",
                )

        elif subset == "device_group_by_id":
            # Get a specific device group by scopeId
            if not device_group_id:
                module.fail_json(
                    msg="device_group_id is required when subset is device_group_by_id"
                )

            device_group_object = scopes.find_device_group(
                device_group_ids=device_group_id
            )

            if device_group_object:
                device_group_dict = {
                    "id": device_group_object.id,
                    "name": device_group_object.name,
                    "description": device_group_object.description,
                    "device_count": device_group_object.device_count,
                    "assigned_profiles": device_group_object.assigned_profiles,
                    "devices": device_group_object.devices,
                }

                result.update(
                    {"device_groups": [device_group_dict], "count": 1}
                )
            else:
                module.fail_json(
                    msg=f"Get device group by ID failed - {device_group_id} not found",
                )

        module.exit_json(msg="success", changed=False, **result)

    except Exception as e:
        # Handle any unexpected errors during device group retrieval
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
