# in-built libraries
import argparse
import signal
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
            'hydrogen': kwargs.get('hydrogen', 'yes')
        }
        data = {'charm': 'c27'}

        response = requests.post(url, files=files, params=params, data=data)
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