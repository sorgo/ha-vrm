import logging
from typing import Any, Dict, Optional

import requests
import json
from datetime import datetime

from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_SITES, DOMAIN

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


async def validate_auth(access_token: str, hass: core.HomeAssistant) -> None:
    """Validates a VRM access token.
    Raises a ValueError if the auth token is invalid.
    """
    session = async_get_clientsession(hass)
    gh = GitHubAPI(session, "requester", oauth_token=access_token)
    try:
        await gh.getitem("repos/home-assistant/core")
    except BadRequest:
        raise ValueError


class VRMHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """VRM HA Custom config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_auth(user_input[CONF_ACCESS_TOKEN], self.hass)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                self.data[CONF_SITES] = []
                # Return the form of the next step.
                return await self.async_step_site()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_site(self, user_input: Optional[Dict[str, Any]] = None):
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
                return self.async_create_entry(title="GitHub Custom", data=self.data)

        return self.async_show_form(
            step_id="repo", data_schema=REPO_SCHEMA, errors=errors
        )