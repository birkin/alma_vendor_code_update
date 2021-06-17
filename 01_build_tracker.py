"""
Builds dct for tracking work
"""

import json, logging, os

## setup
SOURCE_FILEPATH = os.environ[ 'ALMA_VENDOR__SOURCE_FILEPATH' ]
OUTPUT_DIR = os.environ[ 'ALMA_VENDOR__OUTPUT_DIRPATH' ]
assert OUTPUT_DIR[-1] != '/'

logging.basicConfig(
    # filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)

## read in data
data = ''
with open( SOURCE_FILEPATH, encoding='utf-8' ) as src_fh:
    data = src_fh.read()

## make list
codes = data.split( ',' )
log.debug( f'codes, ``{codes}``' )
assert type(codes) == list, type(codes)
assert len(codes) > 5, len(codes)

## create dct
dct = {}
for code in codes:
    # log.debug( f'code, ``{code}``' )
    dct[code] = {}

## write json output
output_path = f'{OUTPUT_DIR}/tracker.json'
with open( output_path, 'w', encoding='utf-8' ) as output_fh:
    jsn = json.dumps( dct, sort_keys=True, indent=2 )
    output_fh.write( jsn )
