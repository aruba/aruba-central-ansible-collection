# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils.clients.pycentral_clients import (  # NOQA
    CentralClient,
    GLPClient,
    UnifiedClient,
    MSPClient,
    ClassicClient,
)


class ModuleCentralConnection(CentralClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


class ModuleGLPConnection(GLPClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


class ModuleUnifiedConnection(UnifiedClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


class ModuleMSPConnection(MSPClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


class ModuleClassicConnection(ClassicClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


def get_central_connection(module):
    """
    Establish a Central connection based on module parameters.

    Connection precedence:
      1) workspace_id + tenant_id/tenant_name => MSP tenant-scoped connection
      2) workspace_id alone                   => Unified (GLP) connection
      3) fallback                             => Standard Central connection

    Returns the connection object. Calls module.fail_json on any failure so
    callers do not need to handle connection errors themselves.
    """
    workspace_id = module.params.get("workspace_id")
    tenant_id = module.params.get("tenant_id")
    tenant_name = module.params.get("tenant_name")

    try:
        if workspace_id and (tenant_id or tenant_name):
            # MSP client expects msp_workspace_id parameter name.
            module.params["msp_workspace_id"] = workspace_id
            msp_obj = ModuleMSPConnection(module)
            central_conn = msp_obj.get_tenant_conn()
            if central_conn is None:
                module.fail_json(
                    msg=(
                        "Failed to establish tenant-scoped MSP connection; "
                        "verify tenant_id/tenant_name and workspace_id"
                    )
                )
        elif workspace_id:
            unified_obj = ModuleUnifiedConnection(module)
            central_conn = unified_obj.get_unified_conn()
        else:
            central_obj = ModuleCentralConnection(module)
            central_conn = central_obj.get_central_conn()

        if central_conn is None:
            module.fail_json(
                msg=(
                    "Failed to establish connection to HPE Aruba Networking Central. "
                    "Please check your credentials and base_url."
                )
            )
    except Exception as e:
        module.fail_json(
            msg=f"Failed to establish connection to HPE Aruba Networking Central: {str(e)}",
            exception=str(e),
        )

    return central_conn


def get_glp_connection(module):
    """
    Establish a GLP connection based on module parameters.

    Connection precedence:
      1) workspace_id + tenant_id/tenant_name => MSP tenant-scoped connection
      2) workspace_id alone                   => Unified (GLP) connection
      3) fallback                             => Standard GLP connection

    Returns the connection object. Calls module.fail_json on any failure so
    callers do not need to handle connection errors themselves.
    """
    workspace_id = module.params.get("workspace_id")
    tenant_id = module.params.get("tenant_id")
    tenant_name = module.params.get("tenant_name")

    try:
        if workspace_id and (tenant_id or tenant_name):
            # MSP client expects msp_workspace_id parameter name.
            module.params["msp_workspace_id"] = workspace_id
            msp_obj = ModuleMSPConnection(module)
            glp_conn = msp_obj.get_tenant_conn()
            if glp_conn is None:
                module.fail_json(
                    msg=(
                        "Failed to establish tenant-scoped MSP connection; "
                        "verify tenant_id/tenant_name and workspace_id"
                    )
                )
        elif workspace_id:
            unified_obj = ModuleUnifiedConnection(module)
            glp_conn = unified_obj.get_unified_conn()
        else:
            glp_obj = ModuleGLPConnection(module)
            glp_conn = glp_obj.get_glp()

        if glp_conn is None:
            module.fail_json(
                msg="Failed to establish connection to HPE GreenLake Platform"
            )
    except Exception as e:
        module.fail_json(
            msg="Failed to establish connection to HPE GreenLake Platform",
            exception=str(e),
        )

    return glp_conn


def central_base_argument_spec():
    """
    This returns a dictionary that can be used as the baseline for all Central module specs
    """
    return dict(
        base_url=dict(
            type="str",
            required=True,
        ),
        client_id=dict(
            type="str",
            required=False,
        ),
        client_secret=dict(
            type="str",
            required=False,
            no_log=True,
        ),
        access_token=dict(
            type="str",
            default=None,
            no_log=True,
        ),
    )


def glp_base_argument_spec():
    """
    This returns a dictionary that can be used as the baseline for all GLP module specs
    """
    return dict(
        client_id=dict(
            type="str",
            required=False,
        ),
        client_secret=dict(
            type="str",
            required=False,
            no_log=True,
        ),
        access_token=dict(
            type="str",
            default=None,
            no_log=True,
        ),
    )


def msp_base_argument_spec():
    """
    This returns a dictionary that can be used as the baseline to enable MSP functionality in modules
    """
    return dict(
        client_id=dict(
            type="str",
            required=True,
        ),
        client_secret=dict(
            type="str",
            required=True,
            no_log=True,
        ),
        msp_workspace_id=dict(
            type="str",
            required=True,
        ),
        tenant_id=dict(
            type="str",
            required=False,
        ),
        tenant_name=dict(
            type="str",
            required=False,
        ),
    )


def unified_base_argument_spec():
    """
    This returns a dictionary that can be used as the baseline for unified GLP credentials modules
    """
    return dict(
        client_id=dict(
            type="str",
            required=True,
        ),
        client_secret=dict(
            type="str",
            required=True,
            no_log=True,
        ),
        workspace_id=dict(
            type="str",
            required=True,
        ),
    )


def classic_base_argument_spec():
    """
    This returns a dictionary that can be used as the baseline for all Classic Central module specs
    """
    return dict(
        base_url=dict(
            type="str",
            required=True,
        ),
        access_token=dict(
            type="str",
            required=True,
            no_log=True,
        ),
    )
