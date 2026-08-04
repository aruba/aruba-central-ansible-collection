#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_api
short_description: Execute generic API calls to HPE GreenLake Platform
description:
  - This module allows you to execute API calls to HPE GreenLake Platform.
  - It uses the glp connection plugin to handle authentication and API calls.
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
  method:
    description:
      - HTTP method to use for the API call
    type: str
    choices: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    default: 'GET'
    required: false
  path:
    description:
      - API endpoint path without BASE URL (e.g., /subscriptions/v1/subscriptions)
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
- name: Get list of all subscriptions
  arubanetworks.hpeanw_central.glp_api:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    method: GET
    path: " /subscriptions/v1/subscriptions"
  register: subscriptions_result

- name: Get list of all subscriptions using unified credentials
  arubanetworks.hpeanw_central.glp_api:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: 1234567890
    method: GET
    path: " /subscriptions/v1/subscriptions"
  register: subscriptions_result

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
    glp_base_argument_spec,
    get_glp_connection,
)
import traceback


def main():
    module_args = dict(
        **glp_base_argument_spec(),
        workspace_id=dict(type="str", required=False),
        tenant_id=dict(type="str", required=False),
        tenant_name=dict(type="str", required=False),
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

    # Establish a connection to GreenLake Platform using provided credentials or access token
    glp_conn = get_glp_connection(module)

    try:
        resp = glp_conn.command(
            api_method=method,
            api_path=path,
            api_data=data,
            api_params=params,
            app_name="glp",
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
