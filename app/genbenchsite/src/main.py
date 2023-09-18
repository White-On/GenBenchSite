import argparse
import os
import shutil
import subprocess
from pathlib import Path

from .benchmark import Benchmark
from .benchsite import BenchSite
from .logger import logger
from .template import create_template


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
    benchmark.run()
    benchmark.result_to_json(outputFileName=resultFilename)


def benchmark(args):
    start_benchmark(
        structure_test_path=args.I,
        resultFilename="results.json",
    )


def website(args):
    BenchSite(
        inputFilename="results.json",
        outputPath=args.O,
        structureTestPath=args.I,
    ).GenerateStaticSite()


def create_name_for_backup_file(resultFilename: str):
    """
    Generates the name of the backup file.

    Arguments
    ---------
    resultFilename : str
        The path to the file containing the results of the benchmark.
    """
    import datetime

    # we get the current date
    now = datetime.datetime.now()
    # we get the name of the file
    filename = Path(resultFilename).name
    # we get the extension of the file
    extension = Path(resultFilename).suffix
    # we get the name of the file without the extension
    filename_without_extension = filename.replace(extension, "")
    # we create the name of the backup file
    backup_filename = (
        f"{filename_without_extension}_{now.strftime('%m-%d_%H-%M')}{extension}"
    )
    return backup_filename


def repository_is_local(repository, resultFilename: str = "results.json"):
    # we save the resutls file in a backup folder
    # as we can't know if the user want to keep the old results or not
    # if resultFilename.exists():
    #     BackupResultsFile(resultFilename)
    #     # we delete the results file
    #     delete_file(resultFilename)
    return Path(repository)


def get_task_to_reset(python_files_changed: list):
    """
    Get the tasks to reset from the python files changed.

    Arguments
    ---------
    python_files_changed : list
        The list of python files changed.
    """
    task_to_reset = []
    for file in python_files_changed:
        task_path = Path(file)
        task_to_reset.append(task_path.parent.name)
    logger.debug(f"Tasks to reset: {task_to_reset}")
    return task_to_reset


def save_results_in_backup(resultFilename: str):
    """
    Backup the results file.

    Arguments
    ---------
    resultFilename : str
        The path to the file containing the results of the benchmark.
    """
    backup_filename = create_name_for_backup_file(resultFilename)
    # we create the backup folder
    backup_folder = Path("backup")
    if not backup_folder.exists():
        backup_folder.mkdir()
    # we copy the results file in the backup folder
    shutil.copyfile(
        resultFilename,
        backup_folder / backup_filename,
    )
    logger.info(
        f"Backup of the previous results file {resultFilename} created in {backup_folder} folder with the name {backup_filename}"
    )


def reset_task(task_to_reset: list, resultFilename: str = "results.json"):
    """
    Reset the tasks.

    Arguments
    ---------
    task_to_reset : list
        The list of tasks to reset.
    """
    import json

    resultFilename = Path(resultFilename)
    # we check if the file exists
    if not resultFilename.exists():
        logger.warning("No results file to reset, you must run the benchmark first")
        logger.warning(f"File {resultFilename} does not exist")
        return
    # we open the file
    results = None
    with open(resultFilename, "r") as f:
        results = json.load(f)
    # we check if the file is empty
    if len(results) == 0:
        logger.warning("No results file to reset, the file is empty")
        logger.warning(f"File {resultFilename} is empty")
        return
    # we reset the tasks
    for target in results.keys():
        for task in task_to_reset:
            if task in results[target].keys():
                results[target][task]["results"] = {}
            else:
                logger.warning(f"Task {task} not found in results file")
    # we save the file
    with open(resultFilename, "w") as f:
        json.dump(results, f, indent=4)


