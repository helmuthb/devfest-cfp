from flask import Flask
from auth import auth_api
from utils import get_random_string


# when this script is called from the command line
# vs being imported as a module from some other module
if __name__ == '__main__':
    # set debugging
    app.debug = True
    # create key for session storage
    app.secret_key = getRandomString()
    # assign my json encoder
    app.json_encoder = MyJSONEncoder
    # add markdown filter
    Markdown(app)
    # add blueprints
    app.register_blueprint(auth_api)
    # start the Flask server on port 8080
    app.run(host='0.0.0.0', port=8080)