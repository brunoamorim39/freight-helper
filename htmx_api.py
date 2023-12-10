import json
import os

from flask import request

from __init__ import app, dynamodb

@app.route('/htmx-api/truck-form')
def truck_form_get_body_type_options():
    print(request.form)
    return 'test'