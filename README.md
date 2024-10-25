# Swissparam

### [http://www.swissparam.ch/command-line.php](http://www.swissparam.ch/command-line.php)

## Overview

The `swissparam.py` script is a command-line utility for parameterizing small molecules using the SwissParam web service. It supports both covalent and non-covalent parameterization approaches, allowing users to obtain molecular parameters for various applications in computational chemistry, molecular modeling, and drug design.

## Features

- Supports covalent and non-covalent parameterization.
- Validates input parameters to ensure compatibility.
- Checks server status and session management.
- Retrieves parameterization results and saves them to a specified file.
- Handles user interruptions gracefully with cancellation options.

## Requirements

- Internet connection
- Python 3.x
- `requests` library
- `argparse` library (included in Python's standard library)
- `os` library (included in Python's standard library)
- `sys` library (included in Python's standard library)
- `time` library (included in Python's standard library)
- `signal` library (included in Python's standard library)
- `logging` library (included in Python's standard library)
- accompanying `utils.py` file and `config.py` file

You can install the required library using pip:

```bash
pip install requests
```

## Usage

To run the script, use the following command format:

```bash
python swissparam.py -c <covalent/non-covalent> -f <filename> -a <approach> [-h <True/False>] -l <ligand> -r <reaction> -p <protres> [-t <topology>] [-m <charm>] [-d <delete_atoms>]
```

### Command Line Arguments

- `-c`, `--covalent`: (Required) Specify whether the parameterization is `covalent` or `non-covalent`.
- `-f`, `--filename`: (Required) Path to the input `.mol2` file containing the molecular structure.
- `-a`, `--approach`: (Optional) Specify the approach for non-covalent parameterization. Choices: `both`, `mmff-based`, `match`.
- `-y`, `--hydrogen`: (Optional) Include hydrogen atoms in the parameterization. Choices: `yes`, `no`.
- `-l`, `--ligand`: (Required for covalent parameterization) Specify the ligand name.
- `-r`, `--reaction`: (Required for covalent parameterization) Specify the type of reaction. Valid choices include: `aziridine_open`, `blac_open`, `carbonyl_add`, `disulf_form`, `epoxide_open`, `glac_open`, `imine_form`, `michael_add`, `nitrile_add`, `nucl_subst`.
- `-p`, `--protres`: (Required for covalent parameterization) Specify the residue type. Valid choices include: `CYS`, `SER`, `THR`, `LYS`, `TYR`, `ASP`, `GLU`.
- `-t`, `--topology`: (Optional) Specify the topology. Choices: `post-cap`, `pre`. Default is `post-cap`.
- `-m`, `--charm`: (Optional) Specify the CHARMM force field version. Choices: `c22`, `c27`.
- `-d`, `--delete_atoms`: (Optional) Specify whether to delete certain atoms during parameterization.

### Example

#### Covalent Parameterization

```bash
python swissparam.py -c covalent -f molecule.mol2 -l LIG1 -r aziridine_open -p CYS
```

#### Non-Covalent Parameterization

```bash
python swissparam.py -c non-covalent -f molecule.mol2 -a mmff-based
```

## Running the Script

1. Ensure that the SwissParam server is reachable.
2. Prepare your input `.mol2` file with the desired molecular structure.
3. Execute the script with the appropriate command-line arguments.

## Notes

- Ensure that all required parameters are provided based on the type of parameterization (covalent or non-covalent).
- The script will output the session number and status updates during execution.
- Results will be saved as `results.tar.gz` in the current working directory.

## Acknowledgments

This script utilizes the SwissParam web service, which provides valuable resources for molecular parameterization.

## Reference

[http://www.swissparam.ch/command-line.php](
http://www.swissparam.ch/command-line.php)
