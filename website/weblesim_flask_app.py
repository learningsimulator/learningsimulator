# This file is also used on the server, in PythonAnywhere, read from
# the WSGI-config file /var/www/www_learningsimulator_online_wsgi.py
# ("from weblesim_flask_app import app as application")

from . import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
