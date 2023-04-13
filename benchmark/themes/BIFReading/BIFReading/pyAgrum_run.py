import sys
import pyAgrum as gum
import os

currentdir = os.path.dirname(os.path.realpath(__file__))

bn = gum.loadBN(f"{currentdir}/data/{sys.argv[1]}")
