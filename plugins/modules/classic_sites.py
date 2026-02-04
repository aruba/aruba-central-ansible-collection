#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: classic_sites
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
  site_name:
    description: >
      The name of the site to which devices will be assigned or unassigned
    type: str
    required: true
  device_type:
    description: >
      The type of devices to assign or unassign (e.g., ACCESS_POINT, SWITCH, GATEWAY)
    type: str
    required: true
    choices: ['ACCESS_POINT', 'SWITCH', 'GATEWAY']
  devices:
    description:
      - List of device serial numbers to assign or unassign to the site, all devices must be of the same type
    type: list
    elements: str
    required: true
  state:
    description: >
      Desired state of the devices with respect to the site
    type: str
    required: false
    choices: ['assigned', 'unassigned']
    default: 'assigned'
"""

EXAMPLES = r"""
- name: Assign devices to a site
  arubanetworks.hpeanw_central.classic_sites:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    site_name: "SiteA"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: assigned

- name: Unassign devices from a site
  arubanetworks.hpeanw_central.classic_sites:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    site_name: "SiteA"
    devices:
      - "ABC1234567"
      - "XYZ9876543"
    state: unassigned
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
      description: Response body (can be dict or str depending on API response)
      type: raw
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
from pycentral.monitoring import Sites
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

# New to Classic Central Device Type Mapping
DEVICE_TYPE_MAPPING = {
    "ACCESS_POINT": "IAP",
    "SWITCH": "SWITCH",
    "GATEWAY": "CONTROLLER",
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
                        device["serial"]: device["site"]
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
        site_name=dict(type="str", required=True),
        device_type=dict(
            type="str",
            required=True,
            choices=["ACCESS_POINT", "SWITCH", "GATEWAY"],
        ),
        devices=dict(type="list", elements="str", required=True),
        state=dict(
            type="str", default="assigned", choices=["assigned", "unassigned"]
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    site_name = module.params["site_name"]
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
        s = Sites()
        # Retrieve the Classic Site ID for the given site name
        classic_site_id = s.find_site_id(conn=classic_conn, site_name=site_name)

        if not classic_site_id:
            module.exit_json(
                changed=False,
                msg=f"Site {site_name} not found in Classic Central.",
            )

        device_site_mapping = get_devices_by_type(
            classic_conn, GET_DEVICE_APIs[device_type]
        )

        process_devices = []
        classic_device_type = DEVICE_TYPE_MAPPING[device_type]

        for device_serial_number in devices:
            if device_serial_number not in device_site_mapping:
                module.fail_json(
                    msg=f"Device {device_serial_number} not found in Classic Central."
                )

            if state == "assigned":
                if (
                    device_site_mapping[device_serial_number] is not None
                    and device_site_mapping[device_serial_number] != site_name
                ):
                    module.fail_json(
                        msg=f"Device {device_serial_number} is already assigned to site "
                        f"{device_site_mapping[device_serial_number]}. Please remove the device "
                        f"from the site before assigning it to a new site."
                    )

                elif (
                    device_site_mapping[device_serial_number]
                    and device_site_mapping[device_serial_number] == site_name
                ):
                    # Device already assigned to the site
                    result["msg"] += (
                        f" Device {device_serial_number} already assigned to site {site_name}."
                    )

                    continue

            elif state == "unassigned":
                if device_site_mapping[device_serial_number] != site_name:
                    # Already unassigned from this site
                    if device_site_mapping[device_serial_number]:
                        # Throw warning that device is assigned to different site
                        pass
                    result["msg"] += (
                        f" Device {device_serial_number} is already unassigned from site {site_name} "
                        f"and current site is {device_site_mapping[device_serial_number]}."
                    )
                    continue
            process_devices.append(device_serial_number)

        if state == "unassigned" and process_devices:
            # Unassign the devices from the site
            site_unassociation_resp = s.unassociate_devices(
                conn=classic_conn,
                site_id=classic_site_id,
                device_type=classic_device_type,
                device_ids=process_devices,
            )
            if site_unassociation_resp["code"] != 200:
                module.fail_json(
                    msg=f"Failed to unassociate devices {site_unassociation_resp['msg']['failed']} "
                    f"from site {site_name}. Error: {site_unassociation_resp['msg']}",
                    result=site_unassociation_resp,
                )

            module.exit_json(
                changed=True,
                msg=f"Devices {site_unassociation_resp['msg']['success']} successfully unassigned from site {site_name}.",
            )

        if state == "assigned" and process_devices:
            # Assign the devices to the site
            site_association_resp = s.associate_devices(
                conn=classic_conn,
                site_id=classic_site_id,
                device_type=classic_device_type,
                device_ids=process_devices,
            )
            if site_association_resp["code"] != 200:
                module.fail_json(
                    msg=f"Failed to associate devices {site_association_resp['msg']['failed']} with site {site_name}. Error: {site_association_resp['msg']}",
                    result=site_association_resp,
                )

            module.exit_json(
                changed=True,
                msg=f"Devices {site_association_resp['msg']['success']} successfully assigned to site {site_name}.",
            )

        if not process_devices:
            if state == "assigned":
                module.exit_json(
                    changed=False,
                    msg=f"Devices {devices} already assigned to site {site_name}.",
                )
            else:
                module.exit_json(
                    changed=False,
                    msg=f"Devices {devices} already unassigned from site {site_name}.",
                )

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
