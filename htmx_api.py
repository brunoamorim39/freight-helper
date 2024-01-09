import json
import os

from flask import render_template, request, flash
from werkzeug.utils import secure_filename

from __init__ import app, dynamodb
from forms import TruckOpenGlassRackForm, TruckExteriorRackForm, UploadForm
import utils

@app.route('/htmx-api/truck-form/body-type', methods=['GET'])
def truck_form_get_body_type_options():
    selected_body_type = request.args.get('truck_body_type', default=None, type=str)

    with open('./schemas/truck_body_to_forms.json', 'r', encoding='utf-8') as f:
        schema_json = json.load(f)
    
    form = eval(f'{schema_json[selected_body_type]}()')

    return render_template(f'./htmx/trucks/{selected_body_type}.html', form=form)

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
    form = UploadForm()
    return render_template('./htmx/layout/manifest-upload.html',
        form=form,
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
    manifest_map = utils.get_manifest_map(manifest_name)
    manifest_details = utils.analyze_manifest(manifest_name, manifest_map)

    return render_template('./htmx/layout/mapped-manifest.html',
        manifest_name=manifest_name,
        manifest_params=manifest_params,
        manifest_details=manifest_details
    )

@app.route('/htmx-api/layout-form/describe-manifest', methods=['POST'])
def layout_form_post_describe_manifest():
    manifest_name = request.args.get('manifest', default=None, type=str)

    print(request.form)
    
    manifest_params = utils.get_manifest_params()
    utils.make_manifest_map(manifest_name=manifest_name, manifest_params=request.form)
    manifest_map = utils.get_manifest_map(manifest_name)
    manifest_details = utils.analyze_manifest(manifest_name, manifest_map)

    return render_template('./htmx/layout/mapped-manifest.html',
        manifest_name=manifest_name,
        manifest_params=manifest_params,
        manifest_details=manifest_details
    )
