import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# --------------------------------------------------
# Docker
# --------------------------------------------------

DOCKER_PROJECT_PATH = os.getenv("DOCKER_PROJECT_PATH")

# --------------------------------------------------
# Image To Forms
# --------------------------------------------------

LOCAL_AUTH_URL = os.getenv("LOCAL_AUTH_URL")
DEV_AUTH_URL = os.getenv("DEV_AUTH_URL")

LOCAL_IMAGE_WS_URL = os.getenv("LOCAL_IMAGE_WS_URL")
DEV_IMAGE_WS_URL = os.getenv("DEV_IMAGE_WS_URL")

LOCAL_HTML_WS_URL = os.getenv("LOCAL_HTML_WS_URL")
DEV_HTML_WS_URL = os.getenv("DEV_HTML_WS_URL")

REFRESH_TOKEN_LOCAL = os.getenv("REFRESH_TOKEN_LOCAL")
REFRESH_TOKEN_DEV = os.getenv("REFRESH_TOKEN_DEV")

NEMO_PROJECT_PATH = os.getenv("NEMO_PROJECT_PATH")