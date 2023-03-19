#!/usr/bin/env python

"""a command line application to `unzip` archives"""

__version__ = "0.1.0"

from argparse import ArgumentParser
from datetime import datetime
from fnmatch import fnmatch
from os import makedirs, path
from re import match
from sys import argv, exit
from zipfile import is_zipfile, ZipFile

parser = ArgumentParser(
    usage="%(prog)s [-lnojptq] ZIP [FILE]... [-x FILE]... [-d DIR]",
    description="Extract FILEs from ZIP archive",
)

parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="List contents (with -q for short form)",
)

parser.add_argument(
    "-n",
    "--never-overwrite",
    action="store_false",
    default="ask",
    help="Never overwrite files (default: ask)",
    dest="overwrite",
)

parser.add_argument(
    "-o",
    "--overwrite",
    action="store_true",
    help="Overwrite",
    dest="overwrite",
)

parser.add_argument(
    "-j",
    "--junk-dirs",
    action="store_true",
    help="Do not restore paths",
)

parser.add_argument(
    "-p",
    "--pipe-to-stdout",
    action="store_true",
    help="Write to stdout",
)

parser.add_argument(
    "-t",
    "--test",
    action="store_true",
    help="Test",
)

parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Quiet",
)

parser.add_argument(
    "-x",
    "--exclude",
    nargs="+",
    help="Exclude FILEs",
    metavar="FILE",
)

parser.add_argument(
    "-d",
    "--extract-dir",
    help="Extract into DIR",
    metavar="DIR",
)

parser.add_argument(
    "ZIP",
    nargs="+",
    help="The zip archive that contains FILEs to process",
)

args = parser.parse_args()

# Split the positional agruments.
#
# `args.ZIP`     -- the zip archive.
#
# `args.include` -- an array of patterns to fnmatch each against the
#                   files in `args.ZIP`.
#
args.include = args.ZIP[1:]
args.ZIP = args.ZIP[0]


# is_excluded :: String -> Boolean
def is_excluded(file):
    if args.exclude:
        return any([e for e in args.exclude if fnmatch(file, e)])

    return False


# is_included :: String -> Boolean
def is_included(file):
    if args.include:
        return any([i for i in args.include if fnmatch(file, i)])

    return True


# get_file_list :: ZipFile -> [String]
def get_file_list(zip):
    files = zip.namelist()
    return [f for f in files if is_included(f) and not is_excluded(f)]


# print_file_list :: ZipFile -> IO -> None
def print_file_list(zip):
    file_list = get_file_list(zip)
    total_size = 0

    if file_list:
        print("  Length      Date    Time    Name")
        print(" --------  ---------- -----   ----")

        for z in zip.infolist():
            if z.filename in file_list:
                total_size += z.file_size
                print(
                    "{:>9}  {:%m-%d-%Y %H:%M}   {}".format(
                        z.file_size, datetime(*z.date_time), z.filename
                    )
                )

        print(f" --------{' ':>21}-------")
        print(f"{total_size:>9}{' ':>21}{len(file_list)} files")


# extract_file :: (ZipFile, String, String) -> IO -> None
def extract_file(zip, new_name, old_name):
    new_path = path.join(args.extract_dir or "", new_name)

    if old_name.endswith("/"):
        if not path.exists(new_path):
            if not args.quiet:
                print(f"   creating {new_name}")

            makedirs(path.dirname(new_path))
    else:
        if not args.quiet:
            print(f"  inflating {new_name}")

        with open(new_path, "wb") as output:
            output.write(zip.read(old_name))


# prompt_user_overwrite :: String -> IO -> String
def prompt_user_overwrite(file):
    options = "[y]es, [n]o, [A]ll, [N]one, [r]ename"
    overwrite = input(f"replace {file}? {options}: ")

    while not match("^[ynANr]", overwrite):
        print(f"error: invalid response [{overwrite[0]}]")
        overwrite = input(f"replace {file}? {options}: ")

    return overwrite


# prompt_user_new_name :: () -> IO -> String
def prompt_user_new_name():
    new_name = input("new name: ")

    while not new_name or path.isfile(path.join(args.extract_dir or "", new_name)):
        if not new_name:
            print(f"unzip: can't open '{new_name}': No such file or directory")
            exit(1)

        print(f"unzip: can't open {new_name}: File already exists")
        new_name = input("new name: ")

    return new_name


# main :: () -> IO -> None
def main():
    if not is_zipfile(args.ZIP):
        print(f"{path.basename(argv[0])}: can't open {args.ZIP}")
        exit(1)

    with ZipFile(args.ZIP) as zip:
        if args.test:
            if zip.testzip():
                print("unzip: crc error")
                exit(1)

            exit()

        if not args.quiet and not args.pipe_to_stdout:
            print(f"Archive:  {args.ZIP}")

        if args.list:
            print_file_list(zip)
            exit()

        for file in get_file_list(zip):
            new_name = file

            if args.junk_dirs:
                new_name = path.basename(file)

            if args.pipe_to_stdout:
                print(zip.read(file).decode(), end="")

            elif args.overwrite == True or not path.isfile(
                path.join(args.extract_dir or "", new_name)
            ):
                extract_file(zip, new_name, file)

            elif args.overwrite == "ask":
                response = prompt_user_overwrite(new_name)

                if response.startswith("y"):
                    extract_file(zip, new_name, file)

                elif response.startswith("n"):
                    continue

                elif response.startswith("A"):
                    args.overwrite = True
                    extract_file(zip, new_name, file)

                elif response.startswith("N"):
                    args.overwrite = False
                    continue

                else:
                    new_name = prompt_user_new_name()
                    extract_file(zip, new_name, file)


if __name__ == "__main__":
    main()
