# This file is only used on the server, in PythonAnywhere, read from
# the WSGI-config file /var/www/www_learningsimulator_online_wsgi.py
# ("from main import app as application")

from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
