#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_devices
short_description: Allows for application & subscription assignment of devices managed in HPE GreenLake Platform.
description:
  - This module allows for application & subscription assignment of devices in HPE GreenLake Platform.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "1.0.0"
options:
  client_id:
    description: >
      The client ID for the GLP account, used to create OAuth token, required if access_token is not provided
    type: str
    required: false
  client_secret:
    description: >
      The client secret for the GLP account, used to create OAuth token, required if access_token is not provided
    type: str
    required: false
  access_token:
    description: >
      A generated OAuth token for authenticating API requests
    type: str
    required: false
  devices:
    description: >
      List of device serial numbers to assign/unassign to the application and/or subscription
    type: list
    elements: str
    required: true
  application:
    description: >
      Retrieve a subset of devices and their information
    type: dict
    required: false
    suboptions:
      id:
        description: >
          ID of application to assign devices to
        type: str
      name:
        description: >
          Name of application to assign devices to
        type: str
      region:
        description: >
          Region of application to assign devices to
        type: str
  subscription_key:
    description: >
      Key of subscription to assign devices to
    type: str
    required: false
  state:
    description: >
      Desired state of the devices
    type: str
    required: false
    choices: ['assigned', 'unassigned']
    default: 'assigned'
"""

EXAMPLES = r"""
- name: Assign devices to application and subscription with client credentials
  arubanetworks.hpeanw_central.glp_devices:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    application:
      name: HPE Aruba Networking Central
      region: "US West"
    subscription_key: "sub-key-123"
    devices:
      - "SN123456789"
      - "SN987654321"
    state: "assigned"
  register: devices_result

- name: Assign devices to application and subscription
  glp_devices:
    client_id: "111222-333444-555666777888"
    client_secret: "888777666555444333222111"
    application:
      name: "MyApp"
      region: "eu-central"
    subscription_key: "sub-key-456"
    state: "assigned"
  register: devices_result

- name: Unassign devices from application and subscription
  glp_devices:
    access_token: "AABBCC-111222-333444-555666777888"
    application:
      name: "MyApp"
    subscription_key: "sub-key-789"
    state: "unassigned"
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
    ModuleGLPConnection,
    glp_base_argument_spec,
)
import traceback
from pycentral.glp import Devices, ServiceManager, Subscriptions


