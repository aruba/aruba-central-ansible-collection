# module: central_sites_info

description: This module allows you to retrieve Site(s) in HPE Aruba Networking Central. Provides various subsets to fetch different types of site information.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```

##### RETURNED
```YAML
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
```