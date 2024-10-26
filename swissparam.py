# swissparam/main.py

import argparse
import signal
import time
import sys
import os
import requests
import logging
from typing import Dict, Any


CONFIG = {
    'base_url': "http://swissparam.ch:5678",
    'poll_interval': 5,
    'result_filename': 'results.tar.gz'
}

# Constants as sets for faster lookup
VALID_REACTIONS = {
    'aziridine_open', 'blac_open', 'carbonyl_add', 'disulf_form', 
    'epoxide_open', 'glac_open', 'imine_form', 'michael_add', 
    'nitrile_add', 'nucl_subst'
}
VALID_RESIDUES = {'CYS', 'SER', 'THR', 'LYS', 'TYR', 'ASP', 'GLU'}
VALID_TOPOLOGIES = {'post-cap', 'pre'}
VALID_APPROACHES = {'both', 'mmff-based', 'match'}
VALID_CHARM = {'c22', 'c27'}


# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_server(base_url: str) -> bool:
    """Check if the server is accessible."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        logger.info(" Server is reachable.")
        return True
    except requests.RequestException as e:
        logger.error(f" Error connecting to server: {e}")
        return False


def start_parameterization(base_url: str, is_covalent: bool, mol2_file: str, **kwargs) -> str:
    """Start parameterization process and return session number."""
    url = f"{base_url}/startparam"
    
    with open(mol2_file, 'rb') as f:
        files = {'myMol2': f}
        
        if is_covalent:
            params = {
                'ligsite': kwargs.get('ligand'),
                'reaction': kwargs.get('reaction'),
                'protres': kwargs.get('protres'),
                'topology': kwargs.get('topology', 'post-cap'),
                'delete': kwargs.get('delete_atoms')
            }
            data = {'charm': kwargs.get('charm')}
        else:
            params = {
                'approach': kwargs.get('approach', 'both'),
                'hydrogen': kwargs.get('hydrogen', 'yes')
            }
            data = {}

        response = requests.post(url, files=files, params=params, data=data)
        response.raise_for_status()
        session_number = response.text.split("=")[-1].strip().rstrip('"')
        logger.info(f" Parameterization started. Session number: {session_number}")
        return session_number


def check_session(base_url: str, session_number: str) -> str:
    """Check the status of a parameterization session."""
    response = requests.get(f"{base_url}/checksession", 
                          params={'sessionNumber': session_number})
    response.raise_for_status()
    return response.text


def retrieve_results(base_url: str, session_number: str, filename: str) -> None:
    """Download and save the results."""
    response = requests.get(f"{base_url}/retrievesession", 
                          params={'sessionNumber': session_number})
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        f.write(response.content)
    logger.info(f" Results downloaded as {filename}.")


def cancel_session(base_url: str, session_number: str) -> None:
    """Cancel the parameterization session."""
    response = requests.get(f"{base_url}/cancelsession", 
                          params={'sessionNumber': session_number})
    response.raise_for_status()
    logger.info(f" Session {session_number} cancelled.")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="SwissParam Parameterization Script")
    parser.add_argument('-c', '--covalent', required=True, 
                       choices=['covalent', 'non-covalent'], help="Specify 'covalent' or 'non-covalent' parameterization.")
    parser.add_argument('-f', '--filename', required=True, help="Molecule file (.mol2) path.")
    parser.add_argument('-a', '--approach', choices=VALID_APPROACHES, 
                        help="Specify approach (only for non-covalent).")
    parser.add_argument('-y', '--hydrogen', choices=['yes', 'no'], help="Include hydrogen atoms (only for non-covalent).")
    parser.add_argument('-l', '--ligand', help="Ligand site (only for covalent).")
    parser.add_argument('-r', '--reaction', choices=VALID_REACTIONS, help="Reaction (only for covalent).")
    parser.add_argument('-p', '--protres', choices=VALID_RESIDUES, help="Protein residue (only for covalent).")
    parser.add_argument('-t', '--topology', choices=VALID_TOPOLOGIES, default='post-cap', help="Topology type (default: post-cap).")
    parser.add_argument('-m', '--charm', choices=VALID_CHARM, help="CHAMM parameter set.")
    parser.add_argument('-d', '--delete_atoms', help="Specify atoms to delete.")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if not os.path.isfile(args.filename):
        print(f"The file '{args.filename}' does not exist.")
        sys.exit(1)

    if args.covalent == 'covalent':
        if not all([args.ligand, args.reaction, args.protres]):
            print("For covalent parameterization, -l (ligand), -r (reaction), and -p (protres) must be provided.")
            sys.exit(1)


def main() -> None:
    """Main execution function."""
    args = create_parser().parse_args()
    validate_args(args)

    if not check_server(CONFIG['base_url']):
        sys.exit("Error: Server is not reachable.")

    # Start parameterization
    is_covalent = args.covalent == 'covalent'
    params = vars(args)
    session_number = start_parameterization(
        CONFIG['base_url'], 
        is_covalent, 
        args.filename, 
        **params
    )

    # Signal handler for Control+C
    def signal_handler(sig, frame):
        print("Control+C detected. Cancelling session...")
        cancel_session(CONFIG['base_url'], session_number)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Poll for completion
    while True:
        status = check_session(CONFIG['base_url'], session_number)
        print(status)

        if "finished" in status:
            break
        if "in the queue" in status or "running" in status:
            time.sleep(CONFIG['poll_interval'])
            continue
        print("Unable to compute results.")
        sys.exit(1)

    # Retrieve results
    print("Retrieving results...")
    retrieve_results(CONFIG['base_url'], session_number, CONFIG['result_filename'])


if __name__ == "__main__":
    main()
