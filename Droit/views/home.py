from flask import Blueprint, render_template, request, session, redirect, url_for
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
    if current_user.is_anonymous:
        # redirect to login page if not logged in
        return redirect(url_for('auth.login'))
    userid = current_user.get_user_id()
    email = current_user.get_email()
    address = current_user.get_address()
    policies = []
    for p in current_user.get_policy():
        cur = {'uid': p.get_uid(), 'location': p.get_location(), 'policy_json': p.get_policy_json()}
        policies.append(cur)
    print(policies)
    print(current_user.get_policy())
    if not address:
        address = session.get('address', None)
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