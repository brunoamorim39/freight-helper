'''
Utility functions for use with the freight helper tool.
'''
import copy
import csv
import json
import math
import os
import random

import numpy as np

# Allowed extensions for manifests
ALLOWED_EXTENSIONS = {'csv', 'xslx', 'ods'}

# Set standard units for internal calculations
STANDARD_CALCULATION_UNITS = {
    'dimension': 'inches',
    'mass': 'pounds',
    'area': 'square feet'
}

# Nearest inch factor precision
GRID_PRECISION_FACTOR = 0.25

def save_truck(truck_obj):
    with open(f"./resources/trucks/{truck_obj['truck_name']}", 'w', encoding='utf-8') as truckfile:
        truckfile.write(json.dumps(truck_obj))
    return

def delete_truck(truck_obj):
    os.remove(f"./resources/trucks/{truck_obj['name']}")
    return

def unit_convert(from_unit: str, to_unit: str, val) -> float:
    '''
    Takes an object key and converts the value of it from a specific unit to a specific unit
    '''
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    val = float(val)

    # Checking if the before and after units are the same
    if from_unit == to_unit:
        return val

    # Converting linear dimensional units
    if from_unit == 'inches' and to_unit == 'feet':
        return val / 12
    if from_unit == 'feet' and to_unit == 'inches':
        return val * 12
    
    if from_unit == 'inches' and to_unit == 'millimeters':
        return val * 25.4
    if from_unit == 'millimeters' and to_unit == 'inches':
        return val / 25.4
    
    if from_unit == 'inches' and to_unit == 'meters':
        return val * 25.4 / 1000
    if from_unit == 'meters' and to_unit == 'inches':
        return val * 1000 / 25.4

    if from_unit == 'feet' and to_unit == 'millimeters':
        return val * 12 * 25.4
    if from_unit == 'millimeters' and to_unit == 'feet':
        return val / 25.4 / 12

    if from_unit == 'feet' and to_unit == 'meters':
        return val * 12 * 25.4 / 1000
    if from_unit == 'meters' and to_unit == 'feet':
        return val * 1000 / 25.4 / 12
    
    # Converting mass units
    if from_unit == 'pounds' and to_unit == 'kilograms':
        return val / 2.204
    if from_unit == 'kilograms' and to_unit == 'pounds':
        return val * 2.204

    # Converting area units
    if from_unit == 'square feet' and to_unit == 'square meters':
        return val / 10.764
    if from_unit == 'square meters' and to_unit == 'square feet':
        return val * 10.764

    raise ValueError

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

def make_manifest_map(manifest_params):
    manifest_map = {}
    for param in manifest_params:
        manifest_map[param] = {}
        manifest_map[param]['column'] = manifest_params[param]
        if f'{param}-units' in manifest_params:
            manifest_map[param]['units'] = manifest_params[f'{param}-units']
    return manifest_map

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

