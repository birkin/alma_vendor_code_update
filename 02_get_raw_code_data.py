"""
Gets raw data for each code from Alma.
"""

import json, logging, os, pprint
from urllib import parse

import requests

## setup
OUTPUT_DIR = os.environ[ 'ALMA_VENDOR__OUTPUT_DIRPATH' ]
assert OUTPUT_DIR[-1] != '/'    # no ending '/' in dir-path
API_URL = os.environ[ 'ALMA_VENDOR__API_URL_ROOT' ]
assert API_URL[-1] != '/'       # no ending '/' in api-url-root
API_KEY = os.environ[ 'ALMA_VENDOR__API_KEY' ]

logging.basicConfig(
    # filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)


class RawDataBuilder( object ):

    def __init__( self ):
        self.tracker_dct = None

    def build_raw_data( self ):
        """ Manager. """
        self.load_tracker(); assert type(self.tracker_dct) == dict, type(self.tracker_dct)
        items = self.tracker_dct.items()
        for code_key, data_val in items:
            log.debug( f'code_key, ``{code_key}``' )
            assert type(code_key) == str
            assert type(data_val) == dict
            self.check_file_existence( code_key )
            ## see if raw data exists.
            raw_data_exists = self.check_code_raw_data_existence( code_key, data_val ); assert type(raw_data_exists) == bool
            if raw_data_exists:
                continue
            else:  # If not...
                ## get raw data
                raw_data = self.get_raw_data( code_key ); assert type(raw_data) == dict
                ## add it to output file
                self.tracker_dct[code_key] = raw_data
                ## save output file
                self.save_data()
                ## update tracker
                self.update_tracker( code_key )
            break

    def load_tracker( self ):
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        log.debug( f'tracker_path, ``{tracker_path}``' )
        tracker_dct = {}
        with open( tracker_path, encoding='utf-8' ) as tracker_fh:
            tracker_dct = json.loads( tracker_fh.read() )
            # log.debug( f'tracker_dct, ``{tracker_dct}``' )
            # log.debug( f'self.tracker_dct initially, ``{self.tracker_dct}``' )
        self.tracker_dct = tracker_dct
        # log.debug( f'self.tracker_dct now, ``{self.tracker_dct}``' )
        return

    def check_file_existence( self, code ):
        """ Checks to see if output file exists, creates it if not. """
        assert type(code) == str
        raw_data_path = f'{OUTPUT_DIR}/raw_code_data.json'
        if os.path.exists( raw_data_path ):
            log.debug( 'file exists' )
        else:
            output_path = f'{OUTPUT_DIR}/raw_code_data.json'
            with open( output_path, 'w', encoding='utf-8' ) as output_fh:
                jsn = json.dumps( self.tracker_dct, sort_keys=True, indent=2 )
                output_fh.write( jsn )
            log.debug( 'file did not exist; now does' )

    def check_code_raw_data_existence( self, code_key, data_val ):
        """ Checks to see if data's already been grabbed. """
        assert type(code_key) == str
        assert type(data_val) == dict
        exists = False
        if data_val == {}:
            exists = False
        else:
            log.debug( f'data.keys, ``{sort( self.tracker_dct["code_key"].keys() )}``' )
            exists = True
        log.debug( f'exists, ``{exists}``' )
        return exists

    def get_raw_data( self, code_key ):
        """ Hits api. """
        assert type(code_key) == str
        log.debug( f'api-key, ``{API_KEY}``' )
        encoded_code = parse.quote( code_key )
        log.debug( f'encoded_code, ``{encoded_code}``' )
        url = f'{API_URL}/{encoded_code}?apikey={API_KEY}'
        log.debug( f'url, ``{url}``' )
        hdrs = {'accept': 'application/json'}
        log.debug( f'hdrs, ``{hdrs}``' )
        r = requests.get( url, headers=hdrs )
        # log.debug( f'r.content, ``{r.content}``' )
        jdct = r.json()
        log.debug( f'jdct, ``{pprint.pformat(jdct)}``' )
        return jdct

    ## end class RawDataBuilder()


builder = RawDataBuilder()
builder.build_raw_data()
