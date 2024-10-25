# swissparam/config.py

# Configuration as a simple dict
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
