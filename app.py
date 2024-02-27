'''
Runs the app for local development
'''
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from __init__ import app
import routes

if __name__ == "__main__":
    os.environ['env'] = 'local'
    app.jinja_env.cache = {}
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.run()
