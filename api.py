import json
import os

from __init__ import app, dynamodb

@app.route('/api/trucks', methods=['GET'])
def truck_api_get_all_trucks():
    return {"trucks": os.listdir(app.config['TRUCK_PATH'])}

@app.route('/api/trucks', methods=['POST'])
def truck_api_add_truck():
    return None

@app.route('/api/trucks/<truck_name>', methods=['GET'])
def truck_api_get_truck(truck_name):
    with open(f"{app.config['TRUCK_PATH']}/{truck_name}", 'r', encoding='utf-8') as truckfile:
        truck_json = json.load(truckfile)
    return truck_json

@app.route('/api/racks', methods=['GET'])
def rack_api_get_all_racks():
    return {"racks": os.listdir(app.config['RACK_PATH'])}

@app.route('/api/racks', methods=['POST'])
def rack_api_add_rack():
    return None

@app.route('/api/racks/<rack_name>', methods=['GET'])
def rack_api_get_rack(rack_name):
    with open(f"{app.config['RACK_PATH']}/{rack_name}", 'r', encoding='utf-8') as rackfile:
        rack_json = json.load(rackfile)
    return rack_json

@app.route('/api/manifests', methods=['GET'])
def manifest_api_get_all_manifests():
    return {"manifests": os.listdir(app.config['MANIFEST_PATH'])}

@app.route('/api/manifests/<manifest>', methods=['GET'])
def manifest_api_get_manifest(manifest):
    return

@app.route('/api/layouts', methods=['GET'])
def generate_layout_api_get_layouts():
    return

@app.route('/api/layouts', methods=['POST'])
def generate_layout_api_create_layout():
    return
