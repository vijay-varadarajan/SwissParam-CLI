# swissparam/main.py

import argparse
import signal
import time
import sys
import os
from config import CONFIG, VALID_REACTIONS, VALID_RESIDUES, VALID_TOPOLOGIES, VALID_APPROACHES, VALID_CHARM
from utils import check_server, start_parameterization, check_session, retrieve_results, cancel_session

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
