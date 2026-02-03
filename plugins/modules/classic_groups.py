#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: classic_groups
short_description: Assign or Unassign Devices to a Site in HPE Aruba Networking Central
description:
  - This module allows you to assign or unassign devices to a site in HPE Aruba Networking Central.
  - It does not handle refresh token or OAuth token generation; you must provide a valid access token.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "1.0.0"
options:
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
    required: false
    choices: ['ACCESS_POINT', 'SWITCH', 'GATEWAY']
    default: "ACCESS_POINT"
  devices:
    description: >
      List of device serial numbers to assign or unassign to the device group,
      state must be set to 'assigned' or 'unassigned'. All devices must be of the same type.
    type: list
    elements: str
    required: false
    default: []
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
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
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
      description: Response body
      type: dict or str
      returned: always
    headers:
      description: Response headers
      type: dict
      returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleClassicConnection,
    classic_base_argument_spec,
)
import traceback

# Classic API Endpoints to gather device information
GET_DEVICE_APIs = {
    "ACCESS_POINT": {"APIEndpoint": "monitoring/v2/aps", "deviceKey": "aps"},
    "SWITCH": {
        "APIEndpoint": "monitoring/v1/switches",
        "deviceKey": "switches",
    },
    "GATEWAY": {
        "APIEndpoint": "monitoring/v1/gateways",
        "deviceKey": "gateways",
    },
}


def get_devices_by_type(central_conn, device_type_attr):
    device_dict = {}
    offset = 0
    apiMethod = "GET"
    apiPath = device_type_attr["APIEndpoint"]
    headers = {}
    while True:
        apiParams = {"calculate_total": True, "offset": offset}
        resp = central_conn.command(
            apiMethod=apiMethod,
            apiPath=apiPath,
            apiParams=apiParams,
            headers=headers,
        )
        if resp["code"] == 200:
            resp_devices = resp["msg"][device_type_attr["deviceKey"]]
            if len(resp_devices) > 0:
                device_dict.update(
                    {
                        device["serial"]: device["group_name"]
                        for device in resp_devices
                    }
                )
            if resp["msg"]["total"] == len(device_dict):
                break
        else:
            break
        offset += 1
    return device_dict


