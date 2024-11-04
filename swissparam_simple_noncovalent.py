'''
Documentation:

    This script is allows you to use the SwissParam web service to parameterize a molecule. It takes a molecule file (.mol2) as input and sends it to the SwissParam server for parameterization. It returns as output a tar.gz file containing the parameterized molecule.
    
    - A post request is sent to the SwissParam server with the molecule file and the desired parameters. 
    - The session number is retrieved from the response
    - Status of the session is checked at regular intervals (5 seconds by default)
    - Once the session is finished, the results are downloaded and saved as 'results.tar.gz'
    
    Usage:
        python swissparam_simple_noncovalent.py -f molecule.mol2 [--hydrogen {yes / no}]
    
        -f, --filename: Path to the molecule file (.mol2). This is a required argument.
        -y, --hydrogen: [Default: no] Include hydrogen atoms (only for non-covalent). If your Mol2 file does not contain hydrogens, you can set this option to 'yes', it will protonate the molecule at pH 7.4.
        
    Approach is set to mmff-based by default
    Charmm c27 is used by default
'''


# in-built libraries
import argparse
import time
import sys
import os
import logging


# third-party libraries
import requests


# config
CONFIG = {
    'base_url': "http://swissparam.ch:5678",
    'poll_interval': 5,
    'result_filename': 'results.tar.gz'
}


# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# check if server is reachable
def check_server(base_url: str) -> bool:
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        logger.info(" Server is reachable.")
        return True
    except requests.RequestException as e:
        logger.error(f" Error connecting to server: {e}")
        return False


# obtain parameters and send request to server
def start_parameterization(base_url: str, mol2_file: str, **kwargs) -> str:
    url = f"{base_url}/startparam"
    
    with open(mol2_file, 'rb') as f:
        files = {'myMol2': f}
        
        params = {
            'approach': 'mmff-based',
        }
        
        add_hydrogen = False        
        if kwargs.get('hydrogen') == 'yes':
            add_hydrogen = True
            
        charmm = 'c27'
        
        url += f"?approach={params['approach']}{'&addH' if add_hydrogen else ''}&{charmm}" 
        
        response = requests.post(url, files=files)
        print(response.text)
        response.raise_for_status()
        
        session_number = response.text.split("=")[-1].strip().rstrip('"')
        logger.info(f" Parameterization started. Session number: {session_number}")
        return session_number


# check the status of a session
def check_session(base_url: str, session_number: str) -> str:
    response = requests.get(f"{base_url}/checksession", 
                          params={'sessionNumber': session_number})
    response.raise_for_status()
    return response.text


# download and save the results
def retrieve_results(base_url: str, session_number: str, filename: str) -> None:
    response = requests.get(f"{base_url}/retrievesession", params={'sessionNumber': session_number})
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        f.write(response.content)
    logger.info(f" Results downloaded as {filename}.")
    

# create and configure argument parser
def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="SwissParam Parameterization Script")
    parser.add_argument('-f', '--filename', required=True, help="Molecule file (.mol2) path.")
    parser.add_argument('-y', '--hydrogen', choices=['yes', 'no'], help="Include hydrogen atoms (only for non-covalent).")
    return parser


# check if arguments are valid
def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if not os.path.isfile(args.filename):
        print(f"The file '{args.filename}' does not exist.")
        sys.exit(1)
        

# main function
def main():
    parser = create_parser()
    args = parser.parse_args()
    validate_args(args)
    
    if not check_server(CONFIG['base_url']):
        sys.exit(1)
    
    session_number = start_parameterization(CONFIG['base_url'], args.filename, hydrogen=args.hydrogen)
    
    while True:
        status = check_session(CONFIG['base_url'], session_number)
        logger.info(f" Session {session_number} status: {status}")
        
        if "finished" in status:
            retrieve_results(CONFIG['base_url'], session_number, CONFIG['result_filename'])
            break
        
        time.sleep(CONFIG['poll_interval'])
        

if __name__ == "__main__":
    main()