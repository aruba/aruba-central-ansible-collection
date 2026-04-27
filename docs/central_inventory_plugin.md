# HPE Aruba Networking Central Dynamic Inventory Plugin

## Overview

The `central_inventory` plugin is an Ansible dynamic inventory plugin that automatically discovers and organizes network devices from HPE Aruba Networking Central into structured Ansible inventory groups. This eliminates the need to manually maintain inventory files and ensures your Ansible inventory is always synchronized with your actual network infrastructure.

## What It Does

The plugin connects to HPE Aruba Networking Central's API and:

1. **Fetches all network devices** from your Central account ([token_only option](#token-only-mode) can skip this step and only refresh the token in the output YAML).
2. **Organizes devices into logical groups** based on attributes like:
   - Site location
   - Device type (Switch, Gateway, Access Point)
   - Device model
   - Provisioning status
   - Device group assignment
3. **Extracts device metadata** as host variables (IP addresses, serial numbers, firmware versions, etc.)
4. **Stores Central credentials** at the inventory level for reuse in playbooks
5. **Optionally exports** the inventory to a static YAML file

## Configuration

### Minimal Configuration

```yaml
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://internal.api.central.arubanetworks.com
central_client_id: your_client_id
central_client_secret: your_client_secret
```

### Full Configuration Options

```yaml
plugin: arubanetworks.hpeanw_central.central_inventory

# Authentication (choose one method)
central_base_url: https://internal.api.central.arubanetworks.com
central_access_token: your_access_token  # Method 1: Direct token

# OR
central_client_id: your_client_id        # Method 2: OAuth credentials
central_client_secret: your_client_secret

# Grouping options (default: ['site', 'device_type'])
groups:
  - site           # Groups by siteName
  - device_type    # Groups by deviceType (SWITCH, GATEWAY, ACCESS_POINT)
  - model          # Groups by device model
  - status         # Groups by status (ONLINE, OFFLINE)
  - group          # Groups by deviceGroupName

# Filtering options
filters:
  device_type:
    - ACCESS_POINT
    - SWITCH
  status:
    - ONLINE
  site:
    - Building_A
    - ADL-Collin

# Export to static file
output_file: /path/to/central_devices_inventory.yml
token_only: true  # Optional: refresh token only, skip device discovery

# Custom host variables using Jinja2
compose:
  ansible_host: ipv4
  is_online: status == 'ONLINE'

# Dynamic grouping
keyed_groups:
  - key: model
    prefix: model
  - key: softwareVersion
    prefix: version
    separator: '_'
```

## How It Works

### Authentication Flow

1. **Token Reuse**: If `output_file` exists, the plugin reads the stored `central_access_token` and reuses it
2. **New Connection**: If no token exists or is expired, it authenticates using:
   - Provided `central_access_token`, OR
   - OAuth with `central_client_id` and `central_client_secret`
3. **Token Storage**: The active token is stored in the output file for subsequent runs

### Token-Only Mode

Set `token_only: true` with `output_file` to skip device retrieval and inventory/group generation.
In this mode, the plugin updates only `all.vars.central_access_token` in the YAML file and preserves all other content.

### Device Discovery

1. Connects to Central's Monitoring API
2. Fetches all devices in Central's device inventory using [`MonitoringDevices.get_all_device_inventory()`](https://pycentral.readthedocs.io/en/v2/modules/new_monitoring/#pycentral.new_monitoring.devices.MonitoringDevices.get_all_device_inventory)
3. Applies any configured filters
4. Creates inventory groups based on device attributes
5. Assigns devices to appropriate groups
6. Exports to YAML if `output_file` is specified

## Expected Output Format

### Inventory Structure

The plugin generates a hierarchical inventory with:

```yaml
all:
  vars:                    # Shared variables for all hosts
    central_base_url: ...
    central_access_token: ...
    central_client_id: ...
    central_client_secret: ...
  
  hosts:                   # All discovered devices
    <serialNumber>:        # Device serial as hostname
      <device_attributes>
  
  children:                # Dynamic groups
    site_<site_name>:      # Site-based groups
      hosts: ...
    type_<device_type>:    # Type-based groups
      hosts: ...
    model_<model>:         # Model-based groups
      hosts: ...
```

### Example Output

Based on the generated inventory, here's what you can expect:

#### 1. All-Level Variables (Shared Across All Hosts)

```yaml
all:
  vars:
    central_base_url: https://internal.api.central.arubanetworks.com
    central_access_token: eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2...
    central_client_id: e8e333303-f720-446a-8034-6bbf2f39039c
    central_client_secret: 4f722244464d416fac41f6b7ebc00ca5
```

#### 2. Host Entries (Device Details)

Each device becomes a host with comprehensive metadata:

```yaml
all:
  hosts:
    CNSKKLB00C:              # Serial number as hostname
      status: ONLINE
      deviceType: GATEWAY
      model: 9004-US
      deviceName: Aruba9004_63_89_1E
      macAddress: f0:1a:a0:63:89:1e
      ipv4: 0.0.0.0
      siteName: LSV-WPA3-PSK-Site
      siteId: '49171617624236032'
      deviceGroupName: ADL-Lucas
      softwareVersion: 10.7.2.2_94048
      firmwareVersion: 10.7.2.2_94048
      tier: ADVANCE_70XX
      persona: Mobility Gateway
      deviceFunction: Mobility GW
      isProvisioned: 'Yes'
      inventory_hostname: CNSKKLB00C
      group_names:
        - site_lsv_wpa3_psk_site
        - type_gateway
```

#### 3. Dynamic Groups

**Site-Based Groups:**
```yaml
all:
  children:
    site_building_a:
      hosts:
        CNSKKLB0DW:    # Gateway
        VNQ7KZD4P5:    # Access Point
    
    site_adl_collin:
      hosts:
        TW3BLZB0V5:    # Switch
        VNQ7KZD4JB:    # Access Point
```

**Type-Based Groups:**
```yaml
all:
  children:
    type_switch:
      hosts:
        TW3BLZB0VB:
        TW3BLZB0V5:
        SG38LMY056:
        SG38LMY07R:
    
    type_gateway:
      hosts:
        CNSKKLB00C:
        CNSKKLB09T:
        CNSKKLB0DW:
    
    type_access_point:
      hosts:
        VNQ7KZD4MS:
        VNQ7KZD4P5:
        VNQ7KZD4J7:
```

## Available Host Variables

Each device includes the following variables:

### Core Identifiers
- `serialNumber` - Device serial number
- `macAddress` - Device MAC address
- `deviceName` - Friendly name
- `id` - Unique device ID
- `scopeId` - Device scope identifier

### Network Information
- `ipv4` - IPv4 address (null if unprovisioned)
- `status` - Current status (ONLINE, OFFLINE, null)
- `siteName` - Assigned site name
- `siteId` - Site identifier

### Device Classification
- `deviceType` - SWITCH, GATEWAY, ACCESS_POINT
- `deviceFunction` - Functional role (e.g., "Mobility GW", "Campus AP")
- `persona` - Device persona (e.g., "Access Switch", "Campus Access Point")
- `model` - Device model (e.g., "6200F", "9004-US", "AP-615-US")
- `partNumber` - Part number
- `tier` - Subscription tier (e.g., "ADVANCED_SWITCH_6200", "ADVANCE_70XX")

### Software & Provisioning
- `softwareVersion` - Installed software version
- `firmwareVersion` - Firmware version
- `isProvisioned` - "Yes" or "No"
- `deployment` - Deployment type (Standalone, Campus AP, etc.)

### Organizational
- `deviceGroupName` - Assigned device group
- `deviceGroupId` - Group identifier
- `role` - Device role (if assigned)
- `stackId` - Stack ID (null for non-stacked devices)

## Use Cases

### 1. Automated Device Configuration

Target specific device types:
```bash
ansible-playbook configure_switches.yml -i central_inventory.yml --limit type_switch
```

### 2. Site-Specific Deployments

Deploy configurations to specific sites:
```bash
ansible-playbook deploy.yml -i central_inventory.yml --limit site_building_a
```

### 3. Status-Based Operations

Target only online devices:
```yaml
# In your inventory config
filters:
  status:
    - ONLINE
```

### 4. Accessing Central Credentials in Playbooks

The plugin stores credentials at the `all` group level, making them available in your playbooks:

```yaml
- name: Make Central API call
  arubanetworks.hpeanw_central.central_api:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    endpoint: /monitoring/v2/devices
```

### 5. Device Auditing

Generate reports on device status, versions, and provisioning:
```bash
ansible-inventory -i central_inventory.yml --list > device_audit.json
```

## Group Naming Convention

The plugin sanitizes group names to be Ansible-compatible:

- Spaces → underscores (`Building A` → `building_a`)
- Hyphens → underscores (`LSV-WPA3` → `lsv_wpa3`)
- Lowercase conversion
- Numeric prefixes get `g_` prefix (`6300` → `g_6300`)

**Group Prefixes:**
- `site_` - Site-based groups
- `type_` - Device type groups
- `model_` - Model-based groups
- `status_` - Status-based groups
- `group_` - Device group-based groups

## Troubleshooting

### Authentication Failures
- Verify `central_base_url` [matches your region](https://developer.arubanetworks.com/new-central/docs/getting-started-with-rest-apis#api-gateway-base-urls)
- Check client ID/secret or token validity


## Related Documentation

- [Central API Documentation](https://developer.arubanetworks.com/new-central/docs/about)
- [Ansible Inventory Plugins](https://docs.ansible.com/ansible/latest/plugins/inventory.html)
- [pycentral Library](https://pycentral.readthedocs.io/en/v2/)
