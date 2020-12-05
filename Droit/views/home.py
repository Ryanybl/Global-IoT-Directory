from flask import Blueprint, render_template, request, session
from flask_login import current_user
from ..auth.oauth2 import oauth
import json
home = Blueprint('home', __name__)

@home.route('/')
@home.route('/index')
@home.route('/home')
def index():
    """Render the home page for the project

    Returns:
        response: the flask response object representing the HTML page
    """
    return render_template("home/index.html")


@home.route('/about', methods=['GET', 'POST'])
def about():
    """Render the abount page for the project

    Returns:
        response: the flask response object representing the HTML page
    """

    userid = current_user.get_user_id()
    email = current_user.get_email()
    address = current_user.get_address()
    policies = []
    for p in current_user.get_policy():
        cur = {}
        cur['uid'] = p.get_uid()
        cur['location'] = p.get_location()
        cur['policy_json'] = p.get_policy_json()
        policies.append(cur)
    print(policies)
    print(current_user.get_policy())
    if not address:
        address = session.get('return_address', None)
    # if the current user logged in using oidc
    provider = current_user.get_provider_name()
    # define additional scope needed
    add_scope = "openid address"
    # Note: the scope added must be pre-included in providers_config

    if request.method == 'POST':
        if 'confirm' in request.form:
            if provider:
                client = oauth.create_client(provider)
                return client.authorize_redirect(add_scope=add_scope)

    return render_template("home/about.html", userid=userid, email=email, address=address, policies = policies)

@home.route('/contact')
def contact():
    """Render the contact page for the project

    Returns:
        response: the flask response object representing the HTML page
    """
    return render_template("home/contact.html")


@home.route('/delete_policy')
def policy_decision():

    return render_template('home/about.html', tagname = 'delete_policy')