# module: glp_subscriptions_info

description: This module allows you to retrieve information about subscriptions managed in HPE GreenLake Platform. Provides various subsets to fetch different types of subscription information.

##### ARGUMENTS

```YAML
client_id:
  description: >
    The client ID for the GLP account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, workspace_id must be provided.
  type: str
  required: false
client_secret:
  description: >
    The client secret for the GLP account, used to create OAuth token, required if access_token is not provided.
    If using unified credentials, workspace_id must be provided.
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
subset:
  description: >
    Retrieve a subset of subscriptions and their information
  type: str
  required: false
  choices:
    - all_subscriptions
    - subscription_by_filter
  default: all_subscriptions
subscription_filter:
  description: >
    Filter expression for retrieving specific subscriptions when using subscription_by_filter subset.
    Filter expressions consist of simple comparison operations joined by logical operators.
  type: str
  required: false
select:
  description: >
    A comma separated list of properties to display in the response
  type: str
  required: false
```

##### EXAMPLES

```YAML
- name: Get all subscriptions in GLP
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
  register: subscriptions_result

- name: Get subscriptions with specific fields
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    access_token: AABBCC-111222-333444-555666777888
    subset: all_subscriptions
    select: "id,key"
  register: subscriptions_result

- name: Get Subscriptions by Filter
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    subset: subscription_by_filter
    subscription_filter: "subscriptionType eq 'CENTRAL_GW'"
  register: subscriptions_result

- name: Get all subscriptions using unified credentials
  arubanetworks.hpeanw_central.glp_subscriptions_info:
    client_id: 111222-333444-555666777888
    client_secret: 888777666555444333222111
    workspace_id: 1234567890
  register: subscriptions_result
```

##### RETURNED
```YAML
subscriptions:
  description: List of dictionaries containing details of subscriptions in GLP
  returned: always
  type: dict
  contains:
    subscriptions:
      description: Subscription information based on requested subset
      type: list
      elements: dict
      returned: on success
    count:
      description: Number of subscriptions returned
      type: int
      returned: on success with subscription_by_filter subset
    msg:
      description: Detailed message or error information
      type: str
      returned: always
```