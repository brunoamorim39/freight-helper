'''
Handles all of the URL routing for the server
'''
from decimal import Decimal
import glob
import json
import os

from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests
from werkzeug.utils import secure_filename

from __init__ import app, dynamodb
from models import User
from forms import TruckForm, RackForm, UploadForm
from emails import send_creation_confirmation_email, send_password_reset_email

from utils import allowed_file, get_manifest_params, get_manifest_column_names, make_manifest_map, check_if_manifest_mapped, get_manifest_map, analyze_manifest, save_truck, delete_truck, save_rack, delete_rack

TRUCK_PATH = './resources/trucks'
RACK_PATH = './resources/racks'

# @login_manager.user_loader
# def load_user(user_id):
#     '''
#     Loads a User object based on the email information provided
#     '''
#     accounts_table = dynamodb.Table('user_accounts')
#     user = accounts_table.get_item(Key={'email': user_id}).get('Item', None)
#     return User(
#         email=user['email'],
#         display_name=user['display_name'],
#         password=user['password'],
#         created_on=user['created_on'],
#         updated_on=user['updated_on'],
#         confirmed=user['confirmed'],
#         subscription=user['subscription']
#     )

@app.route('/', methods=['GET'])
def landing_page():
    '''
    Landing page of the website
    '''
    if request.method == 'GET':
        return render_template('landing_page.html')
    return _404('invalid method')

@app.route('/configure-trucks', methods=['GET', 'POST'])
def configure_trucks():
    '''
    Route for configuring trucks
    '''
    truck_form = TruckForm()
    if request.method == 'POST':
        if truck_form.validate_on_submit():
            truck_obj = {
                "name": request.form.get('truck_name'),
                "interior_length": request.form.get('interior_length'),
                "interior_width": request.form.get('interior_width'),
                "interior_height": request.form.get('interior_height'),
                "distance_to_rear_axle_from_cab": request.form.get('distance_to_rear_axle_from_cab'),
                "exterior_rack_capability": request.form.get('exterior_racks')
            }
            save_truck(truck_obj)

            if request.args.get('edit_mode'):
                delete_truck(truck_obj)
        return redirect(url_for('configure_trucks'))
    if request.method == 'GET':
        selected_truck = request.args.get('truck', default=None, type=str)

        if selected_truck:
            truck_response = truck_api_get_truck(selected_truck)
            if request.args.get('edit_mode'):
                truck_form.truck_name.data = truck_response['name']
                truck_form.interior_length.data = Decimal(truck_response['interior_length'])
                truck_form.interior_width.data = Decimal(truck_response['interior_width'])
                truck_form.interior_height.data = Decimal(truck_response['interior_height'])
                truck_form.distance_to_rear_axle_from_cab.data = Decimal(truck_response['distance_to_rear_axle_from_cab'])
                truck_form.exterior_racks.data = truck_response['exterior_rack_capability']

        trucks = truck_api_get_all_trucks()

        return render_template('configure_trucks.html',
            truck_form=truck_form,
            selected_truck=selected_truck,
            truck_data=truck_response if selected_truck else None,
            trucks=trucks
        )
    return _404('invalid method')

@app.route('/configure-racks', methods=['GET', 'POST'])
def configure_racks():
    '''
    Route for configuring racks
    '''
    rack_form = RackForm()
    if request.method == 'POST':
        if rack_form.validate_on_submit():
            rack_obj = {
                "name": request.form.get('rack_name'),
                "rack_length": request.form.get('rack_length'),
                "rack_depth": request.form.get('rack_depth'),
                "rack_height": request.form.get('rack_height')
            }
            save_rack(rack_obj)

            if request.args.get('edit_mode'):
                delete_rack(rack_obj)
        return redirect(url_for('configure_racks'))
    if request.method == 'GET':
        selected_rack = request.args.get('rack', default=None, type=str)

        if selected_rack:
            rack_response = rack_api_get_rack(selected_rack)
            if request.args.get('edit_mode'):
                rack_form.rack_name.data = rack_response['name']
                rack_form.rack_length.data = Decimal(rack_response['rack_length'])
                rack_form.rack_depth.data = Decimal(rack_response['rack_depth'])
                rack_form.rack_height.data = Decimal(rack_response['rack_height'])

        racks = rack_api_get_all_racks()

        return render_template('configure_racks.html',
            rack_form=rack_form,
            selected_rack=selected_rack,
            rack_data=rack_response if selected_rack else None,
            racks=racks
        )
    return _404('invalid method')

