import argparse
import os
import shutil
import subprocess
from pathlib import Path

from benchmark import Benchmark
from benchsite import BenchSite
from logger import logger


def delete_directory(dir_path: str):
    """
    Clears the contents of a directory.

    Arguments
    ---------
    dir_path : str
        The path to the directory to clear.

    """
    logger.info(f"Deleting directory: {dir_path}")
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        logger.info(f"Deleted directory: {path}")
    else:
        logger.warning(f"Directory not found: {path}")


def delete_file(file_path):
    """
    Clears the contents of a file.

    Arguments
    ---------
    file_path : str
        The path to the file to clear.
    """
    logger.info(f"Deleting file: {file_path}")
    path = Path(file_path)
    if path.exists() and path.is_file():
        os.remove(path)
        logger.info(f"Deleted file: {path}")
    else:
        logger.warning(f"File not found: {path}")


def start_benchmark(structure_test_path: str, resultFilename: str = "results.json"):
    """
    Starts the benchmark script with the given parameters.

    Arguments
    ---------
    structure_test_path : str

    """
    baseFilename = resultFilename if Path(resultFilename).exists() else None
    benchmark = Benchmark(
        pathToInfrastructure=structure_test_path, baseResult=baseFilename
    )
    benchmark.StartAllProcedure()
    benchmark.ConvertResultToJson(outputFileName=resultFilename)


def repository_is_local(repository, **kargs):
    return Path(repository)


def repository_is_github(repository, **kargs):
    default_repository_name = "repository"

    # we create a local repository
    path = Path(default_repository_name)
    if not path.exists():
        logger.debug(f"Creating the local repository {path}")
        path.mkdir()
    else:
        # we check if a python file has changed since the last pull
        if len(has_python_file_changed(path.absolute().__str__())) > 0:
            logger.info(f"Python file has changed since the last pull")
            # we clear the local repository and the results file needed for the benchmark
            # as the old test are now deprecated we delete the old results
            delete_directory(path.absolute().__str__())
            delete_file(kargs["resultFilename"])

        else:
            logger.info(f"No python file has changed since the last pull")
            # we merge the remote repository with the local repository
            command = f"git -C {path} pull"
            try:
                os.system(command)
            except:
                logger.error(
                    f"Error when merging the remote repository with the local repository {repository}"
                )
                raise Exception(
                    f"Error when merging the remote repository with the local repository {repository}"
                )
            return path

    # we clone the repository in the local repository
    command = f"git clone {repository} {path}"
    try:
        os.system(command)
    except:
        logger.error(f"Error when cloning the repository {repository}")
        raise Exception(f"Error when cloning the repository {repository}")

    return path


def has_python_file_changed(repository_name: str)-> list:
    # we memorize the current directory
    current_dir = os.getcwd()
    # we check if a python file has changed since the last pull
    # we go to the repository
    os.chdir(repository_name)
    # we get the last commit
    fetch = subprocess.Popen(["git", "fetch"], stdout=subprocess.PIPE)
    fetch.wait()
    # we get the last commit of the remote repository
    last_commit = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"]).strip()
    # we get the last commit of the local repository
    local_last_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    # we compare the two commits
    # compare the SHAs to see if the Python file has changed
    files_changed = subprocess.check_output(
        ["git", "diff", "--name-only", last_commit, local_last_commit], encoding="utf-8"
    ).splitlines()
    logger.debug(f"Files changed : {files_changed}")
    # we go back to the current directory
    os.chdir(current_dir)
    changed_python_files = []
    for file in files_changed:
        if file.endswith(".py"):
            changed_python_files.append(file) 
    return changed_python_files


def enough_test_to_publish(resultFilename: str, min_test_required: int = 10):
    """
    Checks if there are enough tests to publish the results.

    Arguments
    ---------
    resultFilename : str
        The path to the file containing the results of the benchmark.
    """
    # we check if the file exists
    if not Path(resultFilename).exists():
        return False
    # we check if the file is empty
    if Path(resultFilename).stat().st_size == 0:
        return False
    # we're not constraint by the number of tests
    if min_test_required == 0:
        return True
    # we check if there are enough tests
    return count_test() % min_test_required == 0


