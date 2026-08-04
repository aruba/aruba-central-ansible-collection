#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: central_sites
short_description: Create or manage Sites in HPE Aruba Networking Central
description:
  - This module allows you to create and manage Sites in HPE Aruba Networking Central.
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
  site_attributes:
    description: >
      Dictionary containing required data to configure the specified Site
    type: dict
    required: true
    suboptions:
      name:
        description:
          - The name of the Site
        type: str
        required: true
      address:
        description:
          - The street address of the Site
        type: str
        required: true
      city:
        description:
          - The city where the Site is located, can be any valid string but recommended to be in ISO format
        type: str
        required: true
      state:
        description:
          - The state or province where the Site is located, must be in ISO short name format ex) California
        type: str
        required: true
      country:
        description:
          - The country where the Site is located, must be in ISO short name format ex) United States
        type: str
        required: true
      zipcode:
        description:
          - The postal/zip code of the Site
        type: str
        required: true
      timezone:
        description:
          - The timezone for the Site
        type: str
        required: true
  state:
    description: >
      The state of the configuration after module completion:

      merged - Ansible merges the Site configuration with the provided configuration
      deleted - Ansible deletes the Site configuration
    type: str
    choices:
      - merged
      - deleted
    default: merged
"""

EXAMPLES = r"""
- name: Create a new Site
  arubanetworks.hpeanw_central.central_sites:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    site_attributes:
      name: SJ_Office
      address: "123 Main St"
      city: "San Jose"
      state: "California"
      country: "United States"
      zipcode: "12345"
      timezone: "America/Los_Angeles"
    state: merged

- name: Delete a Site
  arubanetworks.hpeanw_central.central_sites:
    base_url: https://us4.api.central.arubanetworks.com
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    site_attributes:
      name: Ansible-Demo-Site
    state: deleted

- name: Create a Site using unified credentials
  arubanetworks.hpeanw_central.central_sites:
    base_url: "{{ central_base_url }}"
    client_id: "{{ glp_client_id }}"
    client_secret: "{{ glp_client_secret }}"
    workspace_id: "{{ glp_workspace_id }}"
    site_attributes:
      name: SJ_Office
      address: "123 Main St"
      city: "San Jose"
      state: "California"
      country: "United States"
      zipcode: "12345"
      timezone: "America/Los_Angeles"
    state: merged
"""

RETURN = r"""
changed:
  description: True if the site was created/modified/deleted, False otherwise
  type: bool
  returned: always
  sample: true
msg:
  description: Message indicating success or failure of the site operation
  type: str
  returned: always
  sample: "Site Ansible_Site created successfully."
result:
  description: Boolean indicating if the operation was successful, or dictionary containing detailed response when operation fails
  returned: always
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule
from pycentral.scopes import Scopes
from pycentral.utils.scope_utils import validate_iso_location
from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils._module_pycentral_base import (  # NOQA
    central_base_argument_spec,
    get_central_connection,
)

import traceback


def check_attributes(desired_attrs, site_obj):
    """
    Check if the attributes in desired_attrs match those in the site_obj.
    If attributes don't match, update the site_obj with the desired values.

    :param desired_attrs: Dictionary of desired site attributes from Ansible playbook
    :param site_obj: Site object retrieved from Central API to compare against
    :return: True if all attributes match (no changes needed), False if differences found
    """
    for key, value in desired_attrs.items():
        # Compare each attribute from desired config with existing site object
        if getattr(site_obj, key, None) != value:
            # Update the site object with new value for later update operation
            setattr(site_obj, key, value)
            return False
    return True


def main():
    # Define module arguments combining base Central connection args with site-specific args
    module_args = dict(
        **central_base_argument_spec(),  # Includes base_url, client_id, client_secret, access_token
        workspace_id=dict(type="str", required=False),
        tenant_id=dict(type="str", required=False),
        tenant_name=dict(type="str", required=False),
        site_attributes=dict(
            type="dict", required=True
        ),  # Site configuration data
        state=dict(
            type="str",
            default="merged",
            choices=["merged", "deleted"],
        ),
    )

    # Initialize the Ansible module with argument spec
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Extract module parameters
    site_attributes = module.params["site_attributes"]
    state = module.params["state"]
    result = dict()  # Initialize result dictionary for return values

    # Validate that provided site attributes for location are in correct ISO format
    if all(key in site_attributes for key in ["country", "state", "city"]):
        try:
            validate_iso_location(
                country=site_attributes["country"],
                state=site_attributes["state"],
                city=site_attributes["city"],
            )
        except Exception as e:
            module.fail_json(msg=f"Failed to validate ISO location: {e}")

    # Establish a connection to Central using provided credentials or access token
    central_conn = get_central_connection(module)

    try:
        # Initialize Scopes object to interact with Central's site management API
        scopes = Scopes(central_conn)

        # Retrieve Site if it exists
        site_name = site_attributes["name"]
        site_object = scopes.find_site(site_names=site_name)

    except Exception as e:
        error_msg = str(e)
        # Continue if sites haven't been created yet
        if (
            "Failed to fetch sites from Central" in error_msg
            and "Sites are a required construct" in error_msg
        ):
            site_object = None
        else:
            module.fail_json(msg=f"Failed to retrieve site {site_name}: {e}")

    try:
        # Handle site creation or update (merged state)
        if state == "merged":
            # Check if a site with this name already exists
            if site_object:
                # Site exists - check if attributes need updating
                # Compare existing site attributes with desired attributes
                if check_attributes(site_attributes, site_object):
                    # No changes needed - site already matches desired state
                    module.exit_json(
                        changed=False,
                        msg=f"Site {site_attributes['name']} already exists.",
                        result=result,
                    )

                # Attributes differ - update the site with new values
                result = site_object.update()
                module.exit_json(
                    changed=result,
                    msg=f"Site {site_attributes['name']} updated successfully.",
                )

            # Site doesn't exist - create new site
            site_creation_result = scopes.create_site(
                site_attributes=site_attributes
            )

            # Verify site creation was successful
            if not site_creation_result:
                module.fail_json(
                    msg=f"Failed to create site {site_attributes['name']}.",
                    result=site_creation_result,
                )

            # Site created successfully - prepare success response
            result["changed"] = True
            result["msg"] = (
                f"Site {site_attributes['name']} created successfully."
            )
            result["result"] = site_creation_result

        # Handle site deletion (deleted state)
        elif state == "deleted":
            # Check if site exists before attempting deletion (idempotency)
            if not site_object:
                # Site doesn't exist - nothing to delete, return unchanged
                module.exit_json(
                    changed=False,
                    msg=f"Site {site_attributes['name']} does not exist.",
                    result=result,
                )

            # Site exists - proceed with deletion
            site_deletion_result = scopes.delete_site(site_name=site_name)

            # Verify site deletion was successful
            if not site_deletion_result:
                msg_str = (
                    f"Failed to delete site {site_attributes['name']}."
                    "Ensure no devices are assigned to this site before deletion."
                )
                module.fail_json(
                    msg=msg_str,
                    result=site_deletion_result,
                )

            # Site deleted successfully - prepare success response
            result["changed"] = True
            result["msg"] = (
                f"Site {site_attributes['name']} deleted successfully."
            )
            result["result"] = site_deletion_result

        # Return final result to Ansible
        module.exit_json(**result)

    except Exception as e:
        # Handle any unexpected errors during site operations
        module.fail_json(
            msg=f"Exception occurred: {str(e)}",
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    main()
