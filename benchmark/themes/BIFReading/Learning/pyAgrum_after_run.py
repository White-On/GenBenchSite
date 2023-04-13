import pyAgrum as gum
import pyAgrum.lib.bn_vs_bn as gcm
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))

# bn = gum.loadBN(f"{currentdir}/data/alarm.bif")

# learner = gum.BNLearner(f"{currentdir}/data/sample_{sys.argv[1]}_alarm.csv")
# learner.useLocalSearchWithTabuList()
# bnlearned = learner.learnBN()

# gum.saveBN(bnlearned,f"{currentdir}/data/pyAgrum_learned_{sys.argv[1]}_alarm.bif")

# evaluation of the learned network

# probleme ICI 
# bn1 = gum.loadBN(f"{currentdir}/data/alarm.bif")
# bn2 = gum.loadBN(f"{currentdir}/data/pyAgrum_learned_{sys.argv[1]}_alarm.bif")

# cmp=gcm.GraphicalBNComparator(bn1,bn2)

# print("\nscore: ",cmp.scores())
