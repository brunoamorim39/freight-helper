import json
import os

from flask import render_template, request

from __init__ import app, dynamodb
from forms import TruckOpenGlassRackForm, TruckExteriorRackForm

@app.route('/htmx-api/truck-form/body-type', methods=['GET'])
def truck_form_get_body_type_options():
    selected_body_type = request.args.get('truck_body_type', default=None, type=str)

    with open('./schemas/truck_body_to_forms.json', 'r', encoding='utf-8') as f:
        schema_json = json.load(f)
    
    form = eval(f'{schema_json[selected_body_type]}()')

    return render_template(f'htmx/trucks/{selected_body_type}.html', form=form)

@app.route('/htmx-api/truck-form/exterior-rack-options', methods=['GET'])
def truck_form_exterior_rack_options():
    exterior_rack_quantity = request.args.get('exterior_rack_quantity', default=0, type=int)

    forms = []
    for i in range(exterior_rack_quantity):
        forms.append(TruckExteriorRackForm())

    return render_template(f'htmx/trucks/exterior_rack_info.html', forms=forms)
