'''
- based on <https://www.geeksforgeeks.org/convert-csv-to-json-using-python/>.
- turns out not needed cuz the csv is just a list of codes.
'''

import csv, json, os


SOURCE_DIR = os.environ[ ALMA_VENDOR__SOURCE_DIR_PATH ]
OUTPUT_DIR = os.environ[ ALMA_VENDOR__OUTPUT_JSON_PATH ]
assert SOURCE_PATH[-1] != '/'

source_path = f'{SOURCE_PATH}/vendors_to_update.csv'
output_path = f'{OUTPUT_DIR}/vendors_to_update.json'


def make_json(csv_filepath, json_filepath):
    data = {}
    with open( csv_filepath, encoding='utf-8' ) as csvf:
        csvReader = csv.DictReader( csvf )
        ## Convert each row into a dictionary and add it to data
        for rows in csvReader:
            key = rows['No']
            data[key] = rows
    with open( json_filepath, 'w', encoding='utf-8' ) as jsonf:
        jsonf.write( json.dumps(data, indent=2) )

make_json(SOURCE_PATH, OUTPUT_PATH)
