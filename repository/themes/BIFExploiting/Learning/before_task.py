import pyAgrum as gum
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

bifFile, sample_size = sys.argv[1].split(" ")
sample_size = sample_size.split(",")

bn = gum.loadBN(f"{currentdir}/data/{bifFile}")

for size in sample_size:
    gum.generateSample(bn,int(size),f"{currentdir}/data/sample_{size}_{bifFile.split('.')[0]}.csv");