@app.route('/parse-manifest', methods=['GET', 'POST'])
def parse_manifest():
    '''
    Route for parsing and preparing a shipping manifest
    '''
    upload_form = UploadForm()
    if request.method == 'POST':
        if upload_form.validate_on_submit():
            if 'file' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['MANIFEST_UPLOAD_FOLDER'], f"{filename.split('.')[0]}.csv"))
                return redirect(url_for('parse_manifest'))
            
        manifest_params = get_manifest_params()
        if request.form.get(manifest_params[0]['key']):
            make_manifest_map(manifest_name=request.args.get('manifest', default=None, type=str), manifest_params=request.form)
            return redirect(f"{request.path}?{request.args.get('manifest')}")

    if request.method == 'GET':
        selected_manifest = request.args.get('manifest', default=None, type=str)
        manifest_mapped = request.args.get('mapped', default=False, type=bool)

        if selected_manifest is not None:
            manifest_params = get_manifest_params()
            manifest_column_names = get_manifest_column_names(selected_manifest)

            if check_if_manifest_mapped(selected_manifest):
                manifest_mapped = True
                manifest_map = get_manifest_map(selected_manifest)
                manifest_details = analyze_manifest(selected_manifest, manifest_map)

        uploaded_manifests = glob.glob('./uploads/manifests/*')
        trimmed_manifests = []
        for manifest in uploaded_manifests:
            trimmed_manifests.append(manifest.split('\\')[-1].split('.')[0])

        return render_template('parse_manifest.html',
            upload_form=upload_form,
            manifests=trimmed_manifests,
            selected_manifest=selected_manifest,
            manifest_params=manifest_params if selected_manifest else None,
            manifest_column_names=manifest_column_names if selected_manifest else None,
            manifest_map=manifest_map if manifest_mapped else None,
            selected_manifest_details=manifest_details if manifest_mapped else None
        )
    return _404('invalid method')

@app.route('/generate-layout', methods=['GET', 'POST'])
def generate_layout():
    '''
    Route for generating a truck layout
    '''
    if request.method == 'POST':
        return
    if request.method == 'GET':
        return render_template('generate_layout.html')
    return _404('invalid method')

@app.route('/api/trucks', methods=['GET'])
def truck_api_get_all_trucks():
    return {"trucks": os.listdir(TRUCK_PATH)}

@app.route('/api/trucks', methods=['POST'])
def truck_api_add_truck():
    return None

@app.route('/api/trucks/<truck_name>', methods=['GET'])
def truck_api_get_truck(truck_name):
    if request.method == 'GET':
        with open(f"{TRUCK_PATH}/{truck_name}", 'r', encoding='utf-8') as truckfile:
            truck_json = json.load(truckfile)
        return truck_json

@app.route('/api/racks', methods=['GET'])
def rack_api_get_all_racks():
    return {"racks": os.listdir(RACK_PATH)}

@app.route('/api/racks', methods=['POST'])
def rack_api_add_rack():
    return None

@app.route('/api/racks/<rack_name>', methods=['GET'])
def rack_api_get_rack(rack_name):
    if request.method == 'GET':
        with open(f"{RACK_PATH}/{rack_name}", 'r', encoding='utf-8') as rackfile:
            rack_json = json.load(rackfile)
        return rack_json

@app.errorhandler(404)
def _404(error):
    '''
    404 Error handler
    '''
    print(error)
    return render_template('errors/404.html'), 404

@app.errorhandler(413)
def _413(error):
    '''
    413 Error handler
    '''
    print(error)
    return 'File is too large', 413