def get_manifest_details(manifest_name):
    manifest_details = []
    with open(f'./resources/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            manifest_details.append(row)
    return manifest_details

def format_manifest_form_data(formdata, row_to_delete=None):
    manifest_data_obj = {}
    for column in formdata:
        for idx, each in enumerate(formdata.getlist(column)):
            if f'row_{idx + 1}' not in manifest_data_obj:
                manifest_data_obj[f'row_{idx + 1}'] = {}
            manifest_data_obj[f'row_{idx + 1}'][column] = each
    
    if row_to_delete:
        del manifest_data_obj[f'row_{row_to_delete}']
    
    formatted_data = []
    for obj in manifest_data_obj:
        formatted_data.append(manifest_data_obj[obj])

    return formatted_data

def analyze_manifest(manifest_name: str, manifest_map: object) -> list:
    '''
    Analyzes the selected manifest to determine the details for the shipment for later use in optimization.
    '''
    manifest_params = get_manifest_params()
    manifest_details = []
    with open(f'./resources/manifests/{manifest_name}.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_obj = {}
            for param in manifest_params:
                row_obj[param['key']] = {}
                if manifest_map[param['key']] == 'NULL':
                    row_obj[param['key']] = None
                try:
                    row_obj[param['key']] = row[manifest_map[param['key']]['column']]
                except KeyError:
                    row_obj[param['key']] = None
            manifest_details.append(row_obj)
    return manifest_details

def update_manifest(manifest_name: str, manifest_params: object, manifest_details: list) -> None:
    manifest_fields = []
    for param in manifest_params:
        manifest_fields.append(param['key'])
    with open(f'./resources/manifests/{manifest_name}.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=manifest_fields)
        writer.writeheader()
        for row in manifest_details:
            writer.writerow(row)
    return

def save_manifest_units(manifest_name: str, manifest_map: object) -> None:
    units_fields = []
    units_obj = {}
    for param in manifest_map:
        if 'units' in manifest_map[param]:
            units_fields.append(param)
            units_obj[param] = manifest_map[param]['units']
    with open(f'./resources/manifests/{manifest_name}-units.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=units_fields)
        writer.writeheader()
        writer.writerow(units_obj)
    return

def get_manifest_units(manifest_name: str) -> object:
    with open(f'./resources/manifests/{manifest_name}-units.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            unit_map = row
    return unit_map

def check_for_complete_manifest_data(manifest_name: str) -> bool:
    manifest_details = get_manifest_details(manifest_name)
    incomplete_flag = False
    for data_row in manifest_details:
        for key in data_row:
            if not data_row[key]:
                incomplete_flag = True
    return incomplete_flag

def save_rack(rack_obj: object) -> None:
    with open(f"./resources/racks/{rack_obj['name']}", 'w', encoding='utf-8') as rackfile:
        rackfile.write(json.dumps(rack_obj))
    return

def delete_rack(rack_obj: object) -> None:
    os.remove(f"./resources/racks/{rack_obj['name']}")
    return

def prepare_types(truck_details: object, manifest_details: list) -> None:
    '''
    Ensures that all types are set properly for the truck details as well as the items in the manifest
    '''
    truck_details['distance_to_rear_axle'] = float(truck_details['distance_to_rear_axle'])
    truck_details['interior_rack_quantity'] = int(truck_details['interior_rack_quantity'])
    truck_details['exterior_rack_quantity'] = int(truck_details['exterior_rack_quantity'])
    for rack in truck_details['rack_info']['interior']:
        rack['rack_length'] = float(rack['rack_length'])
        rack['rack_depth'] = float(rack['rack_depth'])
        rack['rack_height'] = float(rack['rack_height'])
    for rack in truck_details['rack_info']['exterior']:
        rack['rack_length'] = float(rack['rack_length'])
        rack['rack_depth'] = float(rack['rack_depth'])
        rack['rack_height'] = float(rack['rack_height'])

    for item in manifest_details:
        item['stop_number'] = int(item['stop_number'])
        item['quantity'] = int(item['quantity'])
        item['weight'] = float(item['weight'])
        item['square_footage'] = float(item['square_footage'])
        item['length'] = float(item['length'])
        item['width'] = float(item['width'])
        item['thickness'] = float(item['thickness'])

def calculate_physical_space(truck_details: object, manifest_details: list, manifest_units: list) -> object:

    truck_details['total_interior_rack_volume'] = 0
    for rack in truck_details['rack_info']['interior']:
        rack['rack_length'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_length']
        )
        rack['grid_size_length_axis'] = math.floor(rack['rack_length'] / GRID_PRECISION_FACTOR)

        rack['rack_depth'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_depth']
        )
        rack['grid_size_depth_axis'] = math.floor(rack['rack_depth'] / GRID_PRECISION_FACTOR)

        rack['rack_height'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_height']
        )
        rack['grid_size_height_axis'] = math.floor(rack['rack_height'] / GRID_PRECISION_FACTOR)

        truck_details['total_interior_rack_volume'] += 2 * (
            rack['rack_length'] * 
            rack['rack_depth'] * 
            rack['rack_height']
        )

    truck_details['total_exterior_rack_volume'] = 0
    for rack in truck_details['rack_info']['exterior']:
        rack['rack_length'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_length']
        )
        rack['grid_size_length_axis'] = math.floor(rack['rack_length'] / GRID_PRECISION_FACTOR)

        rack['rack_depth'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_depth']
        )
        rack['grid_size_depth_axis'] = math.floor(rack['rack_depth'] / GRID_PRECISION_FACTOR)

        rack['rack_height'] = unit_convert(
            from_unit='feet',
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=rack['rack_height']
        )
        rack['grid_size_height_axis'] = math.floor(rack['rack_height'] / GRID_PRECISION_FACTOR)

        truck_details['total_exterior_rack_volume'] += 2 * (
            rack['rack_length'] * 
            rack['rack_depth'] * 
            rack['rack_height']
        )

    truck_details['total_cargo_volume'] = 0
    for item in manifest_details:
        item['length'] = unit_convert(
            from_unit=manifest_units['length'],
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=item['length']
        )
        item['width'] = unit_convert(
            from_unit=manifest_units['width'],
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=item['width']
        )
        item['thickness'] = unit_convert(
            from_unit=manifest_units['thickness'],
            to_unit=STANDARD_CALCULATION_UNITS['dimension'],
            val=item['thickness']
        )

        primary_dimension = item['length'] if item['length'] >= item['width'] else item['width']
        secondary_dimension = item['width'] if item['length'] >= item['width'] else item['length']
        item['grid_volume'] = {
            'horizontal': {
                'length': math.ceil(primary_dimension / GRID_PRECISION_FACTOR),
                'height': math.ceil(secondary_dimension / GRID_PRECISION_FACTOR),
                'thickness': math.ceil(item['thickness'] / GRID_PRECISION_FACTOR)
            },
            'vertical': {
                'length': math.ceil(secondary_dimension / GRID_PRECISION_FACTOR),
                'height': math.ceil(primary_dimension / GRID_PRECISION_FACTOR),
                'thickness': math.ceil(item['thickness'] / GRID_PRECISION_FACTOR)
            }
        }

        item_volume = item['quantity'] * (item['length'] * item['width'] * item['thickness'])
        truck_details['total_cargo_volume'] += item_volume
    return truck_details

def prioritize_cargo(manifest_details: list) -> list:
    prioritized_manifest_details = []

    # Sort based on stop number and create sublists for each stop
    manifest_details.sort(key=lambda x: int(x['stop_number']))
    stop_number_sublists = []
    sublist = None
    previous_stop_number = 0
    for item in manifest_details:
        if item['stop_number'] != previous_stop_number:
            if sublist:
                stop_number_sublists.append(sublist)
            sublist = []
        sublist.append(item)
        previous_stop_number = item['stop_number']
    
    # Sort each stop's sublist by descending weight and create new item entries based on the item quantity specification. Then assign a cargo ID value to each unique piece of cargo for tracking its placement.
    item_id = 1
    cargo_id = 1
    for sublist in stop_number_sublists:
        sublist.sort(key=lambda x: x['weight'], reverse=True)
        separated_quantity_sublist = []
        for item in sublist:
            item['item_id'] = item_id
            for i in range(item['quantity']):
                unique_item = item.copy()
                unique_item['cargo_id'] = cargo_id
                separated_quantity_sublist.append(unique_item)
                cargo_id += 1
            item_id += 1
        prioritized_manifest_details.extend(separated_quantity_sublist)

    return prioritized_manifest_details

def generate_color_palette(manifest_details: list) -> object:
    '''
    Based on the items in the cargo manifest, generate and assign random colors to each item so that they can be represented on the UI
    '''
    def pick_random_color(color_palette: object) -> tuple:
        '''
        Create a tuple for a random RGB color code. Then, check it against the already existing colors in the palette thus far. If the color already exists, then we will try to create a new color until one that is not a match is found
        '''
        random_rgb_color = tuple(random.choices(range(256), k=3))
        for item in color_palette:
            if random_rgb_color == color_palette[item]['color']:
                return pick_random_color(color_palette)
        return random_rgb_color

    # Generate a random color to assign to each of the cargo IDs for items and ensure that they are not the same as any other colors
    color_palette = {}
    for i in range(len(manifest_details)):
        color_palette[i + 1] = {
            'cargo_id': manifest_details[i]['cargo_id'],
            'color': pick_random_color(color_palette)
        }
    return color_palette

def prepare_cargo_map_blank(truck_details: object) -> object:
    '''
    The cargo map blank is created in such a way that all empty space is indicated by a '0' value. And nonzero values indicate the cargo ID of the item that is occupying that space. Numpy 3D arrays are used to map out the space on each of the racks. These arrays are set up in a sort of 'stacked' view, as if you were looking straight on towards the rack while placing a panel on there yourself. What this means, is that the depth axis of the rack grids represent the 'stacking' of the arrays, while the height axis represents the quantity of rows present in each of the 'stacks' and the length axis represents the number of columns. This representation looks similar to the following example:

    length  - 5 grid places
    height  - 2 grid places
    depth   - 3 grid places

    [[[0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.]],    This 'stack', being the first one, would represent the bottom layer of the rack, with the top being the front of the truck
        
     [[0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.],
      [0., 0., 0.]]]
    '''
    cargo_map_blank = {}

    for sector in truck_details['rack_info']:
        cargo_map_blank[sector] = {
            'left': {
                'weight': 0,
                'racks': []
            },
            'right': {
                'weight': 0,
                'racks': []
            }
        }
        for rack_definintion in truck_details['rack_info'][sector]:
            for side in cargo_map_blank[sector]:
                cargo_map_blank[sector][side]['racks'].append(
                    {
                        'weight': 0,
                        'map': np.zeros(
                            (
                                rack_definintion['grid_size_height_axis'],
                                rack_definintion['grid_size_length_axis'],
                                rack_definintion['grid_size_depth_axis']
                            )
                        )
                    }
                )

    return cargo_map_blank

def get_empty_space_for_placement(cargo_map: object, line_item: object, rack_to_place_on: object) -> object:
    def set_placement_coordinates_obj_values(placement_coordinates_obj: object, length_layer: int, depth_layer: int) -> None:
        placement_coordinates_obj['length_axis']['start_index'] = length_layer
        placement_coordinates_obj['length_axis']['end_index'] = line_item['grid_volume'][rack_to_place_on['orientation']]['length'] + length_layer

        placement_coordinates_obj['height_axis']['start_index'] = 0
        placement_coordinates_obj['height_axis']['end_index'] = line_item['grid_volume'][rack_to_place_on['orientation']]['height']

        placement_coordinates_obj['depth_axis']['start_index'] = depth_layer
        placement_coordinates_obj['depth_axis']['end_index'] = line_item['grid_volume'][rack_to_place_on['orientation']]['thickness'] + depth_layer

    placement_coordinates_obj = {
        'length_axis': {
            'start_index': None,
            'end_index': None
        },
        'height_axis': {
            'start_index': None,
            'end_index': None
        },
        'depth_axis': {
            'start_index': None,
            'end_index': None
        }
    }
    for rack in cargo_map[rack_to_place_on['sector']][rack_to_place_on['side']]['racks']:
        rack_map = rack['map']
        for depth_layer in range(rack_map.shape[2] - line_item['grid_volume'][rack_to_place_on['orientation']]['thickness']):
            for length_layer in range(rack_map.shape[1] - line_item['grid_volume'][rack_to_place_on['orientation']]['length']):
                submatrix = rack_map[
                    0 : line_item['grid_volume'][rack_to_place_on['orientation']]['height'],
                    length_layer : line_item['grid_volume'][rack_to_place_on['orientation']]['length'] + length_layer,
                    depth_layer : line_item['grid_volume'][rack_to_place_on['orientation']]['thickness'] + depth_layer
                ]
                
                if not submatrix.any():
                    set_placement_coordinates_obj_values(placement_coordinates_obj, length_layer, depth_layer)
                    print(f"\n{line_item['cargo_id']}")
                    print(rack_to_place_on)
                    print(placement_coordinates_obj)
                    break
            else:
                continue
            break
    
    return placement_coordinates_obj

def modify_cargo_array(cargo_map: object, line_item: object, rack_to_place_on: object, placement_coordinate_set: object) -> None:
    cargo_map[rack_to_place_on['sector']][rack_to_place_on['side']]['racks'][rack_to_place_on['rack_index']]['map'][
        placement_coordinate_set['height_axis']['start_index'] : placement_coordinate_set['height_axis']['end_index'],
        placement_coordinate_set['length_axis']['start_index'] : placement_coordinate_set['length_axis']['end_index'],
        placement_coordinate_set['depth_axis']['start_index'] : placement_coordinate_set['depth_axis']['end_index']
    ] = line_item['cargo_id']

def place_cargo(truck_details: object, manifest_details: list, cargo_map_blank: object) -> object:
    DEFAULT_STARTING_SECTOR = 'interior'
    DEFAULT_STARTING_SIDE = 'left'
    DEFAULT_STARTING_INDEX = 0

    def get_least_weights(cargo_map: object, sector: str) -> object:
        '''
        Determines the side and rack with the least amount of weight on it for a given sector
        '''
        least_weight_map = {
            'sector': None,
            'side': None,
            'rack_index': None
        }

        side_weights = {}
        for side in cargo_map[sector]:
            side_weights[side] = cargo_map[sector][side]['weight']
        lightest_side = min(side_weights, key=lambda x: side_weights[x])

        rack_weights = {}
        for idx, rack in enumerate(cargo_map[sector][lightest_side]['racks']):
            rack_weights[idx] = rack['weight']
        lightest_rack = min(rack_weights, key=lambda x: rack_weights[x])
            
        least_weight_map['sector'] = sector
        least_weight_map['side'] = lightest_side
        least_weight_map['rack_index'] = lightest_rack

        return least_weight_map

    def get_item_orientation(truck_details: object, item: object, rack_to_place_on: object) -> str:
        '''
        Simple calculation to determine what the orientation of the item being placed should be
        '''
        if (
            item['grid_volume']['vertical']['height'] < 
            truck_details['rack_info'][rack_to_place_on['sector']][rack_to_place_on['rack_index']]['grid_size_height_axis']
        ):
            return'vertical'
        return 'horizontal'

    def eligible_for_rack(cargo_map: object, line_item: object, rack_to_place_on: object) -> object:
        '''
        Determines whether the item is elgibible to even be placed on the rack based on its size as well as the available space on the rack
        '''
        placement_coordinate_set = get_empty_space_for_placement(cargo_map, line_item, rack_to_place_on)
        for axis in placement_coordinate_set:
            if placement_coordinate_set[axis]['start_index'] == None or placement_coordinate_set[axis]['end_index'] == None:
                return False
        return True

    cargo_map = cargo_map_blank.copy()

    item_id_of_last_placed = None
    rack_last_placed_on = None

    for item_idx, line_item in enumerate(manifest_details):
        rack_to_place_on = {
            'sector': None,
            'side': None,
            'rack_index': None,
            'orientation': None
        }

        if item_idx == 0:
            rack_to_place_on['sector'] = DEFAULT_STARTING_SECTOR
            rack_to_place_on['side'] = DEFAULT_STARTING_SIDE
            rack_to_place_on['rack_index'] = DEFAULT_STARTING_INDEX
            rack_to_place_on['orientation'] = get_item_orientation(truck_details, line_item, rack_to_place_on)
        elif line_item['item_id'] == item_id_of_last_placed:
            # If the item is the same item as the last that was placed, allow the item to be placed on the same rack
            rack_to_place_on = rack_last_placed_on
        else:
            for sector in cargo_map:
                least_weight_map = get_least_weights(cargo_map, sector)
                for side in cargo_map[sector]:
                    # Only load items onto the sector and side that have the least weight loaded onto them
                    if (
                        cargo_map[sector][side]['weight'] <=
                        cargo_map[least_weight_map['sector']][least_weight_map['side']]['weight']
                    ):
                        rack_to_place_on['sector'] = least_weight_map['sector'] = sector
                        rack_to_place_on['side'] = least_weight_map['side'] = side

                        # Check the racks within the sector and side defined to determine which has the least weight and determine item orientation
                        for rack_idx, rack in enumerate(cargo_map[sector][side]['racks']):
                            if (
                                rack['weight'] <=
                                cargo_map[sector][side]['racks'][least_weight_map['rack_index']]['weight']
                            ):
                                rack_to_place_on['rack_index'] = least_weight_map['rack_index'] = rack_idx
                                rack_to_place_on['orientation'] = get_item_orientation(truck_details, line_item, rack_to_place_on)
                                if eligible_for_rack(cargo_map, line_item, rack_to_place_on):
                                    break
                        else:
                            continue
                        break
                else:
                    continue
                break
                                    
        placement_coordinate_set = get_empty_space_for_placement(cargo_map, line_item, rack_to_place_on)
        modify_cargo_array(cargo_map, line_item, rack_to_place_on, placement_coordinate_set)

        cargo_map[rack_to_place_on['sector']][rack_to_place_on['side']]['weight'] += line_item['weight']
        cargo_map[rack_to_place_on['sector']][rack_to_place_on['side']]['racks'][rack_to_place_on['rack_index']]['weight'] += line_item['weight']

        item_id_of_last_placed = line_item['item_id']
        rack_last_placed_on = rack_to_place_on

        # Solely for testing
        if item_idx == 5:
            break
    
    # TODO: Continue building flipping rules for other sides and sectors of the truck layout
    # Handle the appropriate flipping of arrays based on their location
    for sector in cargo_map:
        for side in cargo_map[sector]:
            if sector == 'interior' and side == 'right':
                for idx, rack in enumerate(cargo_map[sector][side]['racks']):
                        cargo_map[sector][side]['racks'][idx]['map'] = np.flip(cargo_map[sector][side]['racks'][idx]['map'], 2)

    return cargo_map

def flatten_map(cargo_map: object) -> object:
    master_flat_map = cargo_map.copy()

    for sector in cargo_map:
        for side in cargo_map[sector]:
            for idx, rack in enumerate(cargo_map[sector][side]['racks']):
                master_flat_map[sector][side]['racks'][idx]['map'] = rack['map'][0].tolist()

    return master_flat_map

def generate_shipment_plan(truck_details: object, manifest_name: str, manifest_details: list, manifest_units: list):    
    # Ensure that types are correct for calculations
    prepare_types(truck_details, manifest_details)

    # Calculation of grid sizes and volumes
    truck_details = calculate_physical_space(truck_details, manifest_details, manifest_units)

    # Prioritization of cargo based on manifest details
    prioritized_manifest_details = prioritize_cargo(manifest_details)
    color_palette = generate_color_palette(prioritized_manifest_details)

    cargo_map_blank = prepare_cargo_map_blank(truck_details)

    cargo_placement_map = place_cargo(truck_details, prioritized_manifest_details, cargo_map_blank)
    flattened_map = flatten_map(cargo_placement_map)

    return {
        'truck_details': truck_details,
        'manifest_details': {
            'name': manifest_name, 
            'items': prioritized_manifest_details
        },
        'color_palette': color_palette,
        'flattened_map': flattened_map
    }

