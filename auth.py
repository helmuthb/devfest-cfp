from models import User
from werkzeug.exceptions import Unauthorized, Forbidden, NotFound
from flask import Blueprint
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from utils import get_random_string


# define blueprint
auth_api = Blueprint('auth', __name__)


# load OAuth secrets
google_secrets = json.loads(open('google_secrets.json', 'r').read())
facebook_secrets = json.loads(open('facebook_secrets.json', 'r').read())
twitter_secrets = json.loads(open('twitter_secrets.json', 'r').read())
github_secrets = json.loads(open('github_secrets.json', 'r').read())


# get the current anti-csrf token
# if not set it will generate a new one and store# it into the session
def get_sync_token():
    state = session.get('state_token')
    if state is None:
        state = getRandomString()
        session['state_token'] = state
    return state


# helper function: get a field from the request parameters
# or the request body
# irrespective if the body is JSON or multipart
# or urlencoded
def get_request_field(name):
    value = request.form.get(name)
    if value is None:
        json_body = request.get_json(force=True, silent=True, cache=True)
        if json_body is not None:
            value = json_body.get(name)
    return value


# decorator: is the user logged in?
# Otherwise throw exception
def requires_login(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        # is the user not yet logged in?
        if session.get('user_id') is None:
            raise Unauthorized()
        else:
            return func(*args, **kwargs)
    return func_wrapper


# decorator: check state token
def checks_token(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        # is the state token valid?
        if get_request_field('state_token') != get_sync_token():
            raise BadRequest('Invalid state token')
        else:
            return func(*args, **kwargs)
    return func_wrapper


# subclass of JSONEncoder: allow jsonify of my model objects
# http://stackoverflow.com/questions/21411497/flask-jsonify-a-list-of-objects
class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if "toDict" in dir(obj):
            return obj.toDict()
        return super(MyJSONEncoder, self).default(obj)


# Google login
@auth_api.route('/connect-google', methods=['POST'])
@checks_token
def connect_google():
    """
    Connect the current user with the Google credentials provided.
    """
    code = request.data
    google = session['google']
    if google is None:
        google = {}
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != google_secrets.web.client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check if user is already logged in
    stored_token = google.get('access_token')
    stored_gplus_id = google.get('gplus_id')
    gplus_id = result['user_id']
    if stored_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    google['access_token'] = access_token
    google['gplus_id'] = gplus_id
    session['google'] = google
    response = make_response(
        json.dumps('Successfully connected user.'), 200)
    response.headers['Content-Type'] = 'application/json'
    # get user details from Google
    url = ('https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=%s'
        % access_token)
    result = json.loads(h.request(url, 'GET'))
    # get user from the database / create new user
    user_uid = session.get("user_id")
    if user_id is None:
        user = db.session.query(User).filter(google_id == gplus_id).first()
        if user is None:
            user = User()
    else:
        user = db.session.query(User).get(user_id)
    # update google details
    user.google_id = gplus_id
    if not user.name:
        user.name = result.get("name")
    if not user.email:
        user.email = result.get("email")
    if not user.picture_url:
        user.picture_url = result.get("picture")
    # update database
    db.session.add(user)
    db.session.commit()
    return response


# OAuth handling - called when user wants to logout
@auth_api.route('/disconnect')
def disconnect():
    """
    Function to logout a user. It checks the currently used identity provider
    and performs the necessary logout actions.
    """
    if 'google' in session:
        disconnect_google()
    pass


def disconnect_google():
    """
    Helper function - perform logout from Google
    """
    google = session['google']
    if google is None:
        return
    access_token = session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Currently not logged in'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # revoke current token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # I do not chekc the status - either the token is revoked
    # successfully or the token is invalid - in both cases I forget
    # the user
    del session['access_token']
    del session['gplus_id']
    response = make_response(json.dumps('Successfully logged out'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