def count_test():
    import json_to_python_object as jtpo

    return jtpo.count_test()


if __name__ == "__main__":
    # first step is to Run the tests and evaluate the library based on the repository
    # inputed by the user. This repository may be a github repository or a local repository.

    # usage :
    # python main.py <repository> [-A <access_folder>] [-O <output_folder>] [-P <publish>] [-B <benchmark>]

    # access_folder = the way the repository is accessed. If the repository is local, the value is local. If the repository is on github, the value is github
    # repository = the path of the repository if isLocal is True, the name of the repository if isLocal is False
    # output_folder = the path of the folder where the user want to save the HTML page
    # publish = True if the user want to deploy the HTML page, False otherwise

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # we go to the current directory
    os.chdir(current_dir)

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
        "-F",
        "--force_publish",
        help="True if the user want to publish the HTML page even if there are not enough tests, False otherwise",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()
    logger.info(f"Arguments: {args}")
    default_repository_name = "repository"

    logger.info("=======Starting the main script=======")

    # Test the repository
    resultFilename = Path("results.json")

    possible_access_folder = {
        "local": repository_is_local,
        "github": repository_is_github,
    }

    logger.info(f"Access folder: {args.access_folder}")
    logger.info(f"Repository: {args.repository}")

    working_directory = possible_access_folder[args.access_folder](
        args.repository, resultFilename=resultFilename.absolute()
    )

    if not working_directory.exists():
        logger.error(f"Path {working_directory.absolute()} does not exist")
        raise Exception(f"Path {working_directory.absolute()} does not exist")

    if args.benchmark:
        start_benchmark(
            working_directory.absolute().__str__(),
            resultFilename.absolute().__str__(),
        )

    # The second step is to create the HTML page from the test results. This HTML page will be
    # created in the output folder. The output folder is the folder where the user want to save the
    # HTML page. The output folder is the same as the input folder if the user didn't specify an output folder.

    benchsite = BenchSite(
        inputFilename=resultFilename.absolute().__str__(), outputPath=args.output_folder
    )
    benchsite.GenerateStaticSite()

    # we copy the result.json file in the output folder
    shutil.copyfile(
        resultFilename.absolute(),
        os.path.join(args.output_folder, resultFilename),
    )

    # The third step is to deploy the HTML page on a server. The server is a github page. The user
    # must have a github account and a github repository. The user must have a github token to deploy
    # the HTML page on the github page. The user must specify the name of the github repository where
    # the HTML page will be deployed.

    if args.publish and args.access_folder == "github":
        if not args.force_publish and not enough_test_to_publish(
            resultFilename.absolute().__str__()
        ):
            logger.info("Not enough tests to publish the results")
            logger.debug(f"Number of tests: {count_test()}")
            exit(0)
        logger.info("Publishing the HTML page on the github page")
        # before copying the output folder in the repository, we need to check if there is not already
        # copy the output folder in the repository
        if os.path.exists(
            os.path.join(working_directory.absolute(), args.output_folder)
        ):
            logger.info(
                f"Removing the folder {os.path.join(working_directory.absolute(), args.output_folder)}"
            )
            shutil.rmtree(
                os.path.join(working_directory.absolute(), args.output_folder)
            )
        shutil.copytree(
            args.output_folder,
            os.path.join(working_directory.absolute(), args.output_folder),
        )
        os.chdir(working_directory.absolute())
        os.system(f"git add {args.output_folder}")
        os.system(f'git commit -m "Updating the HTML page"')
        os.system(f"git push")
        logger.info("HTML page deployed on the github page")

        # we remove the local repository
        # shutil.rmtree(working_directory.absolute())
