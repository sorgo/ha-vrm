import logging
from typing import Any, Dict, Optional

import requests
import json
from datetime import datetime
import async_timeout
import asyncio
import aiohttp
import sys

from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_SITES, DOMAIN, PATH_LOGIN, REQUEST_TIMEOUT, BASE_API_URL

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string, vol.Optional(CONF_URL): cv.string}
)
REPO_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PATH): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional("add_another"): cv.boolean,
    }
)

VERSION = 0
MINOR_VERSION = 1

def validate_path(path: str) -> None:
    """Validates a VRM installation
    Raises a ValueError if the path is invalid.
    """
    if len(path.split("/")) != 2:
        raise ValueError


async def validate_cred(user_name: str, password: str, hass: core.HomeAssistant) -> str:
    """Validates a VRM access token.
    Raises a ValueError if the auth token is invalid.
    """

    try:
        websession = async_get_clientsession(hass)
        with async_timeout.timeout(REQUEST_TIMEOUT):
            cred_data = {
                "username": user_name,
                "password": password
            }


            resp = await websession.request(
                "POST", BASE_API_URL + PATH_LOGIN, data=json.dumps(cred_data, ensure_ascii = False)
            )
#            resp = await websession.post(BASE_API_URL + PATH_LOGIN, data=json.dumps(cred_data, ensure_ascii = False))
            #resp = await websession.post(BASE_API_URL + PATH_LOGIN, data=cred_data)
            # resp = await websession.get(PATH_LOGIN.format(stopId=self._stopid, minutesAfter=self._minsafter))
            #return resp.json()
        if resp.status != 200:
            _LOGGER.error(f"{resp.url} returned {resp.status}")
            return

        json_response = await resp.json()
#        _LOGGER.debug("async_update: %s", resp.text.encode("utf-8"))
#        #
#        _LOGGER.debug(json_response)
        return json_response["token"]

    except (asyncio.TimeoutError) as err:
        _LOGGER.error("[" + sys._getframe().f_code.co_name + "] TimeoutError %s", err)
    except (aiohttp.ClientError) as err:
        _LOGGER.error("[" + sys._getframe().f_code.co_name + "] aiohttp.ClientError %s", err)
    except ValueError:
        _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received non-JSON data from API endpoint")
    except vol.Invalid as err:
        _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Received unexpected JSON from " " API endpoint: %s", err)
    except Exception as e:
        _LOGGER.error("[" + sys._getframe().f_code.co_name + "] Exception: " + str(e))
    #raise myRequestError
    raise ValueError
#    try:
#        await gh.getitem("repos/home-assistant/core")
#    except BadRequest:
#        raise ValueError


class VRMHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """VRM HA Custom config flow."""

    data: Optional[Dict[str, Any]]
    sites: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        self.data = {}
        if user_input is not None:
            try:
                self.data[CONF_ACCESS_TOKEN] = await validate_cred(user_input[CONF_USERNAME], user_input[CONF_PASSWORD], self.hass)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data[CONF_USERNAME] = user_input[CONF_USERNAME]
                self.data[CONF_PASSWORD] = user_input[CONF_PASSWORD]
                self.data[CONF_SITES] = []
                # Return the form of the next step.
                return await self.async_step_sites()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_sites(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Validate the path.
            try:
                validate_path(user_input[CONF_PATH])
            except ValueError:
                errors["base"] = "invalid_path"

            if not errors:
                # Input is valid, set data.
                self.data[CONF_SITES].append(
                    {
                        "path": user_input[CONF_PATH],
                        "name": user_input.get(CONF_NAME, user_input[CONF_PATH]),
                    }
                )
                # If user ticked the box show this form again so they can add an
                # additional repo.
                if user_input.get("add_another", False):
                    return await self.async_step_site()

                # User is done adding repos, create the config entry.
                return self.async_create_entry(title="vrm-ha", data=self.data)
        DISCOVERED_SCHEMA = {}
        DISCOVERED_SCHEMA[vol.Required("aaa")] = cv.boolean
        DISCOVERED_SCHEMA[vol.Required("bbb")] = cv.boolean
        DISCOVERED_SCHEMA[vol.Optional("add_another")] = cv.boolean
        DISCOVERED = vol.Schema(DISCOVERED_SCHEMA)


        return self.async_show_form(
            step_id="sites", data_schema=DISCOVERED, errors=errors
        )