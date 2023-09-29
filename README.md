Aruba Central Ansible Collection
=========

This Ansible Network collection provides a set of platform dependent configuration management modules and plugins specifically designed for Aruba Central, which is a cloud-based Network Management System.

## [](https://github.com/aruba/aruba-central-ansible-collection#requirements)Requirements

* Python 3.5+
* Ansible 2.9 or later
  * Refer to [Ansible's documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for  installation steps
  * Ansible 2.10+ requires `ansible.netcommon` collection to be installed
* Minimum supported Aruba Central firmware is 2.5.2

* Install all Ansible requirements, with the following command:
    ```
    ansible-galaxy install -r requirements.yml
    ```
* Install all Python requirements with the following command:
    ```
    pip install -r requirements.txt
    ```
## [](https://github.com/aruba/aruba-central-ansible-collection#installation)Installation

Through Galaxy:

```
ansible-galaxy collection install arubanetworks.aruba_central  
```

## [](https://github.com/aruba/aruba-central-ansible-collection#notes)Notes

- The plugins in this collection use Aruba Central's REST API. For information on REST API and how to obtain an access for using REST API, visit the Aruba Developer Hub: [Getting Started with REST API](https://developer.arubanetworks.com/aruba-central/docs/api-getting-started)
- An API token must be created for a user on Aruba Central's API Gateway and a valid, non-expired **`access_token`** must be used. For more information on how to get started with the API Gateway you can also watch this [YouTube Video](https://www.youtube.com/watch?v=tWEsL7zSOB0).
- A valid access token can be used in an Inventory file as mentioned in the [Inventory](https://github.com/aruba/aruba-central-ansible-collection#inventory) section.
- Ensure that the access token was created with "Network Operations" selected in the Application drop-down list, while adding a new token on the API Gateway. 
- Once a new token is generated, it will have an `access_token` and a `refresh_token`.
- An access token is valid for a period of 7200 seconds or two hours. After two hours, it will expire and a new token needs to be created. The token expiry time is currently not configurable.
- Aruba Central also provides a token refresh mechanicsm for renewing an expired access token. You can use the [Refresh Token API](https://developer.arubanetworks.com/aruba-central/reference/xxxxxx) to do this and use a valid access token in your inventory/host file.


## Inventory/Host File 
### [](https://github.com/aruba/aruba-cnetral-ansible-collection#inventory-variables)Inventory Variables

The variables that should be defined in your inventory for your Aruba Central account are:

- `ansible_host`: Cluster-specific Base-URL for the API Gateway on Aruba Central in FQDN format, which can be found in the API Documentation URL on API Gateway
- `ansible_connection`: Must always be set to  `httpapi`
- `ansible_network_os`: Must always be set to  `arubanetworks.aruba_central.aruba_central`
- `ansible_httpapi_use_ssl`: Must always be set to  `True`
- `ansible_httpapi_central_access_token`: Aruba Central's API access token

#### [](https://github.com/aruba/aruba-central-ansible-collection#sample-inventory)Sample Inventory:

##### YAML

```YAML
all:
  hosts:
    central:
      ansible_host: apigw-prod2.central.arubanetworks.com
      ansible_connection: httpapi
      ansible_network_os: arubanetworks.aruba_central.aruba_central
      ansible_httpapi_use_ssl: True
      ansible_httpapi_central_access_token: CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```

##### INI

```INI
arubacentral ansible_host=apigw-prod2.central.arubanetworks.com  ansible_connection=httpapi ansible_network_os=arubanetworks.aruba_central.aruba_central ansible_httpapi_use_ssl=True  ansible_httpapi_central_access_token=CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```


## [](https://github.com/aruba/aruba-central-ansible-collection#example-playbook)Example Playbooks

### Including Central collection

Set collections to `arubanetworks.aruba_central` within the playbook:

    ---
    -  hosts: all
       collections:
         - arubanetworks.aruba_central
       tasks:
       - name: Get all the UI and Template Groups on Central
         central_groups:
           action: get_groups
           limit: 20
           offset: 0
  
## [](https://github.com/aruba/aruba-central-ansible-collection#playbook-execution) Playbook Execution

```
ansible-playbook playbook.yml -i inventory.yml
```

Contribution
-------

At Aruba Networks we're dedicated to ensuring the quality of our products, so if you find any
issues at all please open an issue on our [Github](https://github.com/aruba/aruba-central-ansible-collection) and we'll be sure to respond promptly!

For more contribution opportunities follow our guidelines outlined in our [CONTRIBUTING.md](https://github.com/aruba/aruba-central-ansible-collection/blob/master/CONTRIBUTING.md)

License
-------

MIT

Author Information
------------------

- Jay Pathak (@jayp193)
- Ti Chiapuzio-Wong (@tchiapuziowong)
