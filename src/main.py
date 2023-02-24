import sys
import os

from initialize.Initialize import Initialize

# Set path to project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)
os.chdir('../')

"""
    Main class, initializes the program
"""


def main():
    Initialize(sys.argv)


if __name__ == "__main__":
    main()
