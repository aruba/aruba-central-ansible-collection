# Release Notes

## Version 2.2.0-beta

### Overview
Version 2.2.0-beta introduces unified credentials support across all Central and GLP modules, a new `unified_token` module, and several consistency and clarity improvements.

### New Features

#### New Modules
- **`unified_token`** - Module for generating OAuth tokens using unified credentials, enabling a single authentication flow across Central and GLP APIs

#### Module Enhancements
- **`central_api`, `glp_api`, and all Central/GLP modules`** - Added `workspace_id`, `tenant_name`, and `tenant_id` parameters to support unified or MSP authentication; refactored connection handling to use a common method for improved consistency
- **`msp_token`** - Renamed `workspace_id` to `msp_workspace_id` for clarity and consistency
- **`central_profiles`** - Updated local profile options to use `scope-id` and `device-function` parameter names for clarity

### Bug Fixes & Improvements
- Added `base_url` parameter to `UnifiedClient` and `MSPClient` for improved token validity
- Updated required Ansible version in `runtime.yml`

### Documentation & Examples
- Added `AUTHENTICATION.md` guide covering unified credentials usage and configuration
- Refactored all example playbooks to use unified token authentication instead of platform-specific tokens
- Added `workspace_id` parameter to GLP API examples
- Updated `README` to reflect unified credentials usage and inventory configuration changes
- Enhanced documentation across all Central and GLP modules to clarify `client_id`, `client_secret`, and `workspace_id` usage with unified credentials

---


## Version 2.1.1-beta

### Overview
Version 2.1.1-beta fixes a bug regarding GreenLake Platform connection.

### Bug Fixes & Improvements
- Fixed default access_token assignment in GLPClient

---


## Version 2.1.0-beta

### Overview
Version 2.1.0 introduces new modules for enhanced GreenLake Platform capabilities, significant improvements to device and inventory management, and better troubleshooting support.

### New Features

#### New Modules
- **`glp_subscriptions_info`** - Module for retrieving subscription information from the HPE GreenLake Platform API
- **`central_troubleshooting`** - Module for executing troubleshooting commands on devices via Central API
- **`msp_token`** - Module for MSP (Managed Service Provider) and Tenant token generation for multi-tenan support

#### Module Enhancements
- **`central_inventory`** - Added site and group fetching methods to improve inventory management and device organization capabilities
- **`central_devices_info`** - Enhanced device filtering to support separate inventory and monitoring filters with flexible result merging. Now supports multiple device retrieval filter options
- **`central_sites`** - Enhanced documentation and location validation with ISO format checks for city, state, and country attributes
- **`msp_token`** - Updated to enforce proper credential requirements for tenant-scoped token generation

### Bug Fixes & Improvements
- Fixed message formatting for device assignment in `classic_groups` module
- Fixed issue when no sites exist in workspace
- Fixed formatting inconsistencies in documentation for `central_devices_info`, `central_troubleshooting`, and `glp_subscriptions_info` modules
- Updated README and requirements documentation for improved versioning and access token handling
- Enhanced error handling for device filtering operations
- Updated pycentral version compatibility in requirements


---


---

## Version 2.0.0-beta

### Release Date
April 2026

### Overview
Version 2.0.0 is a major release representing a complete rewrite of the Aruba Central Ansible collection with significant modernization efforts. This version introduces support for HPE GreenLake Platform API alongside the existing Central API and introduces a new modular architecture built on the pycentral v2 SDK.

### New Features

#### New Modules
- **`central_api`** - Generic module for executing arbitrary Central API calls
- **`central_device_groups_info`** - Module for retrieving device group information
- **`central_devices_info`** - Module for retrieving device inventory information with filtering capabilities
- **`central_profiles`** - Module for managing device configuration profiles
- **`central_sites_info`** - Module for retrieving site information
- **`central_sites`** - Module for managing sites (create, update, delete operations)
- **`central_token`** - Module for generating and managing Central API access tokens
- **`central_inventory` (plugin)** - Dynamic inventory plugin for Aruba Central for automated device discovery
- **`glp_api`** - Generic module for executing arbitrary GreenLake Platform API calls
- **`glp_devices_info`** - Module for retrieving device inventory from GreenLake Platform
- **`glp_devices`** - Module for managing devices in GreenLake Platform
- **`glp_inventory`** - Module for managing device inventory entries in GreenLake Platform
- **`glp_token`** - Module for generating GreenLake Platform access tokens
- **`classic_api`** - Module for executing Classic Aruba Central API calls (legacy support)
- **`classic_groups`** - Module for managing device groups in Classic Aruba Central (legacy support)
- **`classic_sites`** - Module for managing sites in Classic Aruba Central (legacy support)

### Major Changes

#### Architecture & Infrastructure
- Complete migration to **pycentral v2 SDK** for improved API compatibility and performance
- Updated **Ansible version requirement to 2.19.6** for better module support and features
- Introduced support for **check mode** across all modules for idempotent playbook validation
- Refactored token handling with **`central_access_token`** parameter (renamed from `oauth_token`) for consistency across all modules
- Added **requirements.txt** to specify pycentral dependency for easy installation

#### Plugin & Inventory Management
- **Token-only mode support** in central_inventory plugin for secure credential handling
- Dynamic inventory discovery for automated Central API device inventory management
- Support for GreenLake Platform device inventory management alongside Central API

#### Module-Specific Features
- **glp_inventory**: Support for device inventory management in HPE GreenLake Platform
- **central_inventory**: Enhanced with site and group lookup capabilities
- **glp_token**: Direct definition of `client_id` and `client_secret` in module_args for streamlined token generation
- **central_sites**: Comprehensive site lifecycle management including create/update/delete operations

### Compatibility
- Requires Python 3.7 or later
- Requires Ansible 2.19.6 or later
- Requires pycentral v2 SDK (specified in requirements.txt)
- Compatible with HPE Aruba Networking Central API and HPE GreenLake Platform API
