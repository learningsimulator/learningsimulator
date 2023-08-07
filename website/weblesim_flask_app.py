# This file is also used on the server, in PythonAnywhere, read from
# the WSGI-config file /var/www/www_learningsimulator_online_wsgi.py
# ("from website.weblesim_flask_app import app as application")

from . import create_app
from .admin import add_admin_views

app = create_app()
add_admin_views(app)


if __name__ == '__main__':
    app.run(debug=True)
