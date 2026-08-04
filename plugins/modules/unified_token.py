#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: unified_token
short_description: Generate OAuth Token using unified credentials
description:
  - This module allows you to generate an OAuth Token using unified credentials.
  - Unified credentials are useful when your workflow needs HPE GreenLake Platform only, or both HPE GreenLake Platform and HPE Aruba Networking Central.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "2.1.0"
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
  workspace_id:
    description: >
      The GreenLake workspace ID associated with your GLP workspace
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Create OAuth Token with unified credentials for GLP only
  arubanetworks.hpeanw_central.unified_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: workspace-abc-123
  register: token_result
  no_log: true

- set_fact:
    unified_access_token: "{{ token_result['access_token'] }}"

"""

RETURN = r"""
access_token:
  description: OAuth Token generated using unified credentials
  type: str
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleUnifiedConnection,
    unified_base_argument_spec,
)


def main():
    module_args = dict(
        **unified_base_argument_spec(),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        unified_obj = ModuleUnifiedConnection(module)
        unified_conn = unified_obj.get_unified_conn()

        if unified_conn is None:
            module.fail_json(
                msg="Failed to establish connection using unified credentials"
            )

        result = unified_conn.token_info["unified"]["access_token"]
        module.exit_json(changed=True, access_token=result)
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection using unified credentials",
            exception=str(e),
        )


if __name__ == "__main__":
    main()
