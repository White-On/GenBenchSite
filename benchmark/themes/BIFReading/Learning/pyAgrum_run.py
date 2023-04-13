import pyAgrum as gum
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

bn = gum.loadBN(f"{currentdir}/data/alarm.bif")

learner = gum.BNLearner(f"{currentdir}/data/sample_{sys.argv[1]}_alarm.csv")
learner.useLocalSearchWithTabuList()
bnlearned = learner.learnBN()

gum.saveBN(bnlearned,f"{currentdir}/data/pyAgrum_learned_{sys.argv[1]}_alarm.bif")