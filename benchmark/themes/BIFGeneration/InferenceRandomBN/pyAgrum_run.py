import pyAgrum as gum
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

bn = gum.loadBN(f"{currentdir}/data/{sys.argv[1]}")

ie=gum.LazyPropagation(bn)
ie.makeInference()
