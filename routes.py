'''
Handles all of the URL routing for the server
'''
import glob
import json
import os

from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from __init__ import app, dynamodb
from models import User
from forms import UploadForm
from emails import send_creation_confirmation_email, send_password_reset_email

from utils import allowed_file, get_manifest_params, get_manifest_column_names, make_manifest_map, check_if_manifest_mapped, get_manifest_map, analyze_manifest

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
    if request.method == 'POST':
        return
    if request.method == 'GET':
        return render_template('configure_trucks.html')
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
