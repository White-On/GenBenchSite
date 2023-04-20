import argparse
import os

from benchmark import Benchmark
from benchsite import BenchSite
from collectCode import CollectCode
from getMachineData import SaveMachineDataInJson

if __name__ == "__main__":
    # first step is to Run the tests and evaluate the library based on the repository 
    # inputed by the user. This repository may be a github repository or a local repository.

    # usege :
    # python main.py {isLocal} {repository} {output_folder} {isDeployed}

    # isLocal = True if the repository is local, False if the repository is on github
    # repository = the path of the repository if isLocal is True, the name of the repository if isLocal is False
    # output_folder = the path of the folder where the user want to save the HTML page
    # isDeployed = True if the user want to deploy the HTML page, False otherwise

    curentPath = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description='Generate a static website of a benchamrk of library.'
        )
    
    parser.add_argument('repository',
                        type=str,
                        help='the path of the repository if isLocal is True, the name of the repository if isLocal is False',
                        )
    
    parser.add_argument('-L','--isLocal', 
                        help='True if the repository is local, False if the repository is on github',
                        default=True,
                        action=argparse.BooleanOptionalAction)
    
    parser.add_argument('-of','--output_folder',
                        type=str,
                        help='the path of the folder where the user want to save the HTML page',
                        default='output')
    
    parser.add_argument('-D','--isDeployed',
                        help='True if the user want to deploy the HTML page, False otherwise',
                        default=False,
                        action=argparse.BooleanOptionalAction)
    
    args = parser.parse_args()
    # print(args)

    if not args.isLocal:
        print("Online repository")
        # we create a local repository 
        tmpPath = os.path.join(curentPath, "repository")
        if not os.path.exists(tmpPath):
            os.mkdir(tmpPath)
        # we clone the repository in the local repository
        command = f"git clone {args.repository} {tmpPath}"
        try:
            os.system(command)
        except:
            raise Exception(f"Error when cloning the repository {args.repository}")

        args.repository = tmpPath
    
    if not os.path.exists(args.repository):
        raise Exception(f"Path {args.repository} does not exist")
    
    # Test the repository
    benchmark = Benchmark(pathToInfrastructure = args.repository)
    benchmark.StartAllProcedure()

    print(benchmark.results)
    benchmark.ConvertResultToJson(outputPath=curentPath, outputFileName="result50")

    # we want to create two additional files :
    # - a file that contains the machine information/metadata
    # - a file that contains the code of the tests done on the test repository

    CollectCode(args.repository, curentPath)

    SaveMachineDataInJson(curentPath)

    # The second step is to create the HTML page from the test results. This HTML page will be
    # created in the output folder. The output folder is the folder where the user want to save the
    # HTML page. The output folder is the same as the input folder if the user didn't specify an output folder.

    benchsite = BenchSite("result50.json", outputFilePath=args.output_folder)

    # The third step is to deploy the HTML page on a server. The server is a github page. The user
    # must have a github account and a github repository. The user must have a github token to deploy
    # the HTML page on the github page. The user must specify the name of the github repository where
    # the HTML page will be deployed.


