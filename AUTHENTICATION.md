# Authentication Guide

This guide describes how to authenticate with each platform supported by the HPE Aruba Networking Central Ansible Collection: **Central**, **HPE GreenLake Platform (GLP)**, and **Classic Central**.

---

## Overview

Modules in this collection support two authentication approaches:

| Approach | How It Works | Best For |
| :--- | :--- | :--- |
| **Direct credentials** (recommended) | Pass `client_id`, `client_secret`, and `workspace_id` for the [HPE GreenLake Platform]((https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens#create-client-credentials)) directly to each module — the module handles token generation automatically | Most playbooks; avoids token expiry issues in longer runs |
| **Token module** | Generate a token once with a `*_token` module and pass `access_token` to tasks | Short playbooks where you want a single token exchange at play start |

Classic Central modules only accept a pre-generated `access_token` — direct credential generation is not supported for that platform.

> **Security note:** Always use `no_log: true` on any task that handles credentials or tokens. Store secrets in [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html) or environment variables rather than plain text.

---

## Unified Credentials (GLP + Central)

The preferred method of authentication is to use the unified token capabilities of HPE GreenLake Platform and Central. For simplicity in token management, users can use a single set of credentialss for both GLP and Central modules.

### Prerequisites

- **Workspace ID**: The `workspace_id` can be found in the GLP UI, [by navigating to **Manage Workspace**](https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens#using-api-credentials-for-glp).
- **Client ID and Client Secret**: Provide the `client_id` and `client_secret` scoped to the HPE GreenLake Platform to automatically generate and manage OAuth2 tokens. Use this guide for instructions on [how to create a personal API client](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client) for GLP.
- **Base URL**: Provide `base_url` which is the base URL for HPE Aruba Networking Central (e.g., https://us4.api.central.arubanetworks.com). Refer to [this guide](https://developer.arubanetworks.com/new-central/docs/making-api-calls#3-choosing-the-right-base-url) on how to find your Base URL for Central. Applicable to `central_*` modules only, omit for `glp_*` modules.

### Option 1 — Pass Credentials Directly (recommended)

Pass `client_id` and `client_secret` to each module. The module handles token generation internally on every call, so tokens never go stale regardless of how long the playbook runs.

```yaml
- name: Use unified credentials for GLP and Central
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Get GLP devices using unified credentials directly
      arubanetworks.hpeanw_central.glp_devices_info:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
        workspace_id: "{{ glp_workspace_id }}"
      register: glp_devices_result

    - name: Get Central devices using unified credentials directly
      arubanetworks.hpeanw_central.central_devices_info:
        base_url: "{{ central_base_url }}"
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
        workspace_id: "{{ glp_workspace_id }}"
      register: central_devices_result
```

### Option 2 — Generate a Token with `unified_token`

Generate a token once and pass it to tasks that need it. Because GLP tokens expire in 15 minutes, this is best suited to short playbooks. For longer runs, use direct credentials on each GLP or Central module instead.

```yaml
- name: Use unified credentials for GLP and Central
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Generate unified OAuth token
      arubanetworks.hpeanw_central.unified_token:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
        workspace_id: "{{ glp_workspace_id }}"
      register: token_result
      no_log: true

    - name: Get GLP devices using unified token
      arubanetworks.hpeanw_central.glp_devices_info:
        access_token: "{{ token_result['access_token'] }}"
      register: glp_devices_result

    - name: Get Central devices using unified token
      arubanetworks.hpeanw_central.central_devices_info:
        base_url: "{{ central_base_url }}"
        access_token: "{{ token_result['access_token'] }}"
      register: central_devices_result
```

---

## Central

### Prerequisites

- **Base URL** — The API gateway URL for your Central account (e.g., `https://us4.api.central.arubanetworks.com`). See [Finding Your Base URL](https://developer.arubanetworks.com/new-central/docs/making-api-calls#3-choosing-the-right-base-url).
- **Client ID & Client Secret** — Create credentials by following the [Access Token guide](https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens).

### Option 1 — Pass Credentials Directly (recommended)

Pass `client_id` and `client_secret` to each module. The module handles token generation internally on every call.

```yaml
- name: Manage Central resources with direct credentials
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Get devices from Central
      arubanetworks.hpeanw_central.central_api:
        base_url: "{{ central_base_url }}"
        client_id: "{{ central_client_id }}"
        client_secret: "{{ central_client_secret }}"
        method: GET
        path: "/network-monitoring/v1alpha1/devices"
      register: devices_result

    - name: Create a VLAN profile
      arubanetworks.hpeanw_central.central_profiles:
        base_url: "{{ central_base_url }}"
        client_id: "{{ central_client_id }}"
        client_secret: "{{ central_client_secret }}"
        name: 100
        path: "layer2-vlan"
        config_dict:
          vlan: 100
          name: "Corp-VLAN"
          description: "Corporate VLAN for main office"
        state: merged
```

### Option 2 — Generate a Token with `central_token`

Generate a token once at play start and pass it to subsequent tasks. Suitable for playbooks where the token will not expire before the play completes (Central tokens are valid for 2 hours).

```yaml
- name: Authenticate and manage Central resources
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Generate Central OAuth token
      arubanetworks.hpeanw_central.central_token:
        base_url: "{{ central_base_url }}"
        client_id: "{{ central_client_id }}"
        client_secret: "{{ central_client_secret }}"
      register: token_result
      no_log: true

    - name: Get devices from Central
      arubanetworks.hpeanw_central.central_api:
        base_url: "{{ central_base_url }}"
        access_token: "{{ token_result['access_token'] }}"
        method: GET
        path: "/network-monitoring/v1alpha1/devices"
      register: devices_result

    - name: Create a site in Central
      arubanetworks.hpeanw_central.central_sites:
        base_url: "{{ central_base_url }}"
        access_token: "{{ token_result['access_token'] }}"
        site_attributes:
          name: SJ_Office
          address: "123 Main St"
          city: "San Jose"
          state: "California"
          country: "United States"
          zipcode: "12345"
          timezone: "America/Los_Angeles"
        state: merged
```

---

## HPE GreenLake Platform (GLP)

### Prerequisites

- **Client ID & Client Secret** — Create a Personal API Client on HPE GreenLake by following [these steps](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#creating-a-personal-api-client). No base URL is required as GLP's endpoint is fixed.

### Option 1 — Pass Credentials Directly (recommended)

Pass `client_id` and `client_secret` to each module. The module handles token generation internally on every call.

```yaml
- name: Query GLP resources with direct credentials
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Get all devices in GLP
      arubanetworks.hpeanw_central.glp_devices_info:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
      register: devices_result

    - name: Make a custom GLP API call
      arubanetworks.hpeanw_central.glp_api:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
        method: GET
        path: "/subscriptions/v1/subscriptions"
      register: subscriptions_result
```

### Option 2 — Generate a Token with `glp_token`

Generate a token once and reuse it across tasks. Suitable only for short playbooks that complete well within GLP's 15-minute token expiry window.

```yaml
- name: Authenticate and query GLP resources
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Generate GLP OAuth token
      arubanetworks.hpeanw_central.glp_token:
        client_id: "{{ glp_client_id }}"
        client_secret: "{{ glp_client_secret }}"
      register: token_result
      no_log: true

    - name: Get all devices in GLP
      arubanetworks.hpeanw_central.glp_devices_info:
        access_token: "{{ token_result['access_token'] }}"
      register: devices_result

    - name: Make a custom GLP API call
      arubanetworks.hpeanw_central.glp_api:
        access_token: "{{ token_result['access_token'] }}"
        method: GET
        path: "/subscriptions/v1/subscriptions"
      register: subscriptions_result
```

---

## Classic Central

Classic Central modules **only accept a pre-generated access token** — the collection does not support automatic token generation for this platform.

### Prerequisites

- **Base URL** — The classic Central API gateway URL (e.g., `https://apigw-uswest5.central.arubanetworks.com`). See the [Classic Central domain URL table](https://developer.arubanetworks.com/central/docs/api-oauth-access-token#table-domain-urls-for-api-gateway-access).
- **Access Token** — Manually generate a token from your Classic Central account and provide it via the `access_token` parameter. Tokens expire and must be refreshed manually.

```yaml
- name: Query Classic Central
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Get sites from Classic Central
      arubanetworks.hpeanw_central.classic_api:
        base_url: "{{ classic_base_url }}"
        access_token: "{{ classic_access_token }}"
        method: GET
        path: "/central/v2/sites"
      register: sites_result
```

---

## MSP Token

For Managed Service Provider (MSP) workflows, use the `msp_token` module to generate workspace-level or tenant-scoped tokens.

### Prerequisites

- **GLP Client ID & Client Secret** — [MSP credentials](https://developer.arubanetworks.com/new-central/docs/msp-token-exchange#one-time-setup).
- **MSP Workspace ID** — The GreenLake Platform workspace ID for the MSP workspace.
- **Tenant ID or Tenant Name** _(optional)_ — Provide either to scope the token to a specific tenant.

```yaml
- name: Generate MSP tokens
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Generate MSP workspace-level token
      arubanetworks.hpeanw_central.msp_token:
        client_id: "{{ msp_client_id }}"
        client_secret: "{{ msp_client_secret }}"
        msp_workspace_id: "{{ msp_workspace_id }}"
      register: msp_token_result
      no_log: true

    - name: Store MSP token
      set_fact:
        msp_access_token: "{{ msp_token_result['msp_access_token'] }}"
      no_log: true

    - name: Generate tenant-scoped token by tenant name
      arubanetworks.hpeanw_central.msp_token:
        client_id: "{{ msp_client_id }}"
        client_secret: "{{ msp_client_secret }}"
        msp_workspace_id: "{{ msp_workspace_id }}"
        tenant_name: MyTenant
      register: tenant_token_result
      no_log: true

    - name: Store tenant token
      set_fact:
        tenant_access_token: "{{ tenant_token_result['tenant_access_token'] }}"
      no_log: true
```

The `msp_token` module returns:
- `msp_access_token` — workspace-level token (always returned)
- `tenant_access_token` — tenant-scoped token (returned when `tenant_id` or `tenant_name` is provided)

---

## Choosing the Right Approach

| Scenario | Recommended Approach |
| :--- | :--- |
| Any playbook against Central | Pass GLP `client_id` + `client_secret` + `workspace_id` directly to each module |
| Any playbook against GLP | Pass GLP `client_id` + `client_secret` + `workspace_id` directly to each module |
| Long playbook — Central only | `central_token` module + `access_token` |
| Short playbook — GLP only | `glp_token` module + `access_token` |
| Short playbook — GLP + Central | `unified_token` module + `access_token` |
| Classic Central | Pre-generated `access_token` (required) |
| MSP workflows | `msp_token` module |

## Token Module Reference

| Module | Platform | Returns |
| :--- | :--- | :--- |
| [`central_token`](./docs/central_token.md) | Central | `access_token` |
| [`glp_token`](./docs/glp_token.md) | GLP | `access_token` |
| [`unified_token`](./docs/unified_token.md) | GLP + Central | `access_token` |
| [`msp_token`](./docs/msp_token.md) | GLP MSP | `msp_access_token`, `tenant_access_token` |
