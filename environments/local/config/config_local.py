import os

SERVER_MODE = True
MASTER_PASSWORD_REQUIRED = True
DEBUG = True
AUTHENTICATION_SOURCES = ['oauth2', 'internal']
OAUTH2_AUTO_CREATE_USER = True
OAUTH2_CONFIG = [{
    'OAUTH2_NAME': 'keycloak',
    'OAUTH2_DISPLAY_NAME': 'keycloak',
    'OAUTH2_CLIENT_ID': 'pgadmin',
    'OAUTH2_TOKEN_URL': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/token',
    'OAUTH2_AUTHORIZATION_URL': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/auth',
    'OAUTH2_SCOPE': 'openid email profile',
    'OAUTH2_SERVER_METADATA_URL': 'http://host.docker.internal:8080/realms/avalanchecms/.well-known/openid-configuration',
    'OAUTH2_AUTO_CREATE_USER': False,
    'OAUTH2_SSL_CERT_VERIFICATION': False,
    'OAUTH2_USERINFO_ENDPOINT': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/userinfo',
    'OAUTH2_API_BASE_URL': 'http://host.docker.internal:8080/realms/avalanchecms'
}]

# Add OAUTH2_CLIENT_SECRET only if PGADMIN_OAUTH2_CLIENT_SECRET is set
if 'PGADMIN_OAUTH2_CLIENT_SECRET' in os.environ:
    OAUTH2_CONFIG[0]['OAUTH2_CLIENT_SECRET'] = os.environ['PGADMIN_OAUTH2_CLIENT_SECRET'].strip()

import logging
FILE_LOG_LEVEL = logging.DEBUG
CONSOLE_LOG_LEVEL = logging.DEBUG
