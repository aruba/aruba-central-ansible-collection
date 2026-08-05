# HPE Aruba Networking Central Ansible Examples

This directory contains example Ansible playbooks demonstrating how to use the HPE Aruba Networking Central Ansible Collection.


## Inventory Configuration

These workflows take advantage of the unified credentials capabilities of HPE GreenLake Platform and Central. Edit the `basic_inventory.yml` file and replace the placeholder values with your credentials. Refer to [this guide](https://developer.arubanetworks.com/new-central/docs/making-api-calls#3-choosing-the-right-base-url) to find your Central Base URL and [this guide](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#creating-a-personal-api-client) to create GLP API client credentials and retrieve your GLP workspace ID:

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      central_base_url: <your_central_instance_url>
      glp_client_id: <your_glp_client_id>
      glp_client_secret: <your_glp_client_secret>
      glp_workspace_id: <your_glp_workspace_id>
      classic_base_url: <your_classic_central_url>
      classic_access_token: <your_classic_access_token>
```

Central and GLP modules accept `client_id`, `client_secret`, and `workspace_id` directly — no separate token generation step is required. Classic Central modules require a pre-generated `classic_access_token`.

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

### 5. Device Onboarding (`onboarding_example.yml`)

Demonstrates a typical end-to-end workflow for onboarding devices into HPE GreenLake Platform and Central.

**Requirements:**
- GLP credentials (`glp_client_id`, `glp_client_secret`, `glp_workspace_id`)
- Central Base URL (`central_base_url`)
- Classic Central credentials (`classic_base_url`, `classic_access_token`)
- Edit the `vars` section and device serial numbers / MAC addresses in the playbook

**Description:** This playbook covers the full onboarding sequence for access points:
1. Adds devices to GLP inventory by serial number and MAC address
2. Assigns devices to an application and subscription in GLP
3. Creates a site in Central
4. Assigns devices to the site via Classic Central APIs
5. Creates a device group and assigns devices for configuration management
6. Assigns device functions/personas (`CAMPUS_AP`) in Central

**Usage:**
```bash
ansible-playbook -i inventory.yml onboarding_example.yml
```

### 6. Advanced Device Onboarding (`onboarding_advanced_example.yml`)

Extends the basic onboarding example with dynamic device handling, automatically mapping devices to applications and subscriptions based on their part numbers.

**Requirements:**
- GLP credentials (`glp_client_id`, `glp_client_secret`, `glp_workspace_id`)
- Central Base URL (`central_base_url`)
- Classic Central credentials (`classic_base_url`, `classic_access_token`)
- Devices must already be present in GLP inventory
- Edit the `vars` section at the top of the playbook:
  - `site_name`: Name of the site to create in Central
  - `group_name`: Prefix for device type-specific group names
  - `application_region`: GreenLake region (e.g. `us-west`)
  - `onboard_list`: List of device serial numbers to onboard

**Description:** This playbook dynamically handles mixed-device onboarding:
1. Retrieves the full GLP device inventory
2. Filters it to the devices listed in `onboard_list`
3. Builds a part-number-to-application/subscription mapping from existing inventory data
4. Assigns each device to its appropriate application and subscription
5. Creates a site in Central
6. Assigns each device to the site and a per-device-type group in Classic Central
7. Assigns device functions/personas dynamically based on device type (`CAMPUS_AP`, `ACCESS_SWITCH`, or `MOBILITY_GW`)

**Usage:**
```bash
ansible-playbook -i inventory.yml onboarding_advanced_example.yml
```