def main():
    module_args = dict(
        **glp_base_argument_spec(),
        devices=dict(type="list", elements="str", required=True),
        application=dict(
            type="dict",
            required=False,
            options=dict(
                id=dict(type="str"),
                name=dict(type="str"),
                region=dict(type="str"),
            ),
        ),
        subscription_key=dict(type="str", required=False),
        state=dict(
            type="str",
            required=False,
            choices=["assigned", "unassigned"],
            default="assigned",
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    state = module.params["state"]
    devices = module.params["devices"]
    application = module.params["application"]
    subscription_key = module.params["subscription_key"]

    try:
        glp_obj = ModuleGLPConnection(module)
        glp_conn = glp_obj.get_glp()

        if glp_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE GreenLake Platform"
            )

    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to HPE GreenLake Platform",
            exception=str(e),
        )

    try:
        d = Devices()
        sm = ServiceManager()
        sub = Subscriptions()

        result = dict()

        # Get all devices in the workspace
        all_devices = d.get_all_devices(
            conn=glp_conn,
            select="id,serialNumber,assignedState,application,region,subscription",
        )

        # Create a Dict of serial_number to device information for easy lookup
        # Based on list of devices retrieved
        devices_by_serial = {
            device["serialNumber"]: {
                k: v for k, v in device.items() if k != "serialNumber"
            }
            for device in all_devices
        }

        # Mapping used for reporting
        id_to_serial_dict = {
            device["id"]: device["serialNumber"]
            for device in all_devices
            if device["serialNumber"] in devices
        }

        if len(id_to_serial_dict.keys()) != len(devices):
            missing_serials = set(devices) - {
                dev["serialNumber"] for dev in id_to_serial_dict
            }
            module.fail_json(
                msg=f"The following serial numbers were not found in GLP: {', '.join(missing_serials)}"
            )

        app_details = None
        sub_id = None
        # Application Assignment
        if application:
            if (
                "id" in application
                and application["id"]
                and "region" in application
                and application["region"]
            ):
                app_details = {
                    "id": application["id"],
                    "region": application.get("region"),
                }
            else:
                app_details = sm.get_application_id_and_region(
                    conn=glp_conn,
                    application_name=application["name"],
                    region=application["region"],
                )
            # Fail is application is invalid
            if not app_details:
                module.fail_json(
                    msg=f"Invalid application {application['name']} not found in GLP"
                )
        if subscription_key:
            # Get Subscription ID returns tuple
            sub_id_result, sub_id = sub.get_sub_id(
                conn=glp_conn, key=subscription_key
            )
            # Fail is subscription key is invalid
            if not sub_id:
                module.fail_json(
                    msg=f"Invalid subscription key {subscription_key} not found in GLP"
                )

        # List to track devices that need to be assigned or subscribed
        # If state is deleted then these lists will track devices to be unassigned or unsubscribed
        unassigned = []
        unsubscribed = []

        # Check existing state for idempotency
        for serial_number, device_info in devices_by_serial.items():
            if serial_number not in devices:
                continue  # Skip devices not in the target list
            # Check application assignment
            if state == "assigned":
                if device_info["assignedState"] != "ASSIGNED_TO_SERVICE":
                    unassigned.append(device_info["id"])
                elif (
                    device_info["application"]["id"] != app_details["id"]
                    or device_info["region"] != app_details["region"]
                ):
                    unassigned.append(device_info["id"])

                # Check subscription assignment
                if device_info["subscription"] is None or (
                    isinstance(device_info["subscription"], list)
                    and device_info["subscription"][0]["id"] != sub_id
                ):
                    unsubscribed.append(device_info["id"])
            elif state == "unassigned":
                # Check application assignment
                if device_info["assignedState"] == "ASSIGNED_TO_SERVICE":
                    unassigned.append(device_info["id"])
                elif (
                    device_info["application"] is not None
                    and device_info["application"]["id"] == app_details["id"]
                ):
                    unassigned.append(device_info["id"])

                # Check subscription assignment
                if (
                    device_info["subscription"] is not None
                    and device_info["subscription"][0]["id"] == sub_id
                ):
                    unsubscribed.append(device_info["id"])

        # Application Assignment/Unassignment
        if unassigned and application:
            if state == "assigned":
                app_result = d.assign_devices(
                    conn=glp_conn,
                    application=app_details["id"],
                    region=app_details["region"],
                    devices=unassigned,
                )

                if app_result["code"] != 200:
                    module.fail_json(
                        msg="Failed to assign devices to application",
                        result=app_result,
                    )

                result["changed"] = True
                result["msg"] = "success"
                result["devices_assigned"] = [
                    id_to_serial_dict[device_id] for device_id in unassigned
                ]
            elif state == "unassigned":
                app_result = d.unassign_devices(
                    conn=glp_conn,
                    devices=unassigned,
                )

                if app_result["code"] != 200:
                    module.fail_json(
                        msg="Failed to unassign devices from application",
                        result=app_result,
                    )

                result["changed"] = True
                result["msg"] = "success"
                result["devices_unassigned"] = [
                    id_to_serial_dict[device_id] for device_id in unassigned
                ]

        # Devices are in desired assigned/unassigned state
        elif not unassigned and application:
            if state == "unassigned":
                result["msg"] = (
                    "Devices already unassigned from the application."
                )
            else:
                result["msg"] = (
                    "Devices already assigned to the desired application."
                )
            result["changed"] = False

        # Subscription Assignment/Unassignment
        if subscription_key and unsubscribed:
            if state == "assigned":
                sub_result = d.add_sub(
                    conn=glp_conn,
                    devices=unsubscribed,
                    sub=subscription_key,
                    key=True,
                )

                # Results are returned as list so each entry must be validated
                for entry in sub_result:
                    if entry["code"] != 200:
                        module.fail_json(
                            msg="Failed to add subscription to devices",
                            result=entry,
                        )

                result["changed"] = True
                result["msg"] = "success"
                result["devices_subscribed"] = [
                    id_to_serial_dict[device_id] for device_id in unsubscribed
                ]
            if state == "unassigned":
                sub_result = d.remove_sub(
                    conn=glp_conn,
                    devices=unsubscribed,
                )
                # Results are returned as list so each entry must be validated
                for entry in sub_result:
                    if entry["code"] != 200:
                        module.fail_json(
                            msg="Failed to remove subscription from devices",
                            result=entry,
                        )

                result["changed"] = True
                result["msg"] = "success"
                result["devices_unsubscribed"] = [
                    id_to_serial_dict[device_id] for device_id in unsubscribed
                ]

        # Devices are in desired subscribed/unsubscribed state
        elif not unsubscribed and subscription_key:
            if state == "unassigned":
                result["msg"] = (
                    result.get("msg", "")
                    + " Devices already unsubscribed from the desired subscription."
                )
            elif state == "assigned":
                result["msg"] = (
                    result.get("msg", "")
                    + " Devices already subscribed with the desired subscription."
                )
            # Possibly changed due to previous application/subscription assignment
            if "changed" not in result:
                result["changed"] = False

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
