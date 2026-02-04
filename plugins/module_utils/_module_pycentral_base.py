# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.arubanetworks.hpeanw_central.plugins.module_utils.clients.pycentral_clients import (  # NOQA
    CentralClient,
    GLPClient,
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


class ModuleClassicConnection(ClassicClient):
    def __init__(self, module):
        super().__init__(**module.params)
        self.module = module
        self.params = module.params


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
