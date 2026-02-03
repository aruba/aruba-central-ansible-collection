# module: central_sites

description: This module allows you to create and manage Sites in HPE Aruba Networking Central.

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
        - The city where the Site is located
      type: str
      required: true
    state:
      description:
        - The state or province where the Site is located
      type: str
      required: true
    country:
      description:
        - The country where the Site is located
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
```

##### EXAMPLES

```YAML
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
```

##### RETURNED
```YAML
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
```