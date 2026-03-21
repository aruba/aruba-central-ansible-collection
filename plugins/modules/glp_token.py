#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: glp_token
short_description: Generate OAuth Token for HPE GreenLake
description:
  - This module allows you to generate an OAuth Token for HPE GreenLake.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "1.0.0"
options:
  client_id:
    description: >
      The client ID for the GLP account, used to create OAuth token
    type: str
    required: true
  client_secret:
    description: >
      The client secret for the GLP account, used to create OAuth token
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Create OAuth Token for GLP
  arubanetworks.hpeanw_central.glp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    register: token_result
    no_log: True

- set_fact:
    glp_access_token: "{{ token_result['access_token'] }}"
"""

RETURN = r"""
access_token:
  description: OAuth Token generated from GLP
  type: str
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleGLPConnection,
)


def main():
    module_args = dict(
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
        glp_obj = ModuleGLPConnection(module)
        glp_conn = glp_obj.get_glp()

        if glp_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE GreenLake Platform"
            )
        result = glp_conn.token_info["glp"]["access_token"]
        module.exit_json(changed=True, access_token=result)
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to HPE GreenLake Platform",
            exception=str(e),
        )


if __name__ == "__main__":
    main()
