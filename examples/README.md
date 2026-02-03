# HPE Aruba Networking Central Ansible Examples

This directory contains example Ansible playbooks demonstrating how to use the HPE Aruba Networking Central Ansible Collection.


## Inventory Configuration

Edit the `inventory.yml` file and replace the placeholder values with your Central API credentials. Refer to [this guide](https://developer.arubanetworks.com/new-central/docs/making-api-calls#3-choosing-the-right-base-url) on how to find your Base URL and use this guide for instructions on [how to generate and manage an access token](https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens):

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      central_base_url: <your_central_instance_url>
      central_client_id: <your_client_id>
      central_client_secret: <your_client_secret>
```

## Available Examples

### 1. Central API Demo (`central_api_demo.yml`)

Demonstrates basic API calls to HPE Aruba Networking Central using the `central_api` module.

**Description:** This playbook retrieves a list of devices from Central and displays the result.

**Usage:**
```bash
ansible-playbook -i inventory.yml central_api_demo.yml
```

### 2. Central Profiles Demo (`central_profiles_demo.yml`)

Demonstrates creating library profiles in Central including VLANs, default gateways, and VRFs.

**Description:** This playbook creates several library profiles that can be assigned to devices or sites:
- A VLAN profile (VLAN 100)
- A default gateway profile
- Multiple VRF profiles

**Usage:**
```bash
ansible-playbook -i inventory.yml central_profiles_demo.yml
```

### 3. AOS-CX Local Profiles (`central_cx_local_profiles.yml`)

Demonstrates creating and assigning device-specific local profiles for AOS-CX switches.

**Requirements:** 
- Edit the variables section at the top of the playbook:
  - `site_scope_id`: Your site's scope ID in Central
  - `switch_serial`: Serial number of your AOS-CX switch
  - `switch_scope_id`: The device scope ID of your AOS-CX switch
  - `switch_persona`: The switch persona (e.g. ACCESS_SWITCH)

**Description:** This playbook:
1. Creates a library VLAN profile
2. Assigns the VLAN profile to a site scope
3. Configures multiple switch interfaces with specific VLANs
4. Creates a custom banner for the switch

**Usage:**
```bash
ansible-playbook -i inventory.yml central_cx_local_profiles.yml
```

### 4. Undo AOS-CX Local Profiles (`undo_central_cx_local_profiles.yml`)

Reverses the changes made by the `central_cx_local_profiles.yml` playbook.

**Requirements:**
- Same variable requirements as `central_cx_local_profiles.yml`

**Description:** This playbook:
1. Removes the custom banner from the switch
2. Resets interface configurations to defaults
3. Unassigns the VLAN profile from the site scope
4. Deletes the library VLAN profile

**Usage:**
```bash
ansible-playbook -i inventory.yml undo_central_cx_local_profiles.yml
```
