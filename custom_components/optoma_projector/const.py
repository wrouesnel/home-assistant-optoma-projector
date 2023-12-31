import logging

DOMAIN = "optoma_projector"
LOGGER = logging.getLogger(__package__)

CONFIG_URL = "url"
CONFIG_USERNAME = "username"
CONFIG_PASSWORD = "password"

MANUFACTURER_NAME = "Creston"

INFO_MODEL_NAME = "Model Name"
INFO_MAC_ADDRESS = "MAC Address"
INFO_FIRWMARE_VERSION = "Firmware Version"
INFO_PROJECTOR_NAME = "Projector Name"

DEFAULT_POLL_INTERVAL: int = 1

LOCAL_LOGO_PATH = "local_logo_path"
CUSTOM_IMAGE_BASE_URL = f"/api/{DOMAIN}/custom"
STATIC_IMAGE_BASE_URL = f"/api/{DOMAIN}/static"
