#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: classic_api
short_description: Execute generic API calls to Classic HPE Aruba Networking Central
description:
  - This module allows you to execute API calls to Classic HPE Aruba Networking Central.
  - It uses the classic connection plugin to handle authentication and API calls.
  - It does not handle refresh token or OAuth token generation; you must provide a valid access token.
author: "HPE Aruba Networking"
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
  method:
    description:
      - HTTP method to use for the API call
    type: str
    choices: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    default: 'GET'
    required: false
  path:
    description:
      - API endpoint path without BASE URL (e.g., /monitoring/v2/network)
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
- name: Get Sites from Classic Central
  arubanetworks.hpeanw_central.classic_api:
    base_url: "{{ classic_base_url }}"
    access_token: "{{ classic_access_token }}"
    method: GET
    path: "/central/v2/sites"
  register: sites_result
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


def main():
    module_args = dict(
        **classic_base_argument_spec(),
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
        resp = classic_conn.command(
            apiMethod=method, apiPath=path, apiData=data, apiParams=params
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
