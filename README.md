> **⚠️Disclaimer Regarding Participation in Beta Testing:**
> This Ansible collection is currently in a **pre-release, beta state** and is being made available for testing and evaluation purposes only. The functionality, performance, and design of this collection are **subject to change** and may continue to evolve as development progresses. While Hewlett Packard Enterprise has conducted internal testing and validation, **no guarantee of full stability, completeness, or production readiness** is provided at this stage.
>Participants in this beta program acknowledge that this code is **not intended for use in production environments** and should only be deployed in controlled, non-production settings. It is strongly advised that users conduct their own validation and testing to ensure suitability within their specific environments.
>This collection's features and final design may change prior to its general availability. The expected timeline for full support and public release of this Ansible collection **is independent of the general availability of the new HPE Aruba Networking Central product**.
>Any use of this pre-release software is subject to the terms and conditions communicated by Hewlett Packard Enterprise and may be further governed by existing confidentiality agreements, where applicable.


# HPE Aruba Networking Central Ansible Collection

This Ansible collection provides modules and plugins to interact with [HPE Aruba Networking Central](https://developer.arubanetworks.com/new-central/docs/about) and HPE GreenLake Platform to manage resources, gather information, and much more!

## Requirements

- Ansible 2.19 or lower
- Python 3.6 or later
- [pycentral v2](https://pycentral.readthedocs.io/en/v2/) Python SDK
    `pip3 install --pre pycentral`


## Installation
The beta version of the collection is provided within Ansible Galaxy and can be installed through the following command:
```bash
ansible-galaxy collection install arubanetworks.hpeanw_central
```
  
  
Additionally, the bundled version of the collection is provided within the repository itself and can be installed through the following command:
```bash
ansible-galaxy collection install arubanetworks-hpeanw_central-2.0.0-beta.tar.gz -f
```

## Authentication

Each module in the HPE Aruba Networking Central Collection expects authentication credentials. Depending on the module those credentials may apply to new Central or GLP. Refer to the [module's documentation](./docs/) for guidance.  

### New Central:  
1. **Base URL**: Provide `base_url` which is the base URL for HPE Aruba Networking Central (e.g., https://us4.api.central.arubanetworks.com). Refer to [this guide](https://developer.arubanetworks.com/new-central/docs/making-api-calls#3-choosing-the-right-base-url) on how to find your Base URL for Central.
2. **Client ID and Client Secret**: Provide `client_id` and `client_secret` to automatically generate and manage OAuth2 tokens. Use this guide for instructions on [how to generate and manage an access token](https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens) for HPE Aruba Networking Central.
3. **Pre-generated Token**: Alternatively, a pre-generated OAuth2 token can be provided directly through the parameter `access_token`, remove if no longer valid. When provided the collection will always attempt to use provided token, upon failure will generate a new one if `client_id` and `client_secret` are provided but will not be saved.

### HPE GreenLake Platform (GLP):  
- GLP does not require a Base URL.
1. **Client ID and Client Secret**: Provide `client_id` and `client_secret` to automatically generate and manage OAuth2 tokens. Use this guide for instructions on [how to generate and manage an access token](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client) for HPE GreenLake Platform.
2. **Pre-generated Token**: Alternatively, [a pre-generated OAuth2 token](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token) can be provided directly through the parameter `access_token`, remove if no longer valid. When provided the collection will always attempt to use provided token, upon failure will generate a new one if `client_id` and `client_secret` are provided but will not be saved.

### Classic Central:  
1. **Base URL**: Provide `base_url` which is the base URL for classic HPE Aruba Networking Central (e.g., https://apigw-uswest5.central.arubanetworks.com). Refer to [this guide](https://developer.arubanetworks.com/central/docs/api-oauth-access-token#table-domain-urls-for-api-gateway-access) on how to find your Base URL for classic Central.
2. **Pre-generated Access Token**: A pre-generated OAuth2 access token is required for each module through the parameter `access_token`. This collection does not support the automatic generation of a new access token, upon expiration a new valid token must be provided.


For each platform (except classic Central), it is recommended to use the `<platform>_token` module to generate an OAuth token for the session then provide the generated token to each module like so:
#### Central Example  
```yaml
---
- name: Generate Token and Create Libary Profile
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create OAuth Token from Central
      arubanetworks.hpeanw_central.central_token:
        base_url: https://us4.api.central.arubanetworks.com
        client_id: 111222-333444-555666777888
        client_secret: 888777666555444333222111
      register: token_result
      no_log: True

    - set_fact:
        central_access_token: "{{ token_result['access_token'] }}"
      no_log: True

    - name: Create a new Library VLAN profile with generated token
      arubanetworks.hpeanw_central.central_profiles:
        base_url: https://us4.api.central.arubanetworks.com
        access_token: "{{ central_access_token }}"
        name: 100
        path: "layer2-vlan"
        config_dict:
          vlan: 100
          name: "Corp-VLAN"
          description: "Corporate VLAN for main office"
        state: merged
```  

#### GLP Example  
```yaml
---
# Example playbook for HPE GreenLake Platform API calls
- name: Demo HPE GreenLake Platform Devices Info
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Generate Token for Session
      arubanetworks.hpeanw_central.glp_token:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
      register: token_result
      no_log: True

    - name: Get Devices in GLP with Token
      arubanetworks.hpeanw_central.glp_devices_info:
        access_token: "{{token_result['access_token']}}"
      register: devices_result
```

### Host/Inventory Variables

Configure the following host/inventory variable to define the connection:

- `ansible_connection`: Must be set to `local`

## Dynamic Inventory Plugin

This collection includes the `central_inventory` plugin that automatically discovers and organizes network devices from HPE Aruba Networking Central into Ansible inventory groups. This eliminates manual inventory maintenance and ensures your inventory is always synchronized with your network infrastructure.

### Quick Start

Create an inventory configuration file (e.g., `central_inventory.yml`):

```yaml
plugin: arubanetworks.hpeanw_central.central_inventory
central_base_url: https://internal.api.central.arubanetworks.com
central_client_id: your_client_id
central_client_secret: your_client_secret

# Optional: Export to static file for faster subsequent runs
output_file: ./central_devices_inventory.yml

# Optional: Customize grouping
groups:
  - site
  - device_type
  - model
```

Use the dynamic inventory in your playbooks:

```bash
ansible-inventory -i central_inventory.yml --list
ansible-playbook playbook.yml -i central_inventory.yml
```

### Features

- **Automatic Device Discovery**: Fetches all devices from Central
- **Dynamic Grouping**: Organizes devices by site, type, model, status, and device groups
- **Token Caching**: Reuses access tokens from previous runs for efficiency
- **Filtering**: Filter devices by type, status, or site
- **Credential Storage**: Stores Central credentials at inventory level for playbook access

### Example Usage

Target specific device types:
```bash
ansible-playbook configure.yml -i central_inventory.yml --limit type_switch
```

Target specific sites:
```bash
ansible-playbook deploy.yml -i central_inventory.yml --limit site_building_a
```

Access Central credentials in playbooks (automatically available from inventory):
```yaml
- name: Call Central API
  arubanetworks.hpeanw_central.central_api:
    base_url: "{{ central_base_url }}"
    access_token: "{{ central_access_token }}"
    method: GET
    path: "/monitoring/v2/devices"
```

For complete documentation, configuration options, and examples, see the [Central Inventory Plugin Guide](./docs/central_inventory_plugin.md).

## Examples
Example playbooks and inventory file can be found under [`examples/`](./examples/). Documentation for all modules can be found under [`docs/`](./docs/).

### Basic Example
It's recommended to store credentials into variabls so it's easily accessed - all examples, including below, demonstrate using variables for authentication. Alternatively, credentials such as the `client_id` and `client_secret` variables can be encrypted by using [Ansible's Vault](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi_-MOJuvePAxXcOTQIHYbUB2YQFnoECB8QAQ&url=https%3A%2F%2Fdocs.ansible.com%2Fansible%2F2.9%2Fuser_guide%2Fvault.html&usg=AOvVaw15tC1w67Azb-xcQnUh1I5B&opi=89978449) but are provided directly below for simplicity.  

```yaml
# inventory.yml
all:
  hosts:
    localhost:
      ansible_connection: local # Do not change
      central_base_url: https://us4.api.central.arubanetworks.com
      central_client_id: 111222-333444-555666777888
      central_client_secret:  888777666555444333222111
```

```yaml
# examples/central_api_demo.yml
- name: Get devices from Central
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create OAuth Token from Central
      arubanetworks.hpeanw_central.central_token:
        base_url: "{{ central_base_url }}"
        client_id: "{{ central_client_id }}"
        client_secret: "{{ central_client_secret }}"
      no_log: True
      register: token_result

    - set_fact:
        classic_access_token: "{{ token_result['access_token'] }}"
      no_log: True

    - name: Get devices from Central
      arubanetworks.hpeanw_central.central_api:
        base_url: "{{ central_base_url }}"
        access_token: "{{ classic_access_token }}"
        method: GET
        path: "/network-config/v1alpha1/devices"
      register: devices_result

    - debug:
        var: devices_result
```

Alternatively users can design their inventory so that the hosts are the devices to be managed by Central like so: