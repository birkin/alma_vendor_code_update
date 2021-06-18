"""
Updates financial_sys_code in json file.
"""

import datetime, json, logging, os, pprint
from urllib import parse

import requests

## setup
OUTPUT_DIR = os.environ[ 'ALMA_VENDOR__OUTPUT_DIRPATH' ]
assert OUTPUT_DIR[-1] != '/'    # no ending '/' in dir-path

logging.basicConfig(
    # filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)


class JsonUpdater():

    def __init__( self ):
        self.tracker_dct = None         # tracks processing
        self.updated_data_dct = None    # stores updated data

    def update_financial_sys_code( self ):
        """ MANAGER. """
        self.load_tracker(); assert type(self.tracker_dct) == dict, type(self.tracker_dct)
        self.check_file_existence()  # creates file if it doesn't exist; also loads self.updated_data_dct
        items = self.tracker_dct.items()
        for i, (code_key, data_val) in enumerate(items):
            log.debug( f'code_key, ``{code_key}``' )
            log.debug( f'i, ``{i}``' )
            assert type(code_key) == str
            assert type(i) == int
            check_result = self.check_financial_sys_code( code_key )  # check financial_sys_code
            assert check_result in ['not_updated', 'updated']
            if check_result == 'updated':
                self.save_updated_data()
                self.update_tracker( code_key )
            if i > 5:                   # for development-checking
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

    def check_file_existence( self ):
        """ Checks to see if output file exists; creates it if not.
            Also loads self.updated_data_dct """
        updated_data_path = f'{OUTPUT_DIR}/updated_data.json'
        if os.path.exists( updated_data_path ):
            log.debug( '`updated_data.json` file exists' )
        else:
            raw_data_path = f'{OUTPUT_DIR}/raw_code_data.json'
            log.debug( f'raw_data_path, ``{raw_data_path}``' )
            raw_data_jsn = ''
            with open( raw_data_path, encoding='utf-8' ) as raw_data_fh:                    # load the `raw_code_data.json` file...
                raw_data_jsn = raw_data_fh.read()
                assert type(raw_data_jsn) == str
                with open( updated_data_path, 'w', encoding='utf-8' ) as updated_data_fh:   # ...& use it to create the `updated_data.json` file.
                    updated_data_fh.write( raw_data_jsn )
            log.debug( '`updated_data.json` file did not exist; now does' )
        with open( updated_data_path, encoding='utf-8' ) as updated_data_fh_B:  # load self.updated_data_dct
            updated_data_jsn = updated_data_fh_B.read()
            self.updated_data_dct = json.loads( updated_data_jsn )
            assert type( self.updated_data_dct ) == dict
        log.debug( 'self.updated_data_dct loaded' )
        return

    def check_financial_sys_code( self, code ):
        """ Checks financial_sys_code and updates it if needed. """
        assert type(code) == str
        return_val = ''
        initial_financial_sys_code = self.updated_data_dct[code]['financial_sys_code']
        assert type(initial_financial_sys_code) == str
        log.debug( f'initial financial_sys_code, ``{initial_financial_sys_code}``' )
        if initial_financial_sys_code[0:1] == 'S':
            return_val = 'not_updated'
            log.debug( 'financial_sys_code good' )
        else:  # update financial_sys_code
            updated_financial_sys_code = f'S{initial_financial_sys_code}'
            assert type(updated_financial_sys_code) == str
            log.debug( f'initial_financial_sys_code updated to, ``{updated_financial_sys_code}``' )
            self.updated_data_dct[code]['financial_sys_code'] = updated_financial_sys_code
            return_val = 'updated'
        log.debug( f'return_val, ``{return_val}``' )
        return return_val

    def save_updated_data( self ):
        """ Saves self.updated_data_dct to json-file. """
        updated_data_path = f'{OUTPUT_DIR}/updated_data.json'
        with open( updated_data_path, 'w', encoding='utf-8' ) as updated_data_fh:
            jsn = json.dumps( self.updated_data_dct, sort_keys=True, indent=2 )
            updated_data_fh.write( jsn )

    def update_tracker( self, code_key ):
        """ Updates tracker. """
        assert type(code_key) == str
        self.tracker_dct[code_key]['02_financial_sys_code_updated'] = str( datetime.datetime.now().isoformat() )
        tracker_path = f'{OUTPUT_DIR}/tracker.json'
        with open( tracker_path, 'w', encoding='utf-8' ) as tracker_fh:
            jsn = json.dumps( self.tracker_dct, sort_keys=True, indent=2 )
            tracker_fh.write( jsn )

    ## end class JsonUpdater()


updater = JsonUpdater()
updater.update_financial_sys_code()
