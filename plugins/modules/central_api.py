#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_api
short_description: Execute generic API calls to HPE Aruba Networking Central
description:
  - This module allows you to execute API calls to HPE Aruba Networking Central.
  - It uses the central connection plugin to handle authentication and API calls.
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
  method:
    description:
      - HTTP method to use for the API call
    type: str
    choices: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    default: 'GET'
    required: false
  path:
    description:
      - API endpoint path without BASE URL (e.g., /network-monitoring/v1alpha1/devices)
    type: str
    required: true
  data:
    description:
      - Data to be sent in the request body for POST, PUT, or PATCH requests
    type: dict
    required: false
    default: {}
  params:
    description:
      - URL query parameters
    type: dict
    required: false
    default: {}
"""

EXAMPLES = r"""
- name: Get list of all devices
  arubanetworks.hpeanw_central.central_api:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    method: GET
    path: "/network-monitoring/v1alpha1/devices"
  register: devices_result

- name: Assign Library Profile to Scope with Token
  arubanetworks.hpeanw_central.central_api:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: "{{central_access_token}}"
    method: POST
    path: "/network-config/v1alpha1/scope-maps"
    data:
      scope-map:
        - scope-name: "1234567897"
          persona: ACCESS_SWITCH
          resource: "layer2-vlan/404"
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
    ModuleCentralConnection,
    central_base_argument_spec,
)
import traceback


def main():
    module_args = dict(
        **central_base_argument_spec(),
        method=dict(
            type="str",
            default="GET",
            choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
        ),
        path=dict(type="str", required=True),
        data=dict(type="dict", default={}),
        params=dict(type="dict", default={}),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    method = module.params["method"]
    path = module.params["path"]
    data = module.params["data"]
    params = module.params["params"]

    try:
        central_obj = ModuleCentralConnection(module)
        central_conn = central_obj.get_central_conn()

        if central_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE Aruba Networking Central"
            )
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to HPE Aruba Networking Central",
            exception=str(e),
        )

    try:
        resp = central_conn.command(
            api_method=method, api_path=path, api_data=data, api_params=params
        )
        success = 200 <= resp["code"] < 300
        if success:
            module.exit_json(changed=True, result=resp)
        else:
            module.fail_json(
                msg=f"API returned error code {resp.get('code')} and the body is {data}",
                result=resp,
            )

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
