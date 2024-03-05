import os
import sys
import urllib.parse

SERVER_MODE = True
AUTO_DISCOVER_SERVERS = False

def build_postgresql_uri():
    
    env_vars = {
        "PGADMIN_DB_URL_USERNAME": True,  # required
        "PGADMIN_DB_URL_HOST": True,      # required
        "PGADMIN_DB_URL_DATABASE": True,  # required
        "PGADMIN_DB_URL_PORT": False      # not required
    }    
    
    missing_vars = [var for var, required in env_vars.items() if required and os.getenv(var) is None]
    vars_set = [var for var in env_vars if os.getenv(var) is not None]    
    
    if not vars_set:
        # all variables are missing; proceed with an empty URI
        return ""
    elif missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
        sys.exit(1)
        
    username = os.getenv('PGADMIN_DB_URL_USERNAME')
    host = os.getenv('PGADMIN_DB_URL_HOST')
    port = os.getenv('PGADMIN_DB_URL_PORT', '5432')
    dbname = os.getenv('PGADMIN_DB_URL_DATABASE')

    return f"postgresql://{username}@{host}:{port}/{dbname}"

CONFIG_DATABASE_URI = build_postgresql_uri()

AUTHENTICATION_SOURCES = ['oauth2']
# Enable internal auth if PGADMIN_ENABLE_INTERNAL_AUTH is set
if os.getenv('PGADMIN_ENABLE_INTERNAL_AUTH', '').lower() in ['true', '1', 'on', 'yes', 'y', 'enabled']:
    AUTHENTICATION_SOURCES.append('internal')
    
MFA_ENABLED = False
OAUTH2_AUTO_CREATE_USER = True
MASTER_PASSWORD_REQUIRED = False
MAX_LOGIN_ATTEMPTS = 3

USER_INACTIVITY_TIMEOUT = 900
OVERRIDE_USER_INACTIVITY_TIMEOUT = True

OAUTH2_CONFIG = [{
    
    'OAUTH2_NAME': 'Keycloak',
    'OAUTH2_DISPLAY_NAME': 'Keycloak',
    'OAUTH2_CLIENT_ID': 'pgadmin',
    
    'OAUTH2_TOKEN_URL': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/token',
    'OAUTH2_AUTHORIZATION_URL': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/auth',
    'OAUTH2_SERVER_METADATA_URL': 'http://host.docker.internal:8080/realms/avalanchecms/.well-known/openid-configuration',
    'OAUTH2_USERINFO_ENDPOINT': 'http://host.docker.internal:8080/realms/avalanchecms/protocol/openid-connect/userinfo',
    'OAUTH2_API_BASE_URL': 'http://host.docker.internal:8080/realms/avalanchecms',
    
    'OAUTH2_SCOPE': 'openid email profile',
    'OAUTH2_AUTO_CREATE_USER': False,
    'OAUTH2_SSL_CERT_VERIFICATION': False,
    
    'OAUTH2_ADDITIONAL_CLAIMS': { # Checked for mapping in the ID token
        'roles': [ "admin" ]
    }    
}]

# Add OAUTH2_CLIENT_SECRET only if PGADMIN_OAUTH2_CLIENT_SECRET is set
if 'PGADMIN_OAUTH2_CLIENT_SECRET' in os.environ:
    OAUTH2_CONFIG[0]['OAUTH2_CLIENT_SECRET'] = urllib.parse.quote(os.environ['PGADMIN_OAUTH2_CLIENT_SECRET'].strip())

#import logging
#FILE_LOG_LEVEL = logging.DEBUG
#CONSOLE_LOG_LEVEL = logging.DEBUG
#DEBUG = True