def main():
    module_args = dict(
        **classic_base_argument_spec(),
        group_name=dict(type="str", required=True),
        group_attributes=dict(type="dict", required=False),
        device_type=dict(
            type="str",
            required=True,
            choices=["ACCESS_POINT", "SWITCH", "GATEWAY"],
        ),
        devices=dict(type="list", elements="str", required=True),
        state=dict(
            type="str",
            default="assigned",
            choices=["merged", "deleted", "assigned", "unassigned"],
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Add in logic to validate parameters based on state
    group_name = module.params["group_name"]
    group_attributes = module.params["group_attributes"]
    device_type = module.params["device_type"]
    devices = module.params["devices"]
    state = module.params["state"]
    result = dict()
    result["msg"] = ""

    try:
        classic_obj = ModuleClassicConnection(module)
        classic_conn = classic_obj.get_classic_conn()

        if classic_conn is None:
            module.fail_json(
                msg="Failed to establish connection to Classic HPE Aruba Networking Central"
            )
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to Classic HPE Aruba Networking Central",
            exception=str(e),
        )

    try:
        # Verify if group exists or not
        api_path = "configuration/v2/groups"
        api_method = "GET"
        api_data = None
        device_group_resp = classic_conn.command(
            apiPath=api_path,
            apiMethod=api_method,
            apiParams={"limit": 100, "offset": 0},
        )

        if device_group_resp["code"] != 200:
            module.fail_json(
                msg="Failed to retrieve device groups",
                result=device_group_resp,
            )

        group_names = [group[0] for group in device_group_resp["msg"]["data"]]

        # Need to implement update
        if group_name in group_names and state == "merged":
            if devices is None or len(devices) == 0:
                module.exit_json(
                    changed=False,
                    msg=f"Device Group {group_name} already exists.",
                )
            # Continue to assign devices to the existing group

        if state == "merged" and group_name not in group_names:
            # Create the device group
            api_path = "configuration/v3/groups"
            api_method = "POST"
            api_data = {
                "group": group_name,
                "group_attributes": group_attributes,
            }
            device_group_creation_resp = classic_conn.command(
                apiPath=api_path, apiMethod=api_method, apiData=api_data
            )
            if device_group_creation_resp["code"] != 201:
                module.fail_json(
                    msg=f"Failed to create device group: {group_name}",
                    result=device_group_creation_resp,
                )

            module.exit_json(
                changed=True,
                msg=f"Successfully created device group: {group_name}",
            )

        if (
            state in ["assigned", "unassigned"]
            and group_name not in group_names
        ):
            module.fail_json(
                msg=f"Device Group {group_name} does not exist in Classic Central."
            )

        device_group_mapping = get_devices_by_type(
            classic_conn, GET_DEVICE_APIs[device_type]
        )

        process_devices = []

        for device_serial_number in devices:
            if device_serial_number not in device_group_mapping:
                module.fail_json(
                    msg=f"Device {device_serial_number} not found in Classic Central."
                )

            if state == "assigned" or state == "merged":
                if (
                    device_group_mapping[device_serial_number]
                    and device_group_mapping[device_serial_number] == group_name
                ):
                    # Device already assigned to the group
                    result["msg"] += (
                        f" Device {device_serial_number} already assigned to group {group_name}."
                    )

                    continue

            elif state == "unassigned":
                if device_group_mapping[device_serial_number] != group_name:
                    # module.exit_json(changed=False, msg=f"Device {device_serial_number} is already unassigned from group {group_name} and current group is {device_group_mapping[device_serial_number]}.")
                    if device_group_mapping[device_serial_number]:
                        # Throw warning that device is assigned to different group
                        pass
                    result["msg"] += (
                        f" Device {device_serial_number} is already unassigned from group {group_name} and current group is {device_group_mapping[device_serial_number]}."
                    )
                    continue

            process_devices.append(device_serial_number)

        # Devices must be moved to default group when unassigned/group deleted
        if (state == "unassigned" or state == "deleted") and process_devices:
            # Unassign the devices from the group (assign to default group)
            api_path = "configuration/v1/devices/move"
            api_method = "POST"
            api_data = {"group": "default", "serials": process_devices}
            device_group_unassignment_resp = classic_conn.command(
                apiPath=api_path, apiMethod=api_method, apiData=api_data
            )
            if device_group_unassignment_resp["code"] != 200:
                module.fail_json(
                    msg=f"Failed to unassign devices from group {group_name}",
                    result=device_group_unassignment_resp,
                )
            module.exit_json(
                changed=True,
                msg=f"Successfully unassigned devices from group {group_name}",
            )

        if state == "deleted":
            if group_name not in group_names:
                module.exit_json(
                    changed=False,
                    msg=f"Device Group {group_name} does not exist, skipping deletion.",
                )

            # Delete the device group
            api_path = f"configuration/v1/groups/{group_name}"
            api_method = "DELETE"
            device_group_deletion_resp = classic_conn.command(
                apiPath=api_path, apiMethod=api_method
            )
            if device_group_deletion_resp["code"] != 200:
                module.fail_json(
                    msg=f"Failed to delete device group: {group_name}",
                    result=device_group_deletion_resp,
                )

            module.exit_json(
                changed=True,
                msg=f"Successfully deleted device group: {group_name}",
            )

        if (state == "assigned" or state == "merged") and process_devices:
            # Assign the devices to the group
            api_path = "configuration/v1/devices/move"
            api_method = "POST"
            api_data = {"group": group_name, "serials": process_devices}
            device_group_assignment_resp = classic_conn.command(
                apiPath=api_path, apiMethod=api_method, apiData=api_data
            )
            if device_group_assignment_resp["code"] != 200:
                module.fail_json(
                    msg=f"Failed to assign devices to group {group_name}"
                )

            module.exit_json(
                changed=True,
                msg=f"Devices successfully assigned to group {group_name}.",
                result={"devices": process_devices},
            )

        if not process_devices:
            module.exit_json(
                changed=False,
                msg=f"Devices {devices} already assigned to group {group_name}.",
            )

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