def repository_is_github(repository, resultFilename: str = "results.json"):
    default_repository_name = "repository"

    # we create a local repository
    path = Path(default_repository_name)
    if not path.exists():
        logger.debug(f"Creating the local repository {path}")
        path.mkdir()
    else:
        # we check if a python file has changed since the last pull
        python_files_changed = has_python_file_changed(path.absolute().__str__())
        if len(python_files_changed) > 0:
            logger.info(f"Python file has changed since the last pull")
            # we clear the local repository and the results file needed for the benchmark
            # as the old test are now deprecated we delete the old results
            # but before that, we create a backup of the results in case the user want to keep them
            if resultFilename.exists():
                save_results_in_backup(resultFilename)
                # we get the tasks to reset
                task_to_reset = get_task_to_reset(python_files_changed)
                # we reset the tasks
                reset_task(task_to_reset, resultFilename=resultFilename)
                # we delete the local repository
                delete_directory(path.absolute().__str__())
                delete_file(resultFilename)

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
                # raise Exception(
                #     f"Error when merging the remote repository with the local repository {repository}"
                # )
                exit(1)
            return path

    # we clone the repository in the local repository
    command = f"git clone {repository} {path}"
    try:
        os.system(command)
    except:
        logger.error(f"Error when cloning the repository {repository}")
        # raise Exception(f"Error when cloning the repository {repository}")
        exit(1)

    return path


def has_python_file_changed(repository_name: str) -> list:
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
    diff_output = subprocess.check_output(
        ["git", "diff", "--name-status", last_commit, local_last_commit],
        encoding="utf-8",
    ).splitlines()
    logger.debug(f"Diff output: {diff_output}")
    # we go back to the current directory
    os.chdir(current_dir)
    changed_python_files = []
    for line in diff_output:
        status, file = line.split("\t")
        if file.endswith(".py"):
            if status == "A":
                changed_python_files.append(file)
                logger.info(f"Python file {file} has been added")
            elif status == "D":
                changed_python_files.append(file)
                logger.info(f"Python file {file} has been deleted")
            elif status == "M":
                changed_python_files.append(file)
                logger.info(f"Python file {file} has been modified")
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


def init(args):
    create_template(args.benchmark_name, args.nb_targets, args.nb_themes, args.nb_tasks)


def reset(args):
    task_name = args.task_name
    # we check if the task name is not empty
    if task_name is None or len(task_name) == 0:
        logger.error("No task name provided")
        # raise Exception("No task name provided")
        exit(1)
    # we reset the tasks
    logger.debug(f"Tasks to reset: {task_name}")
    reset_task(task_name)


def auto(args):
    # Test the repository
    result_filename = Path("results.json")
    website_folder_name = "pages"

    local_directory = repository_is_github(
        args.url, resultFilename=result_filename.absolute()
    )

    if not local_directory.exists():
        logger.error(f"Path {local_directory.absolute()} does not exist")
        # raise Exception(f"Path {local_directory.absolute()} does not exist")
        exit(1)

    start_benchmark(
        local_directory.absolute().__str__(),
        result_filename.absolute().__str__(),
    )

    # The second step is to create the HTML page from the test results. This HTML page will be
    # created in the output folder. The output folder is the folder where the user want to save the
    # HTML page. The output folder is the same as the input folder if the user didn't specify an output folder.

    benchsite = BenchSite(
        inputFilename=result_filename.absolute().__str__(),
        outputPath=Path(website_folder_name),
        structureTestPath=local_directory.absolute().__str__(),
    )
    benchsite.GenerateStaticSite()

    # we copy the result.json file in the output folder
    shutil.copyfile(
        result_filename.absolute(),
        os.path.join(args.output_folder, result_filename),
    )

    # The third step is to deploy the HTML page on a server. The server is a github page. The user
    # must have a github account and a github repository. The user must have a github token to deploy
    # the HTML page on the github page. The user must specify the name of the github repository where
    # the HTML page will be deployed.

    logger.info("Publishing the HTML page on the github page")
    # before copying the output folder in the repository, we need to check if there is not already
    # copy the output folder in the repository
    if os.path.exists(os.path.join(local_directory.absolute(), website_folder_name)):
        logger.info(
            f"Removing the folder {os.path.join(local_directory.absolute(), website_folder_name)}"
        )
        shutil.rmtree(os.path.join(local_directory.absolute(), website_folder_name))
    shutil.copytree(
        website_folder_name,
        os.path.join(local_directory.absolute(), website_folder_name),
    )
    os.chdir(local_directory.absolute())
    os.system(f"git add {website_folder_name}")
    os.system(f'git commit -m "Updating the HTML page"')
    os.system(f"git push")
    logger.info("HTML page deployed on the github page")

    # if args.publish and args.url is not None:
    #     if not args.force_publish and not enough_test_to_publish(
    #         result_filename.absolute().__str__()
    #     ):
    #         logger.info("Not enough tests to publish the results")
    #         logger.debug(f"Number of tests: {count_test()}")
    #         exit(0)
    #     logger.info("Publishing the HTML page on the github page")
    #     # before copying the output folder in the repository, we need to check if there is not already
    #     # copy the output folder in the repository
    #     if os.path.exists(os.path.join(local_directory.absolute(), args.output_folder)):
    #         logger.info(
    #             f"Removing the folder {os.path.join(local_directory.absolute(), args.output_folder)}"
    #         )
    #         shutil.rmtree(os.path.join(local_directory.absolute(), args.output_folder))
    #     shutil.copytree(
    #         args.output_folder,
    #         os.path.join(local_directory.absolute(), args.output_folder),
    #     )
    #     os.chdir(local_directory.absolute())
    #     os.system(f"git add {args.output_folder}")
    #     os.system(f'git commit -m "Updating the HTML page"')
    #     os.system(f"git push")
    #     logger.info("HTML page deployed on the github page")

    # we remove the local repository
    # shutil.rmtree(working_directory.absolute())


