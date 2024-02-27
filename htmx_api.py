import json
import os
import urllib

from flask import render_template, request, flash
from werkzeug.utils import secure_filename

from __init__ import app, dynamodb
from forms import TruckOpenGlassRackForm, TruckInteriorRackForm, TruckExteriorRackForm, UploadForm
import api
import utils

@app.route('/htmx-api/truck-form/body-type', methods=['GET'])
def truck_form_get_body_type_options():
    selected_body_type = request.args.get('truck_body_type', default=None, type=str)

    with open('./schemas/truck_body_to_forms.json', 'r', encoding='utf-8') as f:
        schema_json = json.load(f)
    
    form = eval(f'{schema_json[selected_body_type]}()')

    return render_template(f'./htmx/trucks/{selected_body_type}.html', form=form)

@app.route('/htmx-api/truck-form/interior-rack-options', methods=['GET'])
def truck_form_interior_rack_options():
    interior_rack_quantity = request.args.get('interior_rack_quantity', default=0, type=int)

    forms = []
    for i in range(interior_rack_quantity):
        forms.append(TruckInteriorRackForm())

    return render_template('./htmx/trucks/interior_rack_info.html', forms=forms)

@app.route('/htmx-api/truck-form/exterior-rack-options', methods=['GET'])
def truck_form_exterior_rack_options():
    exterior_rack_quantity = request.args.get('exterior_rack_quantity', default=0, type=int)

    forms = []
    for i in range(exterior_rack_quantity):
        forms.append(TruckExteriorRackForm())

    return render_template('./htmx/trucks/exterior_rack_info.html', forms=forms)

@app.route('/htmx-api/layout-form/manifest-upload', methods=['GET'])
def layout_form_get_manifest_upload():
    selected_manifest = request.args.get('manifest', default=None, type=str)
    manifest_upload_form = UploadForm()

    return render_template('./htmx/layout/manifest-upload.html',
        manifest_upload_form=manifest_upload_form,
        selected_manifest=selected_manifest
    )

@app.route('/htmx-api/layout-form/manifest-upload', methods=['POST'])
def layout_form_post_manifest_upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        if 'file' not in request.files:
            flash('No file part', 'danger')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
        if file and utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = filename.split('.')[0]
            file.save(os.path.join(app.config['MANIFEST_PATH'], f"{filename}.csv"))
        manifest_params = utils.get_manifest_params()
        manifest_column_names = utils.get_manifest_column_names(filename)

    return render_template('./htmx/layout/describe-manifest.html', 
        manifest_name=filename,
        manifest_params=manifest_params,
        manifest_column_names=manifest_column_names
    )

@app.route('/htmx-api/layout-form/describe-manifest', methods=['GET'])
def layout_form_get_describe_manifest():
    manifest_name = request.args.get('manifest', default=None, type=str)

    manifest_params = utils.get_manifest_params()
    manifest_details = utils.get_manifest_details(manifest_name)
    manifest_unit_map = utils.get_manifest_units(manifest_name)
    flag_incomplete_manifest_data = utils.check_for_complete_manifest_data(manifest_name)

    return render_template('./htmx/layout/mapped-manifest.html',
        manifest_name=manifest_name,
        manifest_params=manifest_params,
        manifest_details=manifest_details,
        manifest_unit_map=manifest_unit_map,
        flag_incomplete_manifest_data=flag_incomplete_manifest_data
    )

@app.route('/htmx-api/layout-form/describe-manifest', methods=['POST'])
def layout_form_post_describe_manifest():
    manifest_name = request.args.get('manifest', default=None, type=str)

    manifest_params = utils.get_manifest_params()
    manifest_map = utils.make_manifest_map(request.form)
    manifest_details = utils.analyze_manifest(manifest_name, manifest_map)
    utils.update_manifest(manifest_name, manifest_params, manifest_details)

    utils.save_manifest_units(manifest_name, manifest_map)
    manifest_unit_map = utils.get_manifest_units(manifest_name)

    flag_incomplete_manifest_data = utils.check_for_complete_manifest_data(manifest_name)

    return render_template('./htmx/layout/mapped-manifest.html',
        manifest_name=manifest_name,
        manifest_params=manifest_params,
        manifest_details=manifest_details,
        manifest_unit_map=manifest_unit_map,
        flag_incomplete_manifest_data=flag_incomplete_manifest_data
    )

@app.route('/htmx-api/layout-form/save-manifest', methods=['POST'])
def layout_form_post_save_manifest():
    manifest_name = request.args.get('manifest', default=None, type=str)
    row_to_delete = request.args.get('row_to_delete', default=None, type=int)

    manifest_details = utils.format_manifest_form_data(request.form, row_to_delete)

    manifest_params = utils.get_manifest_params()
    utils.update_manifest(manifest_name, manifest_params, manifest_details)
    manifest_unit_map = utils.get_manifest_units(manifest_name)
    flag_incomplete_manifest_data = utils.check_for_complete_manifest_data(manifest_name)

    return render_template('./htmx/layout/mapped-manifest.html',
        manifest_name=manifest_name,
        manifest_params=manifest_params,
        manifest_details=manifest_details,
        manifest_unit_map=manifest_unit_map,
        flag_incomplete_manifest_data=flag_incomplete_manifest_data
    )

@app.route('/htmx-api/layout-form/generate-shipment-plan', methods=['POST'])
def layout_form_post_generate_shipment_plan():
    truck = request.args.get('truck', default=None, type=str)
    manifest_name = request.args.get('manifest', default=None, type=str)

    truck_details = api.truck_api_get_truck(urllib.parse.unquote(truck))
    manifest_details = utils.format_manifest_form_data(request.form)
    manifest_units = utils.get_manifest_units(manifest_name)

    shipment_plan = utils.generate_shipment_plan(truck_details, manifest_name, manifest_details, manifest_units)
    api.store_shipment_plan(shipment_plan)

    return render_template('./htmx/layout/shipment-plan.html',
        shipment_plan=shipment_plan
    )
    