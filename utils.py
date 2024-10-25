# swissparam/utils.py

import requests
import os
import logging
from typing import Dict, Any

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_server(base_url: str) -> bool:
    """Check if the server is accessible."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        logger.info("Server is reachable.")
        return True
    except requests.RequestException as e:
        logger.error(f"Error connecting to server: {e}")
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
        logger.info(f"Parameterization started. Session number: {session_number}")
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
    logger.info(f"Results downloaded as {filename}.")


def cancel_session(base_url: str, session_number: str) -> None:
    """Cancel the parameterization session."""
    response = requests.get(f"{base_url}/cancelsession", 
                          params={'sessionNumber': session_number})
    response.raise_for_status()
    logger.info(f"Session {session_number} cancelled.")
