'''
Utility functions for use with the freight helper tool.
'''
import csv
import json

ALLOWED_EXTENSIONS = {'csv', 'xslx', 'ods'}

def allowed_file(filename):
    '''
    Determines whether the file being uploaded is of an acceptable extension.
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_manifest_params():
    with open('./schemas/manifest_params.json', 'r', encoding='utf-8') as jsonfile:
        manifest_params = json.load(jsonfile)['manifest_parameters']
    return manifest_params

def get_manifest_column_names(manifest_name):
    manifest_column_names = []
    with open(f'./uploads/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for column_name in row:
                manifest_column_names.append(column_name)
            break
    
    return manifest_column_names

def make_manifest_map(manifest_name, manifest_params):
    with open('./maps/manifest_maps.json', 'r', encoding='utf-8') as jsonfile:
        manifest_maps = json.load(jsonfile)
        manifest_maps[manifest_name] = {}
        for param in manifest_params:
            manifest_maps[manifest_name][param] = manifest_params[param]

    with open('./maps/manifest_maps.json', 'w', encoding='utf-8') as jsonfile:
        jsonfile.write(json.dumps(manifest_maps))

def check_if_manifest_mapped(manifest_name):
    with open('./maps/manifest_maps.json', 'r', encoding='utf-8') as jsonfile:
        manifest_maps = json.load(jsonfile)
    if manifest_name in manifest_maps:
        return True
    return False

def get_manifest_map(manifest_name):
    with open('./maps/manifest_maps.json', 'r', encoding='utf-8') as jsonfile:
        manifest_maps = json.load(jsonfile)
    return manifest_maps[manifest_name]

def analyze_manifest(manifest_name, manifest_map):
    '''
    Analyzes the selected manifest to determine the details for the shipment for later use in optimization.
    '''
    manifest_details = []
    with open(f'./uploads/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            manifest_details.append(
                {
                    "stop_number": row[manifest_map['stop_number']],
                    "description": row[manifest_map['description']],
                    "quantity": row[manifest_map['quantity']],
                    "weight": row[manifest_map['weight']],
                    "square_footage": row[manifest_map['square_footage']]
                }
            )
        
    manifest_details.sort(key=lambda x: x['stop_number'])
    return manifest_details
