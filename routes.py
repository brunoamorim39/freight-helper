'''
Handles all of the URL routing for the server
'''
from decimal import Decimal
import glob
import json
import os
import urllib

from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests
from werkzeug.utils import secure_filename

from __init__ import app, dynamodb
import api
import utils
import errors
from models import User
from forms import TruckForm, RackForm, UploadForm
from emails import send_creation_confirmation_email, send_password_reset_email

# from utils import allowed_file, get_manifest_params, get_manifest_column_names, make_manifest_map, check_if_manifest_mapped, get_manifest_map, analyze_manifest, save_truck, delete_truck, save_rack, delete_rack, generate_truck_layout

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
    return errors._404('invalid method')

@app.route('/configure-trucks', methods=['GET', 'POST'])
def configure_trucks():
    '''
    Route for configuring trucks
    '''
    truck_form = TruckForm()
    if request.method == 'GET':
        selected_truck = request.args.get('truck', default=None, type=str)

        if selected_truck:
            truck_response = api.truck_api_get_truck(selected_truck)
            if request.args.get('edit_mode'):
                truck_form.truck_name.data = truck_response['name']
                truck_form.interior_length.data = Decimal(truck_response['interior_length'])
                truck_form.interior_width.data = Decimal(truck_response['interior_width'])
                truck_form.interior_height.data = Decimal(truck_response['interior_height'])
                truck_form.distance_to_rear_axle_from_cab.data = Decimal(truck_response['distance_to_rear_axle_from_cab'])
                truck_form.exterior_racks.data = truck_response['exterior_rack_capability']

        trucks = api.truck_api_get_all_trucks()

        return render_template('configure_trucks.html',
            truck_form=truck_form,
            selected_truck=selected_truck,
            truck_data=truck_response if selected_truck else None,
            trucks=trucks
        )
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
            utils.save_truck(truck_obj)

            if request.args.get('edit_mode'):
                utils.delete_truck(truck_obj)
        return redirect(url_for('configure_trucks'))
    return errors._404('invalid method')

@app.route('/configure-racks', methods=['GET', 'POST'])
def configure_racks():
    '''
    Route for configuring racks
    '''
    rack_form = RackForm()
    if request.method == 'GET':
        selected_rack = request.args.get('rack', default=None, type=str)

        if selected_rack:
            rack_response = api.rack_api_get_rack(selected_rack)
            if request.args.get('edit_mode'):
                rack_form.rack_name.data = rack_response['name']
                rack_form.rack_length.data = Decimal(rack_response['rack_length'])
                rack_form.rack_depth.data = Decimal(rack_response['rack_depth'])
                rack_form.rack_height.data = Decimal(rack_response['rack_height'])

        racks = api.rack_api_get_all_racks()

        return render_template('configure_racks.html',
            rack_form=rack_form,
            selected_rack=selected_rack,
            rack_data=rack_response if selected_rack else None,
            racks=racks
        )
    if request.method == 'POST':
        if rack_form.validate_on_submit():
            rack_obj = {
                "name": request.form.get('rack_name'),
                "rack_length": request.form.get('rack_length'),
                "rack_depth": request.form.get('rack_depth'),
                "rack_height": request.form.get('rack_height')
            }
            utils.save_rack(rack_obj)

            if request.args.get('edit_mode'):
                utils.delete_rack(rack_obj)
        return redirect(url_for('configure_racks'))
    return errors._404('invalid method')

@app.route('/parse-manifest', methods=['GET', 'POST'])
def parse_manifest():
    '''
    Route for parsing and preparing a shipping manifest
    '''
    upload_form = UploadForm()
    if request.method == 'GET':
        selected_manifest = request.args.get('manifest', default=None, type=str)
        manifest_mapped = request.args.get('mapped', default=False, type=bool)

        if selected_manifest is not None:
            manifest_params = utils.get_manifest_params()
            manifest_column_names = utils.get_manifest_column_names(selected_manifest)

            if utils.check_if_manifest_mapped(selected_manifest):
                manifest_mapped = True
                manifest_map = utils.get_manifest_map(selected_manifest)
                manifest_details = utils.analyze_manifest(selected_manifest, manifest_map)

        uploaded_manifests = glob.glob(f"{app.config['MANIFEST_PATH']}/*")
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
    if request.method == 'POST':
        if upload_form.validate_on_submit():
            if 'file' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
            if file and utils.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['MANIFEST_PATH'], f"{filename.split('.')[0]}.csv"))
                return redirect(url_for('parse_manifest'))
            
        manifest_params = utils.get_manifest_params()
        if request.form.get(manifest_params[0]['key']):
            utils.make_manifest_map(manifest_name=request.args.get('manifest', default=None, type=str), manifest_params=request.form)
            return redirect(f"{request.path}?{request.args.get('manifest')}")
    return errors._404('invalid method')

@app.route('/generate-layout', methods=['GET', 'POST'])
def generate_layout():
    '''
    Route for generating a truck layout
    '''
    if request.method == 'GET':
        selected_truck = urllib.parse.unquote(request.args.get('truck', default=None, type=str))
        selected_racks = urllib.parse.unquote(request.args.get('racks', default=None, type=str))
        selected_manifest = urllib.parse.unquote(request.args.get('manifest', default=None, type=str))[1:-1]

        trucks = api.truck_api_get_all_trucks()
        if selected_truck:
            trucks['selected_truck'] = selected_truck

        racks = api.rack_api_get_all_racks()
        if selected_racks:
            racks['selected_racks'] = selected_racks

        manifests = api.manifest_api_get_all_manifests()
        if selected_manifest:
            manifests['selected_manifest'] = selected_manifest
        for idx, manifest in enumerate(manifests['manifests']):
            manifests['manifests'][idx] = manifest.split('\\')[-1].split('.')[0]

        return render_template('generate_layout.html',
            trucks=trucks,
            racks=racks,
            manifests=manifests
        )
    if request.method == 'POST':
        selected_truck = urllib.parse.unquote(request.args.get('truck', default=None, type=str))
        selected_racks = urllib.parse.unquote(request.args.get('racks', default=None, type=str))
        selected_manifest = urllib.parse.unquote(request.args.get('manifest', default=None, type=str))

        truck_details = api.truck_api_get_truck(selected_truck)

        racks_details = []
        for rack in eval(selected_racks):
            racks_details.append(api.rack_api_get_rack(rack))

        manifest_map = utils.get_manifest_map(selected_manifest)
        manifest_details = utils.analyze_manifest(selected_manifest, manifest_map)

        utils.generate_truck_layout(truck_details, racks_details, manifest_details)

        return 'Test Hello'
    return errors._404('invalid method')
