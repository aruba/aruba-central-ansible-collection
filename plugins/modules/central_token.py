#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_token
short_description: Generate OAuth Token for HPE Aruba Networking Central
description:
  - This module allows you to generate an OAuth Token for HPE Aruba Networking Central.
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
      The client ID for the Central account, used to create OAuth token
    type: str
    required: true
  client_secret:
    description: >
      The client secret for the Central account, used to create OAuth token
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Create OAuth Token from Central
  arubanetworks.hpeanw_central.central_token:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: token_result

- set_fact:
    central_access_token: "{{ token_result['access_token'] }}"
"""

RETURN = r"""
access_token:
  description: OAuth Token generated from Central
  type: str
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleCentralConnection,
)


def main():
    module_args = dict(
        base_url=dict(
            type="str",
            required=True,
        ),
        client_id=dict(
            type="str",
            required=True,
        ),
        client_secret=dict(
            type="str",
            required=True,
            no_log=True,
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        central_obj = ModuleCentralConnection(module)
        central_conn = central_obj.get_central_conn()

        if central_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE Aruba Networking Central"
            )
        result = central_conn.token_info["new_central"]["access_token"]
        module.exit_json(changed=True, access_token=result)
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to HPE Aruba Networking Central",
            exception=str(e),
        )


if __name__ == "__main__":
    main()
