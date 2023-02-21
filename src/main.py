import sys
import os

from initialize.Initialize import Initialize

#print(os.getcwd())
os.chdir('../')
#print(os.getcwd())
# TODO adjust

"""
    Main class, initializes the program
"""


def main():
    Initialize(sys.argv)


if __name__ == "__main__":
    main()
