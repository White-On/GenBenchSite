import os 
import pyAgrum as gum
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))

# remove old data
if not os.path.exists(f"{currentdir}/data"):
    os.mkdir(f"{currentdir}/data")

for file in os.listdir(f"{currentdir}/data"):
    os.remove(f"{currentdir}/data/{file}")

numberBN = 10

listBn = []
listFileName = []
for _ in range(numberBN):
    n = np.random.randint(10,20)
    # ratio_arc = np.random.uniform(1,1.5)
    ratio_arc = 1.5
    domain_size = np.random.randint(2,4)
    
    try:
        bn = gum.randomBN(n = n, ratio_arc= ratio_arc, domain_size=domain_size)
        listBn.append(bn)
        listFileName.append(f"BN_{n}_{ratio_arc}_{domain_size}.bif")
        
        gum.saveBN(bn, f"{currentdir}/data/BN_{n}_{ratio_arc}_{domain_size}.bif")
        
    except:
        print("Could not create BN")
        continue

# We read the config file, find the arguments line and then replace it with the new arguments
with open(f"{currentdir}/config.ini","r") as file:
    lines = file.readlines()
    for i,line in enumerate(lines):
        if line.startswith("arguments"):
            lines[i] = f"arguments = {','.join(listFileName)}\n"
            break
    
    
with open(f"{currentdir}/config.ini","w") as file:
    file.writelines(lines)



