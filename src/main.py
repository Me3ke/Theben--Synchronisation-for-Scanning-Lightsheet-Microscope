import sys
import os

from initialize.Initialize import Initialize

os.chdir('../')

"""
    Main class, initializes the program
"""


def main():
    Initialize(sys.argv)


if __name__ == "__main__":
    main()
