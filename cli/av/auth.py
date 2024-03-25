import base64
import hashlib
import http.server
import json
import queue
import secrets
import socketserver
import threading
import time
import webbrowser
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
import click
import requests

@click.group()
def auth_commands():
    """Authentication commands."""
    pass

def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=')

def generate_code_verifier():
    token = secrets.token_urlsafe(32)
    return token.encode('utf-8')

def generate_code_challenge(verifier):
    sha256 = hashlib.sha256(verifier).digest()
    return base64_url_encode(sha256)

def decode_jwt_payload(token):
    # Split the token into its parts
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid JWT token")

    # Base64 decode the payload part
    payload = parts[1]
    # Add necessary padding
    payload += '=' * (-len(payload) % 4)
    decoded_payload = base64.urlsafe_b64decode(payload)

    # Convert the decoded payload into a dictionary
    payload_dict = json.loads(decoded_payload)
    
    return payload_dict

@click.command()
def login():
    
    PORT = 8888
    authorization_code = None  # This will hold the authorization code
    
    code_queue = queue.Queue()
    code_ready_event = threading.Event()  # Event to signal when the code is ready
    
    client_id = 'avalanchecli'
    realm = 'avalanchecms'
    keycloak_url = 'http://host.docker.internal:8080'
    redirect_uri = 'http://localhost:8888/'
    authorization_endpoint = f'{keycloak_url}/realms/{realm}/protocol/openid-connect/auth'
    token_endpoint = f'{keycloak_url}/realms/{realm}/protocol/openid-connect/token'
    
    code_verifier = generate_code_verifier()
    click.echo(f"code_verifier: {code_verifier}")
    
    code_challenge = generate_code_challenge(code_verifier)
    click.echo(f"code_challenge: {code_challenge}")
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': 'openid profile email',
        'redirect_uri': redirect_uri,
        'code_challenge': code_challenge.decode('utf-8'),
        'code_challenge_method': 'S256',
    }
    click.echo(f"params: {params}")

    authorization_url = requests.Request('GET', authorization_endpoint, params=params).prepare().url
    click.echo(f"authorization_url: {authorization_url}")
    
    class RedirectHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global authorization_code
            # Parse the query parameters
            query_components = parse_qs(urlparse(self.path).query)
            code = query_components.get("code", None)

            if code:
                authorization_code = code[0]  # Extract the authorization code
                code_queue.put(authorization_code)  # Put the code in the queue
                click.echo(f"Authorization code: {authorization_code}")
                # Respond to the browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authentication successful. You can close this window.")
                
                code_ready_event.set()  # Signal that the code is ready
                
                # Shutdown the server on a different thread
                click.echo("Initiating server shutdown...")
                threading.Thread(target=httpd.shutdown).start()                
                   
    # Server setup
    httpd = socketserver.TCPServer(("", PORT), RedirectHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    click.echo(f"Server started at http://host.docker.internal:{PORT}")
    
    try:
        click.echo("Opening the authorization URL in your browser...")
        click.echo(f"If it doesn't show up, open manually: {authorization_url}")
        webbrowser.open_new(authorization_url)
        
        # Define a timeout for user action (e.g., 3 minutes)
        timeout = 300 # seconds
        start_time = time.time()  # Record the start time        
                       
        # Wait for the authorization code or until timeout
        while not code_ready_event.is_set() and (time.time() - start_time) < timeout:            
            
            try:
                # Wait for a short period to allow interrupt
                code_ready_event.wait(timeout=1)
            except KeyboardInterrupt:
                click.echo("Interrupted by user. Exiting...")
                break  # Exit the loop if CTRL+C is pressed

        if code_ready_event.is_set():
            # Only attempt to get from the queue if the event was set
            authorization_code = code_queue.get()  
            click.echo(f"Received authorization code: {authorization_code}")
        elif (time.time() - start_time) >= timeout:
            # If we reached here because of a timeout
            click.echo("Timed out waiting for authorization. Please try again.")
        else:
            # If the loop exited for any other reason (e.g., user interruption)
            click.echo("Authorization process was not completed.")
        
    except Exception as e:
        # Handle any other exception that may occur
        click.echo(f"An error occurred: {e}") 
        
    finally:
        # Whether interrupted or completed, ensure the server is shut down gracefully
        if 'httpd' in locals() or 'httpd' in globals():
            httpd.shutdown()
            click.echo("Shutting down the server...")

        # Ensure the server thread has ended
        if 'server_thread' in locals() or 'server_thread' in globals():
            server_thread.join()
            click.echo("Server thread has been joined successfully.")
            
    cli_response = None           
    
    if authorization_code != None:

        # Exchange the authorization code for an access token
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'code': authorization_code,
            'code_verifier': code_verifier.decode('utf-8'),
        }
        response = requests.post(token_endpoint, data=data)
        
        click.echo(f"URL: {response.url}")
        click.echo(f"Status Code: {response.status_code}")
        click.echo("Response Headers:")
        for key, value in response.headers.items():
            click.echo(f"  {key}: {value}")
        click.echo("Request Headers:")
        for key, value in response.request.headers.items():
            click.echo(f"  {key}: {value}")
        click.echo(f"Response Body:\n{response.text}")    
        
        response_data = response.json()
               
        identity_token = decode_jwt_payload(response_data.get("id_token"))
        access_token = decode_jwt_payload(response_data.get("access_token"))
        refresh_token = decode_jwt_payload(response_data.get("refresh_token"))
        
        click.echo(f"Identity Token: {json.dumps(identity_token, indent=2)}")
        click.echo(f"Access Token: {json.dumps(access_token, indent=2)}")
        click.echo(f"Refresh Token: {json.dumps(refresh_token, indent=2)}")
        
        user_email = identity_token["email"]
        user_id = identity_token["sub"]
        
        cli_response = {
            "user": {
                "id": user_id,
                "email": user_email
            },
            "message": "Login successful."
        }        
        
    else:
        
        cli_response = {
            "error": {
                "message": "Login failed."
            }
        }
        
    click.echo(json.dumps(cli_response, indent=2))
        
    pass