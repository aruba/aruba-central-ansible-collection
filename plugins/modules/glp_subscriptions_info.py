#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_subscriptions_info
short_description: Retrieve a list of subscriptions managed in HPE GreenLake Platform.
description:
  - This module allows you to retrieve information about subscriptions managed in HPE GreenLake Platform.
  - Provides various subsets to fetch different types of subscription information.
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
  subset:
    description: >
      Retrieve a subset of subscriptions and their information
    type: str
    required: false
    choices:
      - all_subscriptions
      - subscription_by_filter
    default: all_subscriptions
  subscription_filter:
    description: >
      Filter expression for retrieving specific subscriptions when using subscription_by_filter subset.
      Filter expressions consist of simple comparison operations joined by logical operators.
    type: str
    required: false
  select:
    description: >
      A comma separated list of properties to display in the response
    type: str
    required: false
"""

EXAMPLES = r"""
- name: Get all subscriptions in GLP
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: subscriptions_result

- name: Get subscriptions with specific fields
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    access_token: AABBCC-111222-333444-555666777888
    subset: all_subscriptions
    select: "id,key"
  register: subscriptions_result

- name: Get Subscriptions by Filter
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: subscription_by_filter
    subscription_filter: "subscriptionType eq 'CENTRAL_GW'"
  register: subscriptions_result
"""

RETURN = r"""
subscriptions:
  description: List of dictionaries containing details of subscriptions in GLP
  returned: always
  type: dict
  contains:
    subscriptions:
      description: Subscription information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of subscriptions returned
      type: int
      returned: on success with subscription_by_filter subset
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
from pycentral.glp import Subscriptions


def main():
    module_args = dict(
        **glp_base_argument_spec(),
        subset=dict(
            type="str",
            default="all_subscriptions",
            choices=[
                "all_subscriptions",
                "subscription_by_filter",
            ],
        ),
        subscription_filter=dict(
            type="str",
            required=False,
        ),
        select=dict(type="str", required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    subset = module.params["subset"]
    subscription_filter = module.params["subscription_filter"]
    select = module.params["select"]

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
        s = Subscriptions()
        result = dict()

        if subset == "all_subscriptions":
            # Get all subscriptions in the workspace
            all_subscriptions = s.get_all_subscriptions(
                conn=glp_conn, select=select
            )
            result.update({"subscriptions": all_subscriptions})

        elif subset == "subscription_by_filter":
            # Get subscriptions matching a specific filter
            if not subscription_filter:
                module.fail_json(
                    msg="subscription_filter is required when subset is subscription_by_filter"
                )

            resp = s.get_subscription(
                conn=glp_conn,
                filter=subscription_filter,
                select=select,
            )

            if resp["code"] != 200:
                module.fail_json(
                    msg=f"Error fetching subscriptions by filter: {resp['code']} - {resp['msg']}"
                )

            result.update(
                {
                    "subscriptions": resp["msg"]["items"],
                    "count": resp["msg"]["count"],
                }
            )

        module.exit_json(msg="success", changed=False, **result)

    except Exception as e:
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
