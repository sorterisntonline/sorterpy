"""
CURRENTLY UNUSED

Console script for sorterpy."""
import sys
import argparse
import sorterpy


def main():
    """Console script for sorterpy."""
    parser = argparse.ArgumentParser(description='sorterpy command line interface')
    args = parser.parse_args()
    
    print("Replace this message by putting your code into sorterpy.cli.main")
    print("See argparse documentation at https://docs.python.org/3/library/argparse.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
