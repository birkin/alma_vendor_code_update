"""
Gets raw data for each code from Alma.
"""

import datetime, json, logging, os, pprint
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
        self.tracker_dct = None     # tracks processing
        self.raw_data_dct = None    # stores data from api-call

    def build_raw_data( self ):
        """ MANAGER. """
        self.load_tracker(); assert type(self.tracker_dct) == dict, type(self.tracker_dct)
        items = self.tracker_dct.items()
        for i, (code_key, data_val) in enumerate(items):
            log.debug( f'code_key, ``{code_key}``' )
            log.debug( f'i, ``{i}``' )
            assert type(code_key) == str
            assert type(data_val) == dict
            self.check_file_existence( code_key )  # creates file if it doesn't exist; also loads self.raw_data_dct
            ## see if raw data exists.
            raw_data_exists = self.check_code_raw_data_existence( code_key ); assert type(raw_data_exists) == bool
            if raw_data_exists:     # skip
                pass
            else:                   # If it doesn't exist, make api call
                data_for_code = self.get_raw_data( code_key ); assert type(data_for_code) == dict
                self.raw_data_dct[code_key] = data_for_code     # add it to output file
                # log.debug( f'self.raw_data_dct, ``{self.raw_data_dct}``' )
                self.save_raw_data()                            # writes to json file -- yes, lots of overhead, but safe
                self.update_tracker( code_key )
            if i > 800:             # for development-checking
                break

    def load_tracker( self ):
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        log.debug( f'tracker_path, ``{tracker_path}``' )
        tracker_dct = {}
        with open( tracker_path, encoding='utf-8' ) as tracker_fh:
            tracker_dct = json.loads( tracker_fh.read() )
            # log.debug( f'tracker_dct, ``{tracker_dct}``' )
            # log.debug( f'self.tracker_dct initially, ``{self.tracker_dct}``' )
        assert type(tracker_dct) == dict
        self.tracker_dct = tracker_dct
        log.debug( f'self.tracker_dct loaded' )
        return

    def check_file_existence( self, code ):
        """ Checks to see if output file exists, creates it if not.
            Also loads self.raw_data_dct """
        assert type(code) == str
        raw_data_path = f'{OUTPUT_DIR}/raw_code_data.json'
        if os.path.exists( raw_data_path ):
            with open( raw_data_path, encoding='utf-8' ) as raw_data_fh:
                self.raw_data_dct = json.loads( raw_data_fh.read() )
        else:
            with open( raw_data_path, 'w', encoding='utf-8' ) as raw_data_fh:  # create the `raw_code_data.json` file
                jsn = json.dumps( self.tracker_dct, sort_keys=True, indent=2 )
                raw_data_fh.write( jsn )
            log.debug( 'file did not exist; now does' )
            self.raw_data_dct = self.tracker_dct.copy()
        assert type(self.raw_data_dct) == dict
        log.debug( 'self.raw_data_dct loaded' )
        return

    def check_code_raw_data_existence( self, code_key ):
        """ Checks to see if data's already been grabbed. """
        assert type(code_key) == str
        data_val = self.raw_data_dct[code_key]
        exists = False
        if data_val == {}:
            exists = False
        else:
            # log.debug( f'data.keys, ``{self.raw_data_dct[code_key].keys()}``' )
            exists = True
        log.debug( f'data exists for code, ``{exists}``' )
        return exists

    def get_raw_data( self, code_key ):
        """ Hits acquisitions vendor api.
            Note: vendor code like `#foo` must be encoded so that api url like `https://root_url/vendor/#foo` works.
            A browser will auto-encode that url fine, but python requires explicit encoding. """
        assert type(code_key) == str
        encoded_code = parse.quote( code_key )  # turns `#foo` into `%23foo`
        url = f'{API_URL}/{encoded_code}?apikey={API_KEY}'
        log.debug( f'url, ``{url}``' )
        hdrs = {'accept': 'application/json'}
        r = requests.get( url, headers=hdrs )
        data_for_code = r.json()
        assert type(data_for_code) == dict
        data_keys = data_for_code.keys()
        if sorted(data_keys) != ['access_provider', 'account', 'code', 'contact_info', 'contact_person', 'currency', 'edi_info', 'financial_sys_code', 'governmental', 'interface', 'language', 'liable_for_vat', 'library', 'licensor', 'link', 'material_supplier', 'name', 'note', 'status']:
            log.debug( f'unusual data_keys, ``{sorted(data_keys)}``' )
            log.debug( f'data_for_code, ``{pprint.pformat(data_for_code)}``' )
        log.debug( 'raw-data grabbed' )
        return data_for_code

    def save_raw_data( self ):
        """ Saves self.raw_data_dct to json-file. """
        raw_data_path = f'{OUTPUT_DIR}/raw_code_data.json'
        with open( raw_data_path, 'w', encoding='utf-8' ) as raw_data_fh:
            jsn = json.dumps( self.raw_data_dct, sort_keys=True, indent=2 )
            raw_data_fh.write( jsn )

    def update_tracker( self, code_key ):
        """ Updates tracker. """
        assert type(code_key) == str
        self.tracker_dct[code_key]['01_initial_data_retrieved'] = str( datetime.datetime.now().isoformat() )
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        with open( tracker_path, 'w', encoding='utf-8' ) as tracker_fh:
            jsn = json.dumps( self.tracker_dct, sort_keys=True, indent=2 )
            tracker_fh.write( jsn )

    ## end class RawDataBuilder()


builder = RawDataBuilder()
builder.build_raw_data()
