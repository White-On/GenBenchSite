import pyAgrum as gum
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

bn = gum.loadBN(f"{currentdir}/data/alarm.bif")


gum.saveBN(bn,f"{currentdir}/data/outContext.bif")