# (C) Copyright 2025 HPE Aruba Networking
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from pycentral import NewCentralBase
    from pycentral.classic.base import ArubaCentralBase

    HAS_PYCENTRAL = True
except ImportError:
    HAS_PYCENTRAL = False


class CentralClient:
    def __init__(
        self, base_url, client_id, client_secret, access_token=None, **_
    ):
        if not HAS_PYCENTRAL:
            raise ImportError("The python pycentral package is required")
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.central = None
        self._connect()

    def _connect(self):
        self._validate_params()
        # Setup the token_info dictionary based on the provided parameters
        token_info = {
            "new_central": {
                "base_url": self.base_url,
            }
        }

        # Use client credentials to get a token
        if self.client_id and self.client_secret:
            token_info["new_central"]["client_id"] = self.client_id
            token_info["new_central"]["client_secret"] = self.client_secret
            token_info["new_central"]["access_token"] = None
        # If OAuth token is provided, use it directly
        if self.access_token:
            # self.logger.info("Using provided OAuth token")
            token_info["new_central"]["access_token"] = self.access_token
        try:
            self.central = NewCentralBase(
                token_info=token_info,
                log_level="INFO",
            )

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Central: {e}")

    def _validate_params(self):
        if not self.base_url:
            raise ValueError(
                "base_url is required ex) https://us4.api.central.arubanetworks.com"
            )
        if not self.access_token:
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    "Either 'access_token' or both 'client_id' and 'client_secret' are required"
                )

    def get_central_conn(self):
        return self.central


class GLPClient:
    def __init__(self, client_id, client_secret, access_token=None, **_):
        if not HAS_PYCENTRAL:
            raise ImportError("The python pycentral package is required")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.glp = None
        self._connect()

    def _connect(self):
        self._validate_params()
        # Setup the token_info dictionary based on the provided parameters
        token_info = {"glp": {}}

        # Use client credentials to get a token
        if self.client_id and self.client_secret:
            token_info["glp"]["client_id"] = self.client_id
            token_info["glp"]["client_secret"] = self.client_secret
            token_info["glp"]["access_token"] = None
        # If OAuth token is provided, use it directly
        if self.access_token:
            # self.logger.info("Using provided OAuth token")
            token_info["glp"]["access_token"] = self.access_token
        try:
            self.glp = NewCentralBase(
                token_info=token_info,
                log_level="INFO",
            )

        except Exception as e:
            raise ConnectionError(f"Failed to connect to GLP: {e}")

    def _validate_params(self):
        if not self.access_token:
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    "Either 'access_token' or both 'client_id' and 'client_secret' are required"
                )

    def get_glp(self):
        return self.glp


class ClassicClient:
    # Classic Central client does not handle refresh token
    def __init__(self, base_url, access_token, **_):
        if not HAS_PYCENTRAL:
            raise ImportError("The python pycentral package is required")
        self.base_url = base_url
        self.access_token = access_token
        self.classic_conn = None
        self._connect()

    def _connect(self):
        self._validate_params()
        # Setup the token_info dictionary based on the provided parameters
        token_info = dict()
        token_info["token"] = dict()

        token_info["base_url"] = self.base_url
        token_info["token"]["access_token"] = self.access_token

        try:
            self.classic_conn = ArubaCentralBase(central_info=token_info)

        except Exception as e:
            raise ConnectionError(f"Failed to connect to classic Central: {e}")

    def _validate_params(self):
        if not self.base_url:
            raise ValueError(
                "base_url is required ex) https://apigw-uswest5.central.arubanetworks.com"
            )
        if not self.access_token:
            raise ValueError("'access_token' is required")

    def get_classic_conn(self):
        return self.classic_conn
