'''
Utility functions for use with the freight helper tool.
'''
import csv
import json
import os

ALLOWED_EXTENSIONS = {'csv', 'xslx', 'ods'}

def unit_convert(from_unit, to_unit, val):
    '''
    Takes an object key and converts the value of it from a specific unit to a specific unit
    '''
    val = float(val)
    if from_unit == 'inches' and to_unit == 'feet':
        return val / 12
    elif from_unit == 'feet' and to_unit == 'inches':
        return val * 12

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
    with open(f'./resources/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
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
    with open(f'./resources/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
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

def save_truck(truck_obj):
    with open(f"./resources/trucks/{truck_obj['name']}", 'w', encoding='utf-8') as truckfile:
        truckfile.write(json.dumps(truck_obj))

def delete_truck(truck_obj):
    os.remove(f"./resources/trucks/{truck_obj['name']}")

def save_rack(rack_obj):
    with open(f"./resources/racks/{rack_obj['name']}", 'w', encoding='utf-8') as rackfile:
        rackfile.write(json.dumps(rack_obj))

def delete_rack(rack_obj):
    os.remove(f"./resources/racks/{rack_obj['name']}")

def generate_truck_layout(truck_details, racks_details, manifest_details):
    print(truck_details)
    # print(racks_details)
    # print(manifest_details)

    widest_rack = ''
    for rack in racks_details:
        rack['rack_length'] = unit_convert(from_unit='inches', to_unit='feet', val=rack['rack_length'])
        rack['rack_depth'] = unit_convert(from_unit='inches', to_unit='feet', val=rack['rack_depth'])
        rack['rack_height'] = unit_convert(from_unit='inches', to_unit='feet', val=rack['rack_height'])

        widest_rack_position = next((idx for idx, rack in enumerate(racks_details) if rack['name'] == widest_rack), None)
        if widest_rack_position is None or rack['rack_depth'] > racks_details[widest_rack_position]['rack_depth']:
            widest_rack = rack['name']
    
    print(racks_details)
    print(widest_rack)

    return layout
