#!/usr/local/bin/python3

# Diffspot v0.1
# Author: Marcelo Martins (exploitedbunker.com)
# Source: https://github.com/mmartins000/diffspot
# Generates and compares files using SHA-256 hash CSV lists.

import os
import hashlib
import argparse
import datetime
from difflib import unified_diff, Differ
import sys
from stat import *

__AUTHOR__ = "Marcelo Martins (exploitedbunker.com)"
__LICENSE__ = "GNU GPL 3"
__VERSION__ = "0.1"

COUNTER = 0
DIFF = 0
blocksize = 64*1024

parser = argparse.ArgumentParser()
action = parser.add_mutually_exclusive_group(required=True)
action.add_argument("-v", "--version", dest='version', action='store_true', help="Prints version")
action.add_argument("-g", "--generate", dest='generate', help="Generates hashes")
action.add_argument("-c", "--compare", dest='compare', help="Compares hashes")

parser.add_argument("-l", "--location", dest='location', help="Folder to hash files (generation only)")
parser.add_argument("-if", "--ignore-fullpath", dest='ignorefullpath', action='store_true',
                    help="Doesn't require full path in location (generation only)")
parser.add_argument("-ip", "--ignore-permission", dest='ignorepermission', action='store_true',
                    help="Ignores permission errors and moves on (generation only)")

parser.add_argument("-b", "--before", dest='before', help="First file for comparison")
parser.add_argument("-a", "--after", dest='after', help="Second file for comparison")
parser.add_argument("-o", "--overwrite", dest='overwrite', action='store_true',
                    help="Overwrites existing hash output file (-g) and existing comparison output file (-c)")
parser.add_argument("-q", "--quiet", dest='quiet', action='store_true', help="Quiet mode")
parser.add_argument("-u", "--unified-diff", dest='unified_diff', action='store_true',
                    help="Uses unified diff to show results (comparison only)")

cmp_opts = parser.add_mutually_exclusive_group(required=False)
cmp_opts.add_argument("--include-matches", dest='includematches', action='store_true',
                      help="Compares and includes matches in results (comparison only)")
cmp_opts.add_argument("--only-matches", dest='onlymatches', action='store_true',
                      help="Compares and includes matches in results (comparison only)")
args = parser.parse_args()


def print_version():
    print("Diffspot, version", __VERSION__)
    exit(0)


def check_folder(folder):
    if os.path.exists(folder):
        return True
    return False


def check_filename(filename):
    if os.path.exists(filename) and not args.overwrite:
        return True
    return False


def check_fullpath(folder):
    if (str(folder).startswith('.') or str(folder).startswith('..')) and not args.ignorefullpath:
        return True
    return False


def hasher(filepath):
    sha = hashlib.sha224()      # sha1 might be an option for a simple diff, it's a bit faster.
    # during tests, sha1 reduced the time in 1s per GB of data
    try:
        with open(filepath, 'rb') as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                sha.update(data)
    except PermissionError:
        if args.ignorepermission:
            pass
            return ""
        else:
            args.quiet or print("Missing read permission while reading", filepath)
            exit(13)
    return sha.hexdigest()


def erase_file_output(file_output):
    if args.overwrite:
        open(file_output, 'w').close()


def is_file_regular(filepath):
    # Avoid sockets, fifos, symbolic links, etc
    if S_ISREG(os.stat(filepath).st_mode):
        return True
    return False


def generate_hashes(file_output, top_folder_location):
    global COUNTER
    erase_file_output(file_output)

    with open(file_output, 'a') as hf:
        for root, dirs, files in os.walk(top_folder_location):
            for file in files:
                full_file_path = os.path.join(root, file)
                if is_file_regular(full_file_path):
                    hash_line = full_file_path + ',' + hasher(full_file_path) + '\n'
                    hf.writelines(hash_line)
                    COUNTER += 1


def compare_hashes(file_output, file_before, file_after):
    global COUNTER, DIFF
    erase_file_output(file_output)

    read_file_before = open(file_before, 'r').readlines()
    read_file_after = open(file_after, 'r').readlines()
    COUNTER = max(len(read_file_before), len(read_file_after))

    if args.unified_diff:
        if args.includematches:
            result = unified_diff(read_file_before, read_file_after,
                                  fromfile=file_before, tofile=file_after, n=COUNTER)
            result = list(result)
        elif args.onlymatches:
            result = unified_diff(read_file_before, read_file_after,
                                  fromfile=file_before, tofile=file_after, n=COUNTER)
            result = list(result)
            result = [x for x in result if not x.startswith("? ") and not x.startswith("-") and not x.startswith("+")]
        else:
            result = unified_diff(read_file_before, read_file_after, fromfile=file_before, tofile=file_after, n=0)
            result = list(result)

        if type(result) == list:
            DIFF = max(sum(1 for r in result if r.startswith("+") and not r.startswith("++")),
                       sum(1 for r in result if r.startswith("-") and not r.startswith("--")))
    else:
        d = Differ()
        result = list(d.compare(read_file_before, read_file_after))

        if type(result) == list:
            DIFF = max(sum(1 for r in result if r.startswith("+ ")), sum(1 for r in result if r.startswith("- ")))

        if args.includematches:
            result = [x for x in result if not x.startswith("? ")]
        elif args.onlymatches:
            result = [x for x in result if not x.startswith("? ") and not x.startswith("- ") and not x.startswith("+ ")]
        else:   # not include-matches
            result = [x for x in result if not x.startswith("? ") and not x.startswith(" ")]

    if not args.quiet and args.verbose:
        print("Compare results:")
        if type(result) == list:
            if len(result) == 0:
                print("Nothing to report.")
            sys.stdout.writelines(result)

    if type(result) == list:
        with open(file_output, 'a') as cf:
            cf.writelines(result)


def main():
    args.version and print_version()
    if not check_folder(args.location):
        print("Folder", args.location, "not found.")
        exit(1)
    if check_fullpath(args.location):
        args.quiet or \
            print("Don't use relative paths (", args.location, ") or specify --no-check-fullpath")
        exit(2)

    starttime = datetime.datetime.now()
    if args.generate:
        if check_filename(args.generate):
            args.quiet or \
                print("File", args.generate, "already exists. Use -o or --overwrite or pick a different file name.")
            exit(3)
        generate_hashes(args.generate, args.location)
    else:
        if check_filename(args.compare):
            args.quiet or \
                print("File", args.compare, "already exists. Use -o or --overwrite or pick a different file name.")
            exit(3)
        if args.before and args.after:
            compare_hashes(args.compare, args.before, args.after)
        else:
            print("Missing one or both files for comparison. Use -b <file> -a <file>")
            exit(4)
    endtime = datetime.datetime.now()

    if not args.quiet:
        if args.generate:
            print("\nDiffspot took", endtime - starttime, "to hash", COUNTER, "files.")
        else:
            print("\nDiffspot took", endtime - starttime,
                  "to compare at least", COUNTER, "files and found at least", DIFF, "differences.")


if __name__ == "__main__":
    main()
