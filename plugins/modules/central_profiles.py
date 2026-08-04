#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_profiles
short_description: Create or manage configuration profiles in HPE Aruba Networking Central
description:
  - This module allows you to create and manage configuration profiles in HPE Aruba Networking Central.
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
"""

EXAMPLES = r"""
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

"""

RETURN = r"""
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
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    central_base_argument_spec,
    get_central_connection,
)

import traceback
from pycentral.profiles import Profiles
from pycentral.utils.profile_utils import validate_local
import time


def main():
    module_args = dict(
        **central_base_argument_spec(),
        workspace_id=dict(type="str", required=False),
        tenant_id=dict(type="str", required=False),
        tenant_name=dict(type="str", required=False),
        config_dict=dict(type="dict", required=True),
        path=dict(type="str", required=True),
        name=dict(type="str", required=False, default=None),
        resource=dict(type="str", required=False, default=None),
        local=dict(type="dict", required=False, default={}),
        state=dict(
            type="str",
            default="merged",
            choices=["merged", "replaced", "deleted"],
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    path = module.params["path"]
    config = module.params["config_dict"]
    local = module.params["local"]
    resource = module.params["resource"]
    name = module.params["name"]
    state = module.params["state"]

    # Establish a connection to Central using provided credentials or access token
    central_conn = get_central_connection(module)

    try:
        profile_obj = Profiles(name=name, central_conn=central_conn)

        if path:
            profile_obj.set_path(path)

        profile_obj.set_config_dict(config)

        if name:
            profile_obj.set_name(name)
            # Path could be set by category
            path = profile_obj.get_path()
            # Check if name is in the last section of path
            path_sections = path.split("/")
            if path_sections and (name not in path_sections[-1]):
                profile_obj.set_path(path + "/" + name)
        if local and validate_local(local):
            local["scope-id"] = int(local["scope-id"])
            profile_obj.set_local_parameters(local)

        if not resource and local:
            module.fail_json(
                msg="Invalid values - Please provide a valid resource when using local profiles"
            )
        elif resource:
            profile_obj.set_resource(resource)

        modified = False
        result = dict()
        get_success, existing_obj_dict = profile_obj.get()

        # GET was unsuccessful due to invalid endpoint
        if not get_success and existing_obj_dict:
            err_msg = (
                "Invalid path - Please provide a valid path/endpoint"
                f", received: {profile_obj.get_path()}"
            )
            module.fail_json(
                msg=err_msg,
                result=result,
            )

        # Check mode implementation
        if module.check_mode:
            result = {"code": 200, "msg": {}, "headers": {}}

            # Use Create when resource does not exist
            if (
                state == "merged"
                and not get_success
                or (state == "merged" and get_success and not existing_obj_dict)
            ):
                modified = True
                result["msg"]["message"] = "New profile would be created"
                result["diff"] = {"before": {}, "after": config}

            # Use Update instead of Create if resource already exists
            elif state == "merged" and get_success and existing_obj_dict:
                # Compare existing config with desired config to show diff
                diff_found = False
                before_config = existing_obj_dict.copy()
                after_config = before_config.copy()

                for key, value in config.items():
                    if (
                        key not in existing_obj_dict
                        or existing_obj_dict[key] != value
                    ):
                        diff_found = True
                        after_config[key] = value

                if diff_found:
                    modified = True
                    result["msg"]["message"] = (
                        "Existing profile would be updated"
                    )
                    result["diff"] = {
                        "before": before_config,
                        "after": after_config,
                    }
                else:
                    modified = False
                    result["msg"]["message"] = (
                        "No changes needed - profile matches desired state"
                    )

            elif state == "replaced":
                if get_success and existing_obj_dict:
                    modified = True
                    result["msg"]["message"] = (
                        "Existing profile would be replaced (delete and recreate)"
                    )
                    result["diff"] = {
                        "before": existing_obj_dict,
                        "after": config,
                    }
                else:
                    modified = True
                    result["msg"]["message"] = "New profile would be created"
                    result["diff"] = {"before": {}, "after": config}

            elif state == "deleted":
                if get_success and existing_obj_dict:
                    modified = True
                    result["msg"]["message"] = "Profile would be deleted"
                    result["diff"] = {"before": existing_obj_dict, "after": {}}
                else:
                    modified = False
                    result["msg"]["message"] = (
                        "Profile does not exist - no deletion needed"
                    )

            module.exit_json(
                msg="Check mode: No changes made",
                changed=modified,
                result=result,
            )

        # Retry logic for 409 conflicts
        max_retries = 30
        # Total 3 seconds divided into 30 loops
        retry_delay = 4.0 / max_retries

        for attempt in range(max_retries):
            # Use Create when resource does not exist
            if (
                state == "merged"
                and not get_success
                or (state == "merged" and get_success and not existing_obj_dict)
            ):
                modified, result = profile_obj.create()

            # Use Update instead of Create if resource already exists
            elif state == "merged" and get_success and existing_obj_dict:
                modified, result = profile_obj.update(
                    compare_dict=existing_obj_dict
                )

            elif state == "replaced":
                # Some objects cannot be deleted - should it fail?
                modified, result = profile_obj.delete()
                modified, result = profile_obj.create()
            elif state == "deleted":
                modified, result = profile_obj.delete()

            # Check if we got a 409 conflict
            if "code" in result and result["code"] == 409:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    # Final attempt failed with 409
                    module.fail_json(
                        msg=f"Operation failed after {max_retries} retries due to conflict (409): {result['msg'].get('message', 'Resource conflict')}",
                        result=result,
                    )
            else:
                # No 409, break out of retry loop
                result["retry_attempts"] = attempt
                break

        # Failure occurs when the call was unsuccessful
        # In the case of DELETE a 400 is returned when a resource
        # does not exist therefore not a failure for idempotency
        if (
            "code" in result
            and 400 <= result["code"] < 600
            and state != "deleted"
        ):
            err_msg = (
                "Error from Central: "
                f"{result['code']} - {result['msg']['message']}"
            )
            if (
                "Invalid module name/configuration root element in the URL"
                in result["msg"]["message"]
            ):
                err_msg = (
                    "Invalid path - Please provide a valid path/endpoint"
                    f", received: {profile_obj.get_path()}"
                )
            module.fail_json(
                msg=err_msg,
                result=result,
            )
        # Fail when API does not allow for DELETE on endpoint
        elif (
            "code" in result
            and 400 == result["code"]
            and state == "deleted"
            and "Cannot" in result["msg"]["message"]
        ):
            err_msg = (
                "DELETE error from Central: "
                f"{result['code']} - {result['msg']['message']}"
            )
            module.fail_json(
                msg=err_msg,
                result=result,
            )
        elif "code" in result and 401 <= result["code"] < 600:
            err_msg = (
                "Error from Central: "
                f"{result['code']} - {result['msg']['message']}"
            )
            module.fail_json(
                msg=err_msg,
                result=result,
            )
        module.exit_json(msg="success", changed=modified, result=result)

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
