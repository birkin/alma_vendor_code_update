"""
Updates financial_sys_code in json file.
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


class AlmaUpdater():

    def __init__( self ):
        self.tracker_dct = None         # tracks processing
        self.updated_data_dct = None    # stores updated data

    def update_alma( self ):
        """ MANAGER. """
        self.load_tracker(); assert type(self.tracker_dct) == dict
        self.load_updated_data_dct(); assert type(self.updated_data_dct) == dict
        tracker_items = self.tracker_dct.items()
        for i, (code_key, data_val) in enumerate(tracker_items):
            log.debug( f'i, ``{i}``' )
            log.debug( f'code_key, ``{code_key}``' )
            log.debug( f'data_val, ``{data_val}``' )
            assert type(i) == int
            assert type(code_key) == str
            assert type(data_val) == dict
            alma_already_updated = self.check_alma_updated( code_key, data_val )  # alma already update?
            assert type(alma_already_updated) == bool
            if alma_already_updated == False:
                self.send_put_to_alma( code_key )
                self.update_tracker( code_key)
            if i >= 800:                   # for development-checking
                break
        return

    def load_tracker( self ):
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        log.debug( f'tracker_path, ``{tracker_path}``' )
        tracker_dct = {}
        with open( tracker_path, encoding='utf-8' ) as tracker_fh:
            tracker_dct = json.loads( tracker_fh.read() )
        assert type(tracker_dct) == dict
        self.tracker_dct = tracker_dct
        log.debug( 'self.tracker_dct loaded' )
        return

    def load_updated_data_dct( self ):
        updated_data_path = f'{OUTPUT_DIR}/updated_data.json'
        log.debug( f'updated_data_path, ``{updated_data_path}``' )
        updated_data_dct = {}
        with open( updated_data_path, encoding='utf-8' ) as updated_data_fh:
            updated_data_dct = json.loads( updated_data_fh.read() )
        assert type(updated_data_dct) == dict
        self.updated_data_dct = updated_data_dct
        log.debug( 'self.updated_data_dct loaded' )
        return

    def check_alma_updated( self, code_key, data_val ):
        assert type(code_key) == str
        assert type(data_val) == dict
        alma_updated = data_val.get( '03_alma_updated', False )
        assert type(alma_updated) in [str, bool]
        if alma_updated:
            log.debug( f'alma already updated for code, ``{code_key}``' )
            return_val = True
        else:
            return_val = False
        log.debug( f'already-updated return-val, ``{return_val}``' )
        return return_val

    def send_put_to_alma( self, code_key ):
        assert type(code_key) == str
        encoded_code = parse.quote( code_key ); assert type(encoded_code) == str  # turns `#foo` into `%23foo`
        payload_dct = self.updated_data_dct[code_key]; assert type(payload_dct) == dict
        url = f'{API_URL}/{encoded_code}?apikey={API_KEY}'
        log.debug( f'url, ``{url}``' )
        hdrs = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
            }
        r = requests.put( url, headers=hdrs, json=payload_dct )
        log.debug( f'r.content, ``{r.content}``' )
        log.debug( f'r.status_code, ``{r.status_code}``')
        if r.status_code != 200:
            raise Exception( 'PROBLEM!' )
        return

    def update_tracker( self, code_key ):
        """ Updates tracker. """
        assert type(code_key) == str
        self.tracker_dct[code_key]['03_alma_updated'] = str( datetime.datetime.now().isoformat() )
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        with open( tracker_path, 'w', encoding='utf-8' ) as tracker_fh:
            jsn = json.dumps( self.tracker_dct, sort_keys=True, indent=2 )
            tracker_fh.write( jsn )

    ## end class AlmaUpdater()


updater = AlmaUpdater()
updater.update_alma()
