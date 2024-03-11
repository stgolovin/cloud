from flask import Flask, redirect, session, request, render_template
import requests
import random
from typing import List, Optional

from config import *


app = Flask(__name__)
app.secret_key = b"\xf3'X6wnlYqJo\x16}M\xcb\x8d\xb4@\xd9\xc0\n\xd1\x08l"


@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


@app.route('/auth')
def auth():
    """Redirect to the OAuth authorization URL."""
    client_id = OAUTH_APP_ID
    scope = 'all'
    authorize_url = f"{AUTHORIZATION_BASE_URL}?response_type=code&client_id={client_id}&redirect_uri={REDIRECT_URI}&scope={scope}"
    return redirect(authorize_url, code=302)


@app.route('/callback')
def resolved():
    """Exchange authorization code for an access token."""
    authorization_code = request.args.get('code') or session.get('code', None)
    if authorization_code:
        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': OAUTH_APP_ID,
            'client_secret': OAUTH_APP_SECRET
        }
        response = requests.post(TOKEN_URL, data=token_data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            session['access_token'] = access_token
            return render_template('endpoints.html')
        else:
            return f'Error: {response.text}', response.status_code
    else:
        return "Authorization code not found."


def get_access_token() -> Optional[str]:
    """Retrieve the access token from the session."""
    return session.get('access_token')


def get_extension_list() -> List[str]:
    """Retrieve a list of extensions."""
    access_token = get_access_token()
    if not access_token:
        return 'Unauthorized', 401
    url = 'https://apiproxy.telphin.ru/api/ver1.0/user/'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    user_data = make_api_request(url, headers)
    client_id_value = user_data.get('client_id')
    extension_url = f'https://apiproxy.telphin.ru/api/ver1.0/client/{client_id_value}/extension/'
    extensions_data = make_api_request(extension_url, headers)
    ext_list = [extension.get('name') for extension in extensions_data]
    return ext_list


@app.route('/extlist/')
def extlist() -> List[str]:
    """Retrieve a list of extensions."""
    return get_extension_list()


@app.route('/randomext/')
def randomext() -> str:
    """Retrieve a random extension."""
    ext_list = get_extension_list()
    selected_option = random.choice(ext_list)
    return selected_option


def make_api_request(url: str, headers: dict):
    """Make a GET request to the specified URL with headers and return the JSON response."""
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5055)
