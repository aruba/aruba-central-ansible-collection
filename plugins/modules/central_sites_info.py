#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_sites_info
short_description: Retrieve Site(s) information in HPE Aruba Networking Central
description:
  - This module allows you to retrieve Site(s) in HPE Aruba Networking Central.
  - Provides various subsets to fetch different types of site information.
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
  subset:
    description: >
      Retrieve a subset of sites and their information
    type: str
    required: false
    choices:
      - all_sites
      - site_by_name
      - site_by_id
      - site_by_filter
    default: all_sites
  site_filter:
    description: >
      Filter expression for retrieving specific sites when using site_by_filter subset
    type: str
    required: false
  site_name:
    description: >
      Site name to retrieve when using site_by_name subset
    type: str
    required: false
  site_id:
    description: >
      Site scopeId to retrieve when using site_by_id subset
    type: int
    required: false
"""

EXAMPLES = r"""
- name: Get all sites in Central
  arubanetworks.hpeanw_central.central_sites_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: sites_result

- name: Get all sites using access token
  arubanetworks.hpeanw_central.central_sites_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: all_sites
  register: sites_result

- name: Get site by name
  arubanetworks.hpeanw_central.central_sites_info:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: site_by_name
    site_name: "SJ_Office"
  register: site_result

- name: Get site by ID
  arubanetworks.hpeanw_central.central_sites_info:
    base_url: https://us4.api.central.arubanetworks.com
    access_token: AABBCC-111222-333444-555666777888
    subset: site_by_id
    site_id: 1122334455
  register: site_result
"""

RETURN = r"""
sites:
  description: List of dictionaries containing details of sites in Central
  returned: always
  type: dict
  contains:
    sites:
      description: Site information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of sites returned in the response
      type: int
      returned: on success
    msg:
      description: Detailed message or error information
      type: str
      returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from pycentral.scopes import Scopes
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    ModuleCentralConnection,
    central_base_argument_spec,
)

import traceback


def main():
    # Define module arguments combining base Central connection args with site info specific args
    module_args = dict(
        **central_base_argument_spec(),  # Includes base_url, client_id, client_secret, access_token
        subset=dict(
            type="str",
            default="all_sites",
            choices=[
                "all_sites",
                "site_by_name",
                "site_by_id",
                "site_by_filter",
            ],
        ),
        site_name=dict(type="str", required=False),
        site_id=dict(type="int", required=False),
        site_filter=dict(type="str", required=False),
    )

    # Initialize the Ansible module with argument spec
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Extract module parameters
    subset = module.params["subset"]
    site_name = module.params["site_name"]
    site_id = module.params["site_id"]
    site_filter = module.params.get("site_filter")

    # Establish connection to HPE Aruba Networking Central
    try:
        central_obj = ModuleCentralConnection(module)
        central_conn = central_obj.get_central_conn()

        # Verify connection was established successfully
        if central_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE Aruba Networking Central"
            )
    except Exception as e:
        # Handle connection plugin loading errors
        module.fail_json(
            msg=f"Failed to load 'arubanetworks.hpeanw_central.central' connection plugin: {e}"
        )

    try:
        # Initialize Scopes object to interact with Central's site management API
        scopes = Scopes(central_conn)
        result = dict()

        if subset == "all_sites":
            # Get all sites in the Central account
            sites = scopes.sites

            # Convert site objects to dictionaries for JSON serialization
            sites_list = []
            for site in sites:
                site_dict = {
                    "id": site.id,
                    "name": site.name,
                    "address": site.address,
                    "city": site.city,
                    "state": site.state,
                    "country": site.country,
                    "zipcode": site.zipcode,
                    "timezone": site.timezone,
                }
                sites_list.append(site_dict)

            result.update({"sites": sites_list, "count": len(sites_list)})

        elif subset == "site_by_filter":
            # Apply filter to get specific sites
            if not site_filter:
                module.fail_json(
                    msg="site_filter is required when subset is site_by_filter"
                )

            filter_result = scopes.get_sites(filter_field=site_filter)

            if filter_result and filter_result["code"] == 200:
                sites_list = filter_result["msg"]["items"]
                count = filter_result["msg"]["count"]
                result.update({"sites": sites_list, "count": count})
            else:
                module.fail_json(
                    msg=f"Get sites by filter failed - {filter_result}",
                )

        elif subset == "site_by_name":
            # Get a specific site by name
            if not site_name:
                module.fail_json(
                    msg="site_name is required when subset is site_by_name"
                )

            site_object = scopes.find_site(site_names=site_name)

            if site_object:
                site_dict = {
                    "id": site_object.id,
                    "name": site_object.name,
                    "address": site_object.address,
                    "city": site_object.city,
                    "state": site_object.state,
                    "country": site_object.country,
                    "zipcode": site_object.zipcode,
                    "timezone": site_object.timezone,
                }
                result.update({"sites": [site_dict]})
            else:
                module.fail_json(
                    msg=f"Get site by name failed - {site_name} not found",
                )

        elif subset == "site_by_id":
            # Get a specific site by ID
            if not site_id:
                module.fail_json(
                    msg="site_id is required when subset is site_by_id"
                )

            site_object = scopes.find_site(site_ids=site_id)

            if site_object:
                site_dict = {
                    "id": site_object.id,
                    "name": site_object.name,
                    "address": site_object.address,
                    "city": site_object.city,
                    "state": site_object.state,
                    "country": site_object.country,
                    "zipcode": site_object.zipcode,
                    "timezone": site_object.timezone,
                }
                result.update({"sites": [site_dict], "count": 1})
            else:
                module.fail_json(
                    msg=f"Get site by ID failed - {site_id} not found",
                )

        module.exit_json(msg="success", changed=False, **result)

    except Exception as e:
        # Handle any unexpected errors during site retrieval
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
