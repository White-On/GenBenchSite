import argparse
import os
import shutil
from pathlib import Path

from benchmark import Benchmark
from benchsite import BenchSite
from collectCode import CollectCode
from getMachineData import SaveMachineDataInJson
from logger import logger


def delete_directory(dir_path):
    """
    Clears the contents of a directory.

    :param dir_path: The path to the directory to clear.
    """
    logger.info(f"Deleting directory: {dir_path}")
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        logger.info(f"Deleted directory: {path}")
    else:
        logger.warning(f"Directory not found: {path}")
    

def start_benchmark(structure_test_path:str, resultFilename:str="result.json"):
    logger.info("Starting the benchmark")
    benchmark = Benchmark(pathToInfrastructure=structure_test_path)
    benchmark.StartAllProcedure()

    benchmark.ConvertResultToJson(outputFileName=resultFilename)

def repository_is_local(repository):
    return Path(repository)

def repository_is_github(repository):
    default_repository_name = "repository"

    # we create a local repository
    path = Path(default_repository_name)
    if not path.exists():
        logger.debug(f"Creating the local repository {path}")
        path.mkdir()
    else:
        # we clear the local repository
        delete_directory(path.absolute().__str__())

    # we clone the repository in the local repository
    command = f"git clone {repository} {path}"
    try:
        os.system(command)
    except:
        logger.error(f"Error when cloning the repository {repository}")
        raise Exception(f"Error when cloning the repository {repository}")

    return path

if __name__ == "__main__":
    # first step is to Run the tests and evaluate the library based on the repository
    # inputed by the user. This repository may be a github repository or a local repository.

    # usage :
    # python main.py {access_folder} {repository} {output_folder} {publish}

    # access_folder = the way the repository is accessed. If the repository is local, the value is local. If the repository is on github, the value is github
    # repository = the path of the repository if isLocal is True, the name of the repository if isLocal is False
    # output_folder = the path of the folder where the user want to save the HTML page
    # publish = True if the user want to deploy the HTML page, False otherwise

    current_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="Generate a static website of a benchmark of libraries."
    )

    parser.add_argument(
        "repository",
        type=str,
        help="the path of the repository",
    )

    parser.add_argument(
        "-A",
        "--access_folder",
        help="The way the repository is accessed. If the repository is local, the value is local. If the repository is on github, the value is github",
        default="local",
        choices=["local", "github"],
    )

    parser.add_argument(
        "-O",
        "--output_folder",
        type=str,
        help="the path of the folder where the user want to save the HTML page",
        default="pages",
    )

    parser.add_argument(
        "-P",
        "--publish",
        help="True if the user want to deploy the HTML page, False otherwise",
        default=True,
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "-B",
        "--benchmark",
        help="True if the user want to run the benchmark, False otherwise.\
            If set to False, the user must provide the result.json file in the repository",
        default=True,
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "-R",
        "--re_use_result",
        help="True if the user want to re-use the result.json file in the repository, False otherwise",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()
    logger.info(f"args: {args}")
    default_repository_name = "repository"

    logger.info("Starting the main script")

    possible_access_folder = {"local":repository_is_local, "github":repository_is_github}
    
    logger.info(f"Access folder: {args.access_folder}")
    logger.info(f"Repository: {args.repository}")

    working_directory = possible_access_folder[args.access_folder](args.repository)

    if not working_directory.exists():
        logger.error(f"Path {working_directory.absolute()} does not exist")
        raise Exception(f"Path {working_directory.absolute()} does not exist")

    # Test the repository
    resultFilename = Path("result.json")
    codeFilename = Path("code.json")
    machineFilename = Path("machine.json")

    if args.benchmark:
        start_benchmark(working_directory.absolute().__str__(), resultFilename.absolute().__str__())

    # we want to create two additional files :
    # - a file that contains the machine information/metadata
    # - a file that contains the code of the tests done on the test repository

    CollectCode(pathToInfrastructure=working_directory.absolute().__str__(), outputPath=current_dir)

    SaveMachineDataInJson(outputFile=os.path.join(current_dir, machineFilename))

    # The second step is to create the HTML page from the test results. This HTML page will be
    # created in the output folder. The output folder is the folder where the user want to save the
    # HTML page. The output folder is the same as the input folder if the user didn't specify an output folder.

    benchsite = BenchSite(inputFilename=resultFilename.absolute().__str__(), outputPath=args.output_folder)
    benchsite.GenerateStaticSite()

    # we copy the result.json file in the output folder
    shutil.copyfile(
        resultFilename.absolute(),
        os.path.join(args.output_folder, resultFilename),
    )

    # we delete the result.json,code.json and machine.json files
    os.remove(resultFilename.absolute())
    os.remove(codeFilename.absolute())
    os.remove(machineFilename.absolute())

    # The third step is to deploy the HTML page on a server. The server is a github page. The user
    # must have a github account and a github repository. The user must have a github token to deploy
    # the HTML page on the github page. The user must specify the name of the github repository where
    # the HTML page will be deployed.

    if args.publish and args.access_folder == "github":
        logger.info("Publishing the HTML page on the github page")
        # before copying the output folder in the repository, we need to check if there is not already
        # copy the output folder in the repository
        if os.path.exists(os.path.join(args.repository, args.output_folder)):
            shutil.rmtree(os.path.join(args.repository, args.output_folder))
        shutil.copytree(
            args.output_folder, os.path.join(args.repository, args.output_folder)
        )
        print("Deploying the HTML page on the github page")
        os.chdir(args.repository)
        os.system(f"git add {args.output_folder}")
        os.system(f'git commit -m "Update the HTML page"')
        os.system(f"git push")
        print("HTML page deployed on the github page")

        # we remove the local repository
        shutil.rmtree(working_directory.absolute())
