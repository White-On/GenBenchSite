from pgmpy.readwrite import BIFReader
import sys
import os

currentdir = os.path.dirname(os.path.realpath(__file__))

reader = BIFReader(f"{currentdir}/data/{sys.argv[1]}")

