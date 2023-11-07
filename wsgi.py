'''
Module for running the production server
'''
import os
from app import app

if __name__ == "__main__":
    os.environ['env'] = 'production'
    app.jinja_env.cache = {}
    app.run()
