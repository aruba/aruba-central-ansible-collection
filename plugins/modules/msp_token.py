#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: msp_token
short_description: Generate OAuth Token for HPE Aruba Networking Central MSP
description:
  - This module allows you to generate an OAuth Token for HPE Aruba Networking Central MSP.
  - Supports generating both workspace-level and tenant-level tokens.
  - When tenant_id or tenant_name is provided, a tenant-scoped token is returned.
author: Ti Chiapuzio-Wong (@tchiapuziowong)
version_added: "2.0.0"
options:
  client_id:
    description: >
      The client ID for the MSP workspace ID, used to create OAuth token
    type: str
    required: true
  client_secret:
    description: >
      The client secret for the MSP workspace ID, used to create OAuth token
    type: str
    required: true
  msp_workspace_id:
    description: >
      The GreenLake workspace ID associated with the MSP workspace
    type: str
    required: true
  tenant_id:
    description: >
      The tenant ID to generate a tenant-scoped token for, can be with or without dashes
      If provided, the module returns a token scoped to this tenant
    type: str
    required: false
  tenant_name:
    description: >
      The tenant name to generate a tenant-scoped token for
      If provided, the module returns a token scoped to this tenant
    type: str
    required: false
"""

EXAMPLES = r"""
- name: Create MSP workspace-level OAuth Token
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    msp_workspace_id: workspace-abc-123
  register: token_result

- set_fact:
    msp_access_token: "{{ token_result['msp_access_token'] }}"

- name: Create tenant-scoped OAuth Token by tenant ID
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    msp_workspace_id: workspace-abc-123
    tenant_id: tenant-abc-123
  register: tenant_token_result

- name: Create tenant-scoped OAuth Token by tenant name
  arubanetworks.hpeanw_central.msp_token:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    msp_workspace_id: workspace-abc-123
    tenant_name: MyTenant
  register: tenant_token_result

- set_fact:
    tenant_access_token: "{{ tenant_token_result['tenant_access_token'] }}"

- set_fact:
    msp_access_token: "{{ tenant_token_result['msp_access_token'] }}"
"""

RETURN = r"""
msp_access_token:
  description: OAuth Token generated for the MSP workspace or tenant
  type: str
  returned: success
tenant_access_token:
  description: OAuth Token generated for the MSP workspace or tenant
  type: str
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleMSPConnection,
    msp_base_argument_spec,
)


def main():
    module_args = dict(
        **msp_base_argument_spec(),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Determine Tenant Token or Workspace Token based on provided parameters
    tenant_id = module.params["tenant_id"]
    tenant_name = module.params["tenant_name"]

    try:
        msp_obj = ModuleMSPConnection(module)
        msp_conn = msp_obj.get_msp_conn()

        if msp_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE Aruba Networking Central"
            )

        msp_result = msp_conn.token_info["unified"]["access_token"]

        if tenant_id or tenant_name:
            tenant_conn = msp_obj.get_tenant_conn()
            tenant_result = tenant_conn.token_info["unified"]["access_token"]
            module.exit_json(
                changed=True,
                msp_access_token=msp_result,
                tenant_access_token=tenant_result,
            )

        module.exit_json(changed=True, msp_access_token=msp_result)
    except Exception as e:
        module.fail_json(
            msg=f"Failed to establish connection to HPE Aruba Networking Central : {str(e)}",
        )


if __name__ == "__main__":
    main()
