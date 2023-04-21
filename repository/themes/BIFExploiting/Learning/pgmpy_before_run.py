from pandas import read_csv, DataFrame
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.readwrite import BIFReader
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

# Read the data from the file
samples = read_csv(f"{currentdir}/data/sample_{sys.argv[1]}_alarm.csv", sep=",")

alarm_model = BIFReader(f"{currentdir}/data/alarm.bif").get_model()

model_struct = BayesianNetwork(ebunch=alarm_model.edges())