def main():
    # first step is to Run the tests and evaluate the library based on the repository
    # inputed by the user. This repository may be a github repository or a local repository.

    # usage :
    # python main.py <repository> [-A <access_folder>] [-O <output_folder>] [-P <publish>] [-B <benchmark>]

    # access_folder = the way the repository is accessed. If the repository is local, the value is local. If the repository is on github, the value is github
    # repository = the path of the repository if isLocal is True, the name of the repository if isLocal is False
    # output_folder = the path of the folder where the user want to save the HTML page
    # publish = True if the user want to deploy the HTML page, False otherwise

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # # we go to the current directory
    # os.chdir(current_dir)

    parser = argparse.ArgumentParser(
        description="Generate a static website of a benchmark of libraries."
    )

    subparsers = parser.add_subparsers(dest="action", help="The action to perform")

    # Subparser for the init action
    init_parser = subparsers.add_parser("init", help="Initialize the repository")
    init_parser.add_argument(
        "benchmark_name", type=str, help="The name of the repository"
    )
    init_parser.add_argument(
        "-nb_targets", type=int, help="The number of targets", default=1
    )
    init_parser.add_argument(
        "-nb_themes", type=int, help="The number of themes", default=1
    )
    init_parser.add_argument(
        "-nb_tasks", type=int, help="The number of tasks", default=1
    )
    init_parser.set_defaults(func=init)

    # Subparser for the reset action
    reset_parser = subparsers.add_parser("reset", help="Reset the repository")
    reset_parser.add_argument(
        "task_name",
        type=str,
        help="The name of the tasks to reset (separated by a space)",
        nargs="+",
    )
    reset_parser.set_defaults(func=reset)

    # Subparser for the benchmark action
    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Run the benchmark tests"
    )
    benchmark_parser.add_argument(
        "-I",
        type=str,
        help="The local path of the folder where the benchmark structure is located",
        default=Path.cwd().__str__(),
    )
    benchmark_parser.set_defaults(func=benchmark)

    # Subparser for the website action
    website_parser = subparsers.add_parser("website", help="Generate the website")
    website_parser.add_argument(
        "-I",
        type=str,
        help="The local path of the folder where the benchmark structure is located",
        default=Path.cwd().__str__(),
    )
    website_parser.add_argument(
        "-O",
        type=str,
        help="The local path of the folder where the HTML page will be generated",
        default="pages",
    )
    website_parser.set_defaults(func=website)

    # Subparser for the auto action
    auto_parser = subparsers.add_parser("auto", help="Run the benchmark tests")
    auto_parser.add_argument(
        "url",
        type=str,
        help="The url of the git repository where the benchmark structure is located",
    )
    # auto_parser.add_argument(
    #     "--publish",
    #     help="True if the user want to deploy the HTML page, False otherwise",
    #     default=True,
    #     action=argparse.BooleanOptionalAction,
    # )
    # auto_parser.add_argument(
    #     "--benchmark",
    #     help="True if the user want to run the benchmark, False otherwise. If set to False, the user must provide the result.json file in the repository",
    #     default=True,
    #     action=argparse.BooleanOptionalAction,
    # )
    auto_parser.set_defaults(func=auto)

    args = parser.parse_args()
    logger.info(f"Arguments: {args}")
    logger.info(f"Action: {args.action}")

    logger.info("=======Starting the main script=======")

    # Call the appropriate function based on the selected action
    if args.action is None:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
