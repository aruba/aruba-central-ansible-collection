#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: central_inventory
short_description: HPE Aruba Networking Central dynamic inventory plugin
description:
  - Reads inventory from HPE Aruba Networking Central
  - Dynamically creates groups based on device attributes
  - Supports grouping by site, device type, model, and more
author: "HPE Aruba Networking"
version_added: "1.0.0"
options:
  plugin:
    description: Name of the plugin
    required: true
    choices: ['arubanetworks.hpeanw_central.central_inventory', 'central_inventory']
  central_base_url:
    description:
      - The base URL for the Central account including leading https://
      - Example https://de3.api.central.arubanetworks.com
    type: str
    required: true
    env:
      - name: ARUBA_CENTRAL_BASE_URL
  central_client_id:
    description:
      - The client ID for the Central account
      - Used to create OAuth token if access_token is not provided
    type: str
    required: false
    env:
      - name: ARUBA_CENTRAL_CLIENT_ID
  central_client_secret:
    description:
      - The client secret for the Central account
      - Used to create OAuth token if access_token is not provided
    type: str
    required: false
    env:
      - name: ARUBA_CENTRAL_CLIENT_SECRET
  central_access_token:
    description:
      - A generated OAuth token for authenticating API requests
      - If using environment variables, this value will be set automatically when generating a new token
    type: str
    required: false
    env:
      - name: ARUBA_CENTRAL_ACCESS_TOKEN
  groups:
    description:
      - List of groups to create in inventory
      - Available options are site, device_type, device_function, model, status, group
    type: list
    elements: str
    default: ['site', 'device_type']
  filters:
    description:
      - Filters to apply when fetching devices
    type: dict
    default: {}
    suboptions:
      device_type:
        description: Filter by device type (ACCESS_POINT, SWITCH, GATEWAY, etc.)
        type: list
        elements: str
      status:
        description: Filter by device status (ONLINE, OFFLINE, etc.)
        type: list
        elements: str
      site:
        description: Filter by site name
        type: list
        elements: str
  compose:
    description:
      - Create custom host variables using Jinja2 expressions
    type: dict
    default: {}
  keyed_groups:
    description:
      - Add hosts to dynamically created groups based on variables
    type: list
    elements: dict
    default: []
  strict:
    description:
      - If true, make invalid entries a fatal error
      - If false, skip invalid entries and continue
    type: bool
    default: false
  output_file:
    description:
      - Path to write the inventory as a YAML file
      - If specified, the inventory will be written to this file in addition to being returned
      - When an output file exists, the access_token from that file will be reused on subsequent runs to avoid generating a new token
      - Automatically sets inventory_file, inventory_dir, and central_* variables at the 'all' group level
    type: str
    required: false
  separator:
    description:
      - Separator to use in group names when using keyed_groups
    type: str
    default: '_'
"""

EXAMPLES = r"""
# Minimal example using environment variables
plugin: arubanetworks.hpeanw_central.central_inventory

# Example with explicit credentials
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_client_id: your_client_id
central_client_secret: your_client_secret

# Example with access token
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_access_token: your_access_token

# Example with custom grouping
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_client_id: your_client_id
central_client_secret: your_client_secret
groups:
  - site
  - device_type
  - model
  - status

# Example with filters
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_client_id: your_client_id
central_client_secret: your_client_secret
filters:
  device_type:
    - ACCESS_POINT
    - SWITCH
  status:
    - ONLINE

# Example with custom variables using compose
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_access_token: your_access_token
compose:
  ansible_host: ipv4
  device_fqdn: deviceName + '.' + siteName
  is_online: status == 'ONLINE'

# Example with keyed groups
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_access_token: your_access_token
keyed_groups:
  - key: model
    prefix: model
  - key: softwareVersion
    prefix: version
    separator: '_'

