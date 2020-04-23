# Diffspot

Diffspot generates a CSV list of file paths and hash values (SHA-224) and also compares two CSV lists to spot differences in files (based on different hash values).

The source code may be modified to use SHA-1 (160-bit output). SHA-1 is known to have collision problems, which could lead to loss of integrity if an attacker manipulates a clear message in order to obtain the same hash of the original message, but for a simple file diff, it would make the hashing function a bit faster. During tests, SHA-1 reduced the time in 1 second per GB of data in comparison with SHA-224.

### Why?

To help describe the status of a file system before the introduction of modifications or before the installation of a package. 

Sample output:
```shell
./venv/bin/pip3.7,4f5345bbffd327d4a7b1c29a2db8e620a1b17069f37e095fc1d6fa99
./venv/bin/python3,f09e66162f6cd1283bb4de465e559542903bb30e5f1a06300b89c33b
./venv/bin/easy_install,54ec59b794776187f4a943c262ee3e059f247f81618a85350940fdfb
```

## Release notes

This repository contains all Diffspot files (one file). 

## Requirements

Based on Python 3, requires only default libraries: os, hashlib, argparse, datetime, difflib, sys, stat

- Clone this repository (or download the single Python script)

## Execution

### Command line options

One of the arguments -v/--version -g/--generate -c/--compare is required.

```
$ python diffspot.py -h
usage: diffspot.py [-h] (-v | -g GENERATE | -c COMPARE) [-l LOCATION] [-if]
                   [-ip] [-b BEFORE] [-a AFTER] [-o] [-q] [-u]
                   [--include-matches | --only-matches]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Prints version
  -g GENERATE, --generate GENERATE
                        Generates hashes
  -c COMPARE, --compare COMPARE
                        Compares hashes
  -l LOCATION, --location LOCATION
                        Folder to hash files (generation only)
  -if, --ignore-fullpath
                        Doesn't require full path in location (generation
                        only)
  -ip, --ignore-permission
                        Ignores permission errors and moves on (generation
                        only)
  -b BEFORE, --before BEFORE
                        First file for comparison
  -a AFTER, --after AFTER
                        Second file for comparison
  -o, --overwrite       Overwrites existing hash output file (-g) and existing
                        comparison output file (-c)
  -q, --quiet           Quiet mode
  -u, --unified-diff    Uses unified diff to show results (comparison only)
  --include-matches     Compares and includes matches in results (comparison
                        only)
  --only-matches        Compares and includes matches in results (comparison
                        only)
```

### Hash generation

- Example
  - $ python3 diffspot.py -g user-Library_before.txt -l /Users/username/Library -o -ip
  - $ python3 diffspot.py -g user-Library_after.txt -l /Users/username/Library -o -ip

### Hash comparison

- Example
  - $ python3 diffspot.py -c user-Library_comparison.txt -b user-Library_before.txt -a user-Library_after.txt -o

## Tests

This script was successfully executed with:
- macOS Catalina 10.15.3
- Python 3.7.2 and 3.7.4
