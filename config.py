from os import environ as env

from dotenv import load_dotenv

load_dotenv()

UNIFI_HOST = env.get("UNIFI_HOST", "localhost")
UNIFI_PORT = env.get("UNIFI_PORT", 443)
UNIFI_USER = env.get("UNIFI_USER", "admin")
UNIFI_PASS = env.get("UNIFI_PASS")
UNIFI_SITE = env.get("UNIFI_SITE", "default")
UNIFI_URL = f"https://{UNIFI_HOST}:{UNIFI_PORT}"

BROTHER_QL_MODEL = env.get("BROTHER_QL_MODEL")
BROTHER_QL_PRINTER = env.get("BROTHER_QL_PRINTER")
