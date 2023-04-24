import argparse
import os
import shutil

from benchmark import Benchmark
from benchsite import BenchSite
from collectCode import CollectCode
from getMachineData import SaveMachineDataInJson

def clear_directory(dir_path):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                clear_directory(file_path)
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


if __name__ == "__main__":
    # first step is to Run the tests and evaluate the library based on the repository 
    # inputed by the user. This repository may be a github repository or a local repository.

    # usage :
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
                        default='pages')
    
    parser.add_argument('-D','--isDeployed',
                        help='True if the user want to deploy the HTML page, False otherwise',
                        default=True,
                        action=argparse.BooleanOptionalAction)
    
    args = parser.parse_args()
    # print(args)
    online_repository = None

    if not args.isLocal:
        print("Online repository")
        # we create a local repository 
        tmpPath = os.path.join(curentPath, "repository")
        if not os.path.exists(tmpPath):
            os.mkdir(tmpPath)

        # # we clear the local repository
        # clear_directory(tmpPath)
        # os.removedirs(tmpPath)

        # we clone the repository in the local repository
        command = f"git clone {args.repository} {tmpPath}"
        try:
            os.system(command)
        except:
            raise Exception(f"Error when cloning the repository {args.repository}")
            exit(1)

        online_repository = args.repository
        args.repository = tmpPath
    
    if not os.path.exists(args.repository):
        raise Exception(f"Path {args.repository} does not exist")
    
    # Test the repository
    resultFilename = "result.json"
    codeFilename = "code.py"
    machineFilename = "machine.json"

    benchmark = Benchmark(pathToInfrastructure = args.repository)
    benchmark.StartAllProcedure()

    print(benchmark.results)
    benchmark.ConvertResultToJson(outputPath=curentPath, outputFileName=resultFilename)

    

    # we want to create two additional files :
    # - a file that contains the machine information/metadata
    # - a file that contains the code of the tests done on the test repository

    CollectCode(pathToInfrastructure= args.repository, outputPath = curentPath)

    SaveMachineDataInJson(outputFile=os.path.join(curentPath, machineFilename))

    # The second step is to create the HTML page from the test results. This HTML page will be
    # created in the output folder. The output folder is the folder where the user want to save the
    # HTML page. The output folder is the same as the input folder if the user didn't specify an output folder.
    
    benchsite = BenchSite(inputFilename=resultFilename, outputPath=args.output_folder)
    benchsite.GenerateStaticSite()
    
    # The third step is to deploy the HTML page on a server. The server is a github page. The user
    # must have a github account and a github repository. The user must have a github token to deploy
    # the HTML page on the github page. The user must specify the name of the github repository where
    # the HTML page will be deployed.

    if args.isDeployed and not args.isLocal:
        # before copying the output folder in the repository, we need to check if there is not already 
        #copy the output folder in the repository
        shutil.copytree(args.output_folder, os.path.join(args.repository, args.output_folder))
        print("Deploying the HTML page on the github page")
        os.chdir(args.repository)
        os.system(f"git add {args.output_folder}")
        os.system(f"git commit -m \"Update the HTML page\"")
        os.system(f"git push")
        print("HTML page deployed on the github page")

        # we remove the local repository
        os.chdir(curentPath)
        # shutil.rmtree(args.repository)
        


        
        