# Example with YAML output file
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://us4.api.central.arubanetworks.com
central_access_token: your_access_token
output_file: /path/to/central_devices_inventory.yml
"""

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable


from ansible.module_utils.six import string_types
import yaml
import os

try:
    from pycentral import NewCentralBase
    from pycentral.new_monitoring import MonitoringDevices

    HAS_PYCENTRAL = True
except ImportError:
    HAS_PYCENTRAL = False


class InventoryModule(BaseInventoryPlugin, Constructable):
    """HPE Aruba Networking Central dynamic inventory plugin"""

    NAME = "arubanetworks.hpeanw_central.central_inventory"

    def verify_file(self, path):
        """
        Verify that the inventory file is valid for this plugin

        :param path: Path to the inventory file
        :return: True if valid, False otherwise
        """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            valid = True
            # Check if file ends with expected extensions
            if path.endswith(
                (
                    "central.yml",
                    "central.yaml",
                    "central_inventory.yml",
                    "central_inventory.yaml",
                )
            ):
                valid = True
            else:
                # Check if plugin is specified in the file
                try:
                    with open(path, "r") as f:
                        content = f.read()
                        if "central_inventory" in content:
                            valid = True
                except Exception:
                    pass
        return valid

    def _get_connection(self, existing_token=None):
        """
        Create a connection to HPE Aruba Networking Central

        :return: NewCentralBase connection object
        """
        base_url = self.get_option("central_base_url")
        client_id = self.get_option("central_client_id")
        client_secret = self.get_option("central_client_secret")
        access_token = self.get_option("central_access_token")

        if not base_url:
            raise ValueError(
                "central_base_url is required for Central connection"
            )

        # Create connection dictionary
        conn_dict = {"new_central": {"base_url": base_url}}

        # Use access_token if provided, otherwise use client credentials
        if existing_token:
            conn_dict["new_central"]["access_token"] = existing_token

        # Override with central_access_token option if both are present
        if access_token:
            conn_dict["new_central"]["access_token"] = access_token

        if client_id and client_secret:
            conn_dict["new_central"]["client_id"] = client_id
            conn_dict["new_central"]["client_secret"] = client_secret
        elif not existing_token and not access_token:
            raise ValueError(
                "Either central_access_token or both central_client_id and central_client_secret are required"
            )

        try:
            central = NewCentralBase(token_info=conn_dict)

            token_info = central.token_info["new_central"]

            # Update environment variable with new access token
            if (
                "access_token" in token_info
                and os.environ.get("ARUBA_CENTRAL_CLIENT_ID")
                and os.environ.get("ARUBA_CENTRAL_CLIENT_SECRET")
            ):
                os.environ["ARUBA_CENTRAL_ACCESS_TOKEN"] = token_info[
                    "access_token"
                ]
            return central
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Central: {str(e)}")

    def _get_devices(self, central):
        """
        Fetch all devices from Central

        :param central: NewCentralBase connection object
        :return: List of device dictionaries
        """
        try:
            # Use the monitoring API to get all devices
            inventory = MonitoringDevices.get_all_device_inventory(
                central_conn=central
            )

            return inventory
        except Exception as e:
            raise ConnectionError(
                f"Error fetching devices from Central: {str(e)}"
            )

    def _apply_filters(self, devices):
        """
        Apply filters to the device list

        :param devices: List of all devices
        :return: Filtered list of devices
        """
        filters = self.get_option("filters")
        if not filters:
            return devices

        filtered_devices = []

        for device in devices:
            # Check device_type filter
            if "device_type" in filters:
                device_types = filters["device_type"]
                if device.get("deviceType") not in device_types:
                    continue

            # Check status filter
            if "status" in filters:
                statuses = filters["status"]
                if device.get("status") not in statuses:
                    continue

            # Check site filter
            if "site" in filters:
                sites = filters["site"]
                if device.get("siteName") not in sites:
                    continue

            filtered_devices.append(device)

        return filtered_devices

    def _sanitize_group_name(self, name):
        """
        Sanitize group name to be valid for Ansible

        :param name: Original group name
        :return: Sanitized group name
        """
        if not name:
            return "ungrouped"

        # Replace spaces and special characters with underscores
        name = str(name).lower()
        name = name.replace(" ", "_")
        name = name.replace("-", "_")
        name = name.replace(".", "_")
        name = name.replace("/", "_")

        # Remove any non-alphanumeric characters except underscores
        import re

        name = re.sub(r"[^a-z0-9_]", "", name)

        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = "g_" + name

        return name or "ungrouped"

    def _populate_groups(self, devices, central):
        """
        Create inventory groups based on device attributes

        :param devices: List of devices
        :param central: NewCentralBase connection object
        """
        group_by = self.get_option("groups")

        # Set common variables at the 'all' group level
        if devices:
            first_device = devices[0]
            if "inventory_file" in first_device:
                self.inventory.set_variable(
                    "all", "inventory_file", str(first_device["inventory_file"])
                )
            if "inventory_dir" in first_device:
                self.inventory.set_variable(
                    "all", "inventory_dir", str(first_device["inventory_dir"])
                )

        # Set Central connection parameters at the 'all' group level
        # Extract values from central.token_info
        if (
            hasattr(central, "token_info")
            and "new_central" in central.token_info
        ):
            token_info = central.token_info["new_central"]

            if "base_url" in token_info:
                self.inventory.set_variable(
                    "all", "central_base_url", str(token_info["base_url"])
                )

            if "access_token" in token_info:
                self.inventory.set_variable(
                    "all",
                    "central_access_token",
                    str(token_info["access_token"]),
                )

            if "client_id" in token_info:
                self.inventory.set_variable(
                    "all", "central_client_id", str(token_info["client_id"])
                )

            if "client_secret" in token_info:
                self.inventory.set_variable(
                    "all",
                    "central_client_secret",
                    str(token_info["client_secret"]),
                )

        for device in devices:
            # Use serial number or ID as the hostname
            hostname = device.get("serialNumber") or device.get("id")
            if not hostname:
                continue

            # Add host to inventory
            self.inventory.add_host(hostname)

            # Set host variables (skip inventory_file and inventory_dir as they're set at group level)
            for key, value in device.items():
                if key == "deviceFunction":
                    formatted_persona = device["deviceFunction"]
                    formatted_persona = formatted_persona.replace(
                        " ", "_"
                    ).upper()
                    self.inventory.set_variable(
                        hostname,
                        "deviceFunction",
                        str(device["deviceFunction"]),
                    )
                    self.inventory.set_variable(
                        hostname, "device_function_formatted", formatted_persona
                    )
                elif key not in (
                    "type",
                    "inventory_file",
                    "inventory_dir",
                    "central_client_id",
                    "central_client_secret",
                    "central_access_token",
                    "central_base_url",
                ):
                    self.inventory.set_variable(hostname, key, value)

            # Create groups based on configuration
            if "site" in group_by:
                site_name = device.get("siteName")
                if site_name:
                    group_name = "site_" + self._sanitize_group_name(site_name)
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            if "device_type" in group_by:
                device_type = device.get("deviceType")
                if device_type:
                    group_name = "type_" + self._sanitize_group_name(
                        device_type
                    )
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            if "device_function" in group_by:
                device_function = device.get("persona")
                if device_function:
                    group_name = "function_" + self._sanitize_group_name(
                        device_function
                    )
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            if "model" in group_by:
                model = device.get("model")
                if model:
                    group_name = "model_" + self._sanitize_group_name(model)
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            if "status" in group_by:
                status = device.get("status")
                if status:
                    group_name = "status_" + self._sanitize_group_name(status)
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            if "group" in group_by:
                device_group = device.get("deviceGroupName")
                if device_group:
                    group_name = "group_" + self._sanitize_group_name(
                        device_group
                    )
                    self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)

            # Apply composed variables
            self._set_composite_vars(
                self.get_option("compose"),
                self.inventory.get_host(hostname).get_vars(),
                hostname,
                strict=self.get_option("strict"),
            )

            # Apply keyed groups
            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                self.inventory.get_host(hostname).get_vars(),
                hostname,
                strict=self.get_option("strict"),
            )

    # Helper method to read token from existing inventory file
    def _read_token_from_output_file(self, output_file):
        """
        Read access token from existing inventory file

        :param output_file: Path to the inventory file
        :return: Access token string or None
        """
        try:
            with open(output_file, "r") as f:
                inventory_data = yaml.safe_load(f)

            # Check if 'all' and 'vars' exist in the inventory
            if (
                inventory_data
                and isinstance(inventory_data, dict)
                and "all" in inventory_data
                and isinstance(inventory_data["all"], dict)
                and "vars" in inventory_data["all"]
                and isinstance(inventory_data["all"]["vars"], dict)
            ):
                token = inventory_data["all"]["vars"].get(
                    "central_access_token"
                )

                # Validate token is not None and is a string
                if token is not None and isinstance(token, string_types):
                    return token

            return None
        except Exception as e:
            self.display.vvv(
                f"Could not read token from {output_file}: {str(e)}"
            )
            return None

    def _sanitize_key(self, key):
        """
        Convert keys to plain strings for YAML serialization

        :param key: Dict key to sanitize
        :return: Plain string key
        """
        if key is None:
            return ""
        return str(key)

    def _sanitize_value(self, value):
        """
        Convert Ansible internal types to plain Python types for YAML serialization

        :param value: Value to sanitize
        :return: Plain Python type
        """
        # Handle None
        if value is None:
            return None

        # Handle primitive types first
        if isinstance(value, (bool, int, float)):
            return value

        # Handle strings (including Ansible tagged strings)
        if isinstance(value, string_types):
            return str(value)

        # Handle dictionaries
        if isinstance(value, dict):
            return {
                self._sanitize_key(k): self._sanitize_value(v)
                for k, v in value.items()
            }

        # Handle lists and tuples
        if isinstance(value, (list, tuple)):
            return [self._sanitize_value(item) for item in value]

        # Handle sets
        if isinstance(value, set):
            return [self._sanitize_value(item) for item in value]

        # For any other object type, convert to string
        return str(value)

    def _write_inventory_to_yaml(self):
        """
        Write the inventory to a YAML file
        """
        output_file = self.get_option("output_file")
        if not output_file:
            return

        # Build inventory dictionary
        inventory_dict = {"all": {"hosts": {}, "children": {}}}

        # Get variables set at the 'all' group level
        if "all" in self.inventory.groups:
            all_group = self.inventory.groups["all"]
            all_group_vars = all_group.get_vars()
            # Filter out host-specific vars and only keep group-level vars
            if all_group_vars:
                inventory_dict["all"]["vars"] = {
                    self._sanitize_key(k): self._sanitize_value(v)
                    for k, v in all_group_vars.items()
                }

        # Get all hosts
        for host_name in self.inventory.hosts:
            host = self.inventory.get_host(host_name)
            if host_name == "localhost":
                continue

            host_vars = host.get_vars()
            # Exclude variables that should only be at the 'all' group level
            filtered_vars = {
                self._sanitize_key(k): self._sanitize_value(v)
                for k, v in host_vars.items()
                if k not in ("inventory_file", "inventory_dir")
            }
            inventory_dict["all"]["hosts"][host_name] = filtered_vars

        # Get all groups
        for group_name in self.inventory.groups:
            if group_name in ("all", "ungrouped"):
                continue

            group = self.inventory.groups[group_name]

            # Get hosts in this group
            group_hosts = {}
            for host in group.get_hosts():
                if host.name == "localhost":
                    continue
                host_vars = host.get_vars()
                # Exclude variables that should only be at the 'all' group level
                filtered_vars = {
                    self._sanitize_key(k): self._sanitize_value(v)
                    for k, v in host_vars.items()
                    if k
                    not in (
                        "inventory_file",
                        "inventory_dir",
                        "central_base_url",
                        "central_access_token",
                        "central_client_id",
                        "central_client_secret",
                    )
                }
                group_hosts[host.name] = filtered_vars

            # Get child groups
            child_groups = {}
            for child in group.child_groups:
                if child.name not in ("all", "ungrouped"):
                    child_groups[child.name] = {}

            if group_hosts or child_groups:
                inventory_dict["all"]["children"][group_name] = {}
                if group_hosts:
                    inventory_dict["all"]["children"][group_name]["hosts"] = (
                        group_hosts
                    )
                if child_groups:
                    inventory_dict["all"]["children"][group_name][
                        "children"
                    ] = child_groups

        # Write to file
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_file, "w") as f:
                yaml.dump(
                    inventory_dict, f, default_flow_style=False, sort_keys=False
                )

            self.display.vvv(f"Inventory written to {output_file}")
        except Exception as e:
            raise Exception(
                f"Failed to write inventory to {output_file}: {str(e)}"
            )

    def parse(self, inventory, loader, path, cache=True):
        """
        Parse the inventory file and populate inventory

        :param inventory: Ansible inventory object
        :param loader: Data loader
        :param path: Path to inventory file
        :param cache: Whether to use cache
        """
        # Check if pycentral is available
        if not HAS_PYCENTRAL:
            raise ImportError(
                "The pycentral library is required for this plugin. "
                "Install it using: pip install pycentral"
            )

        # Call base class method
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Read and validate configuration
        try:
            self._read_config_data(path)
        except Exception as e:
            raise Exception(f"Error reading config data: {str(e)}")
        # Read existing inventory file if output_file is specified and check for token
        output_file = self.get_option("output_file")

        existing_token = None
        if output_file and os.path.exists(output_file):
            try:
                existing_token = self._read_token_from_output_file(output_file)
                if existing_token:
                    self.display.vvv(
                        f"Found existing access token in {output_file}"
                    )
                    # Store access_token option if found in file
                    if not self.get_option("central_access_token"):
                        self.set_option("central_access_token", existing_token)
                        self.display.vvv(
                            "Using access token from existing output file"
                        )
            except Exception as e:
                self.display.warning(
                    f"Failed to read token from {output_file}: {str(e)}"
                )
        # Connect to Central
        try:
            central = self._get_connection(existing_token)
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {str(e)}")

        # Fetch devices
        try:
            devices = self._get_devices(central)
        except Exception as e:
            raise ConnectionError(f"Failed to fetch devices: {str(e)}")

        # Apply filters
        devices = self._apply_filters(devices)

        # Populate inventory
        self._populate_groups(devices, central)

        # Write to YAML file if output_file is specified
        self._write_inventory_to_yaml()
