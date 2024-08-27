import subprocess
import time
import json
import numpy as np
import re
from tqdm import tqdm
from pathlib import Path
import importlib

from .logger import logger
from .structure_test import (
    get_benchmark_config,
    get_target_config,
    get_theme_config,
    get_task_config,
)


class Benchmark:
    """
    Benchmark is a class that run process for each library and each task and save the results in a json file

    We expect a very specific infrastucture of file and folder in order to run the test. See the documentation for more details.

    Class Attributes
    ----------
    NOT_RUN_VALUE : str or int
        value that will be used in the json file if the task has not been run
    ERROR_VALUE : str or int
        value that will be used in the json file if an error occured during the task
    """

    NOT_RUN_VALUE = "NotRun"
    ERROR_VALUE = "Error"
    DEFAULT_VALUE = "Infinity"
    TIMEOUT_VALUE = "Timeout"

    DEFAULT_TIMEOUT = 40
    DEFAULT_NB_RUNS = 1
    DEFAULT_STOP_AFTER_X_TIMEOUT = 10
    DEBUG = False

    def __init__(self, pathToInfrastructure: str, baseResult=None) -> None:
        """
        We initialize the class by reading the config file and getting the list of library and task.
        We also initialize the results dictionary and keep the path to the infrastructure

        Parameters
        ----------
        pathToInfrastructure : str
            path to the infrastructure

        Attributes
        ----------
        pathToInfrastructure : str
            path to the infrastructure
        results : dict
            dictionary that will contain the results and will format the json file
        libraryNames : list
            list of library name
        taskNames : list
            list of task name
        dictionaryTaskInTheme : dict of list of str
            dictionary that associate a theme to a list of task
        dictonaryThemeInTask : dict of str
            dictionary that associate a task to a theme
        """

        self.pathToInfrastructure = Path(pathToInfrastructure)

        # we collect the config into a dictionary
        self.target_config = get_target_config(self.pathToInfrastructure)
        self.task_config = get_task_config(self.pathToInfrastructure)
        self.theme_config = get_theme_config(self.pathToInfrastructure)
        self.benchmark_config = get_benchmark_config(self.pathToInfrastructure)

        logger.info(
            f"Library config retrieved: list of library {self.target_config.keys()}"
        )
        logger.info(f"Task config retrieved: list of task {self.task_config.keys()}")
        logger.info(f"Theme config retrieved: list of theme {self.theme_config.keys()}")

        themeDirectory = self.pathToInfrastructure / "themes"

        self.libraryNames = list(self.target_config.keys())
        self.themeNames = list(self.theme_config.keys())

        self.taskNames = []
        self.dictionaryTaskInTheme = {}
        self.dictonaryThemeInTask = {}

        # create a dictionary that associate a theme to a list of task and a dictionary
        # that associate a task to a theme
        for themeName in self.themeNames:
            listTask = [
                task_path.name
                for task_path in themeDirectory.joinpath(themeName).iterdir()
                if task_path.is_dir()
            ]
            self.taskNames += listTask
            self.dictionaryTaskInTheme[themeName] = listTask
            for taskName in self.dictionaryTaskInTheme[themeName]:
                self.dictonaryThemeInTask[taskName] = themeName

        # We now rearange the order of execution of the tasks
        # We first look for the order in the config file
        # If no order is specified, we keep the order of the tasks in the config file
        self.taskNames = self.order_tasks()

        # look for deactivated tasks
        deactivatedTasks = []
        for taskName in self.taskNames:
            if self.task_config[taskName].get("active") == "False":
                deactivatedTasks.append(taskName)

        # remove deactivated tasks from the list of tasks
        for taskName in deactivatedTasks:
            self.dictionaryTaskInTheme[self.dictonaryThemeInTask[taskName]].remove(
                taskName
            )
            self.taskNames.remove(taskName)

        logger.debug(f"active tasks: {self.taskNames}")

        if baseResult is None:
            self.results = self.create_base_json()
        else:
            self.results = self.get_result_from_json(baseResult)
            # we check if there is a task that is not in the result file -> we added one
            for taskName in self.taskNames:
                res = self.results[self.libraryNames[0]].get(taskName, None)
                if res is None:
                    for libraryName in self.libraryNames:
                        self.results[libraryName][taskName] = {
                            "theme": self.dictonaryThemeInTask.get(taskName),
                            "results": {
                                arg: {"runtime": []}
                                for arg in self.task_config.get(taskName)
                                .get("arguments")
                                .split(",")
                            },
                        }

        logger.debug(f"{self.dictionaryTaskInTheme = }")
        logger.debug(f"{self.dictonaryThemeInTask = }")

        # logger.debug(f"{self.results = }")
        # logger.debug(f"{self.create_base_json() = }")

    def order_tasks(self) -> list:
        order = []
        for themeName in self.themeNames:
            theme_config = self.theme_config.get(themeName)

            if theme_config is None:
                logger.warning(f"No config for {themeName}")
                continue

            order_in_theme = theme_config.get("task_order")
            if order_in_theme is None:
                logger.info(f"No task order for {themeName}")
                continue

            order_in_theme = order_in_theme.split(",")
            for taskName in order_in_theme:
                (
                    order.append(taskName.strip())
                    if taskName.strip() in self.taskNames
                    else None
                )
        # we add the remaining tasks not yet added to the order
        for taskName in self.taskNames:
            if taskName not in order:
                order.append(taskName)
        logger.debug(f"Order of tasks: {order}")
        return order

    def setup_global_variables(self):
        """
        Setup the global variables from the config file

        """
        Benchmark.DEFAULT_TIMEOUT = int(
            self.benchmark_config.get("default_timeout", Benchmark.DEFAULT_TIMEOUT)
        )
        Benchmark.DEFAULT_NB_RUNS = int(
            self.benchmark_config.get("default_nb_runs", Benchmark.DEFAULT_NB_RUNS)
        )
        Benchmark.DEFAULT_STOP_AFTER_X_TIMEOUT = int(
            self.benchmark_config.get(
                "default_stop_after_x_timeout", Benchmark.DEFAULT_STOP_AFTER_X_TIMEOUT
            )
        )

    def get_result_from_json(self, json_file):
        """
        collect the results from a json file from a previous run
        """
        path_json = Path(json_file)
        if not path_json.exists():
            logger.error(f"File {json_file} does not exist")
            return self.create_base_json()

        # check suffix
        if path_json.suffix != ".json":
            logger.error(f"File {json_file} is not a json file")
            return self.create_base_json()

        with open(json_file, "r") as f:
            try:
                results = json.load(f)
            except json.decoder.JSONDecodeError:
                logger.error(f"File {json_file} is not a valid json file")
                return self.create_base_json()

        return results

    def create_base_json(self):
        """
        create the base json file structure if the json file does not exist

        """
        try:
            return {
                libraryName: {
                    taskName: {
                        "theme": self.dictonaryThemeInTask.get(taskName),
                        "results": {
                            arg: {"runtime": []}
                            for arg in self.task_config.get(taskName)
                            .get("arguments")
                            .split(",")
                        },
                    }
                    for taskName in self.taskNames
                }
                for libraryName in self.libraryNames
            }
        except Exception as e:
            logger.error(f"Error in the creation of the base json file {e = }")
            return {}

    def install_upgrade_targets(self):
        """
        Install or upgrade the targets

        """
        logger.info("=======Begining of the installation/upgrade of the targets=======")
        for libraryName in self.libraryNames:
            self.progressBar.set_description(f"Install/upgrade target {libraryName}")
            logger.info(f"Install/upgrade target {libraryName}")
            current_config = self.target_config.get(libraryName)
            if current_config is None:
                logger.warning(f"No config for {libraryName}")
                continue
            command_upgrade = current_config.get("install_command", None)
            if command_upgrade is None:
                logger.info(f"No upgrade command for {libraryName}")
                continue
            process = subprocess.run(
                command_upgrade,
                shell=True,
                capture_output=True,
            )

            if process.returncode != 0:
                logger.error(
                    f"Error in the installation/upgrade of {libraryName} : {process.stderr}"
                )
            else:
                logger.info(f"Installation/upgrade of {libraryName} successful")

    @staticmethod
    def load_module_from_path(module_name, file_path):
        """Dynamically loads a module from a given file path."""
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def run_test_function(module, function_name, *args, **kwargs):
        """Runs a function by name from a loaded module."""
        func = getattr(module, function_name, None)
        if callable(func):
            return func(*args, **kwargs)
        else:
            logger.error(
                f"Function '{function_name}' is not present in the file '{module.__file__}'\n\
                         Please make sure that the function is present in the file and that it is callable."
            )
            return None

    def preparation_task(self, taskPath: str, taskName: str):
        """
        Run the preparation task command/script of a task if it exist

        Parameters
        ----------
        taskPath : str
            path to the task
        taskName : str
            name of the task

        """
        # check if the task has a preparation task script
        preparation_task_script_path = Path(taskPath) / "preparation.py"
        preparation_task_script_exist = (
            preparation_task_script_path.exists()
            and preparation_task_script_path.is_file()
        )
        logger.debug(f"Preparation script : {preparation_task_script_path.name}")
        logger.debug(f"{preparation_task_script_exist = }")

        if not preparation_task_script_exist:
            logger.info(f"No preparation task command/script for {taskName}")
            return

        logger.info(f"preparation task of {taskName}")

        # the preparation task may have some argument
        current_config = self.task_config.get(taskName)
        if current_config is None:
            logger.warning(f"No config for {taskName}")
            return
        args = current_config.get("preparation_task_arguments")
        logger.debug(f"{args = }")
        if len(args) == 0:
            logger.warning(
                f"No arguments for the preparation task command/script for {taskName}"
            )

        preparation_task_as_module = self.load_module_from_path(
            taskName, preparation_task_script_path
        )
        status = self.run_test_function(preparation_task_as_module, "main", args)

        logger.debug(f"End of the preparation task of {taskName}")
        logger.debug(f"{status = }")

        # we run the preparation task script
        # command = f"python {preparation_task_script_path} {kwargs}"
        # logger.debug(f"{command = }")
        # self.run_command(command=command, timeout=Benchmark.DEFAULT_TIMEOUT)

        # # the before task is a function in a module
        # funcName = self.task_config[taskName].get("before_function", None)
        # logger.debug(f"{funcName = }")
        # if funcName is None:
        #     logger.error(
        #         f"No function for the before task command/script for {taskName}"
        #     )
        #     return

        # # the beforetask may have some arguments
        # kwargs = self.task_config[taskName].get("before_task_arguments", "{}")
        # kwargs = ast.literal_eval(kwargs)
        # logger.debug(f"{kwargs = }")
        # if len(kwargs) == 0:
        #     logger.warning(
        #         f"No arguments for the before task command/script for {taskName}"
        #     )

        # # we import the module and run the function
        # relativePath = os.path.relpath(
        #     taskPath, os.path.dirname(os.path.abspath(__file__))
        # ).replace(os.sep, ".")

        # # relative_module = __import__(f"{relativePath}.{beforeTaskModule}", fromlist=[funcName])
        # # func = getattr(module, funcName)

        # # logger.debug(f"{module.__name__ = }")
        # # logger.debug(f"{func.__name__ = }")

        # # try:
        # #     func(**kwargs)
        # # except Exception as e:
        # #     logger.warning(f"Error in the evaluation function {funcName} of {taskName}")
        # #     logger.debug(f"{e = }")

        # # the before task should'nt return anything
        # self.ExecuteFunctionInModule(
        #     f"{relativePath}.{beforeTaskModule}", funcName, **kwargs
        # )

    def evalution_task(
        self, taskName: str, path_to_file_to_evaluate: str, *scoring_scripts
    ):
        """
        Run the evaluation function of a task

        Parameters
        ----------
        taskPath : str
            path to the task
        taskName : str
            name of the task
        target_name : str
            name of the target
        arg : str
            argument of the task
        scoring_scripts : list of str
            list of the scoring scripts

        """
        value_evaluation = []

        if len(scoring_scripts) == 0:
            logger.info(f"No evaluation function for {taskName}")
            return value_evaluation

        for script in scoring_scripts:
            # command = f"{self.taskConfig[taskName].get('evaluation_language')} {os.path.join(taskPath,script)} {libraryName} {arg}"
            command = f"python {script} {path_to_file_to_evaluate}"
            logger.debug(
                f"Run the evaluation function for {taskName} with {command} command"
            )
            output = None
            _, output = self.run_command(
                command=command, timeout=Benchmark.DEFAULT_TIMEOUT, getOutput=True
            )
            logger.debug(f"{output = }")
            # we remove the eventual \n at the end of the output
            output = output.replace("\n", "")
            # and we transform the output to a float if possible
            raw_output = output
            try:
                output = float(output)
            except ValueError:
                logger.warning(
                    f"The scoring function '{script.name}' of '{taskName}' does not return a float, the output is '{raw_output}'"
                )
                output = Benchmark.ERROR_VALUE
            logger.debug(f" after filter {output = }")
            value_evaluation.append(output)

        return value_evaluation

    def run_command(self, command, timeout, getOutput=False):
        """
        Run a process with a timeout and return the time it took to run the process

        Parameters
        ----------
        command : str
            command to run
        timeout : int
            timeout in seconds
        getOutput : bool, optional
            if True return the output of the command, by default False
        """
        logger.debug(f"RunProcess with the command {command}")
        if Benchmark.DEBUG:
            return np.random.randint(low=5, high=10) * 1.0

        start = time.perf_counter()
        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout expired for the {command} command")
            if getOutput:
                return (Benchmark.TIMEOUT_VALUE, "")
            return Benchmark.TIMEOUT_VALUE
        end = time.perf_counter()

        logger.debug(f"{process.stdout = }")
        logger.debug(f"{process.stderr = }")
        logger.debug(f"{process.returncode = }")

        if process.returncode == 1:
            logger.warning(f"Error in the command")
            if getOutput:
                return (Benchmark.ERROR_VALUE, process.stdout)
            return Benchmark.ERROR_VALUE

        elif process.returncode == 2:
            logger.warning(f"Can't run this command")
            if getOutput:
                return (Benchmark.NOT_RUN_VALUE, process.stdout)
            return Benchmark.NOT_RUN_VALUE

        if getOutput:
            return (end - start, process.stdout)

        return end - start

    def RunTask(self, taskName: str):
        """
        Run the task for each library and save the results in the results dictionary

        Parameters
        ----------
        taskName : str
            name of the task
        """
        path = (
            self.pathToInfrastructure
            / "themes"
            / self.dictonaryThemeInTask[taskName]
            / taskName
        )

        # We check if the before task command/script exist if not we do nothing
        preparationScript = self.task_config[taskName].get("preparation_script", None)
        if preparationScript is not None:
            self.preparation_task(path, taskName)
        else:
            logger.info(f"No before task command/script for {taskName}")

        # The timeout of the task is the timeout in the config file or the default timeout
        # the timeout is in seconds
        taskTimeout = int(
            self.task_config[taskName].get("timeout", Benchmark.DEFAULT_TIMEOUT)
        )

        for libraryName in self.libraryNames:
            self.progressBar.set_description(
                f"Run task {taskName} for library {libraryName}"
            )

            self.RunTaskForLibrary(libraryName, taskName, path, timeout=taskTimeout)

    def TaskNotSupported(self, libraryName: str, taskName: str, arguments: str) -> None:
        """
        Add the task to the results dictionary with the value NOT_RUN_VALUE

        Parameters
        ----------
        libraryName : str
            name of the library
        taskName : str
            name of the task
        arguments : str
            arguments of the task
        """

        # if task not supported by the target,
        # we add the results to the results dictionary with the value NOT_RUN_VALUE
        self.results[libraryName][taskName]["results"] = {
            arg: {"runtime": Benchmark.NOT_RUN_VALUE} for arg in arguments
        }
        # Progress bar update
        self.progressBar.update(
            int(self.task_config[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS))
            * len(arguments)
            * 2
        )  # *2 because we have before and after run script

    def RunTaskForLibrary(
        self, libraryName: str, taskName: str, taskPath: str, timeout: int
    ):
        """
        Run the task for a specific library and save the results in the results dictionary

        Parameters
        ----------
        libraryName : str
            name of the library
        taskName : str
            name of the task
        taskPath : str
            path to the task
        timeout : int
            timeout in seconds
        """

        arguments = self.task_config[taskName].get("arguments")
        # if the task has no arguments we do nothing
        if arguments is None:
            logger.error(f"No arguments for {taskName}")
            return
        # we check if the argument is write in a calculable way
        # if not we split the arguments with ,
        if not re.match(r"\(\d+(?:,\d+)*\) \* \(\d+:\d+:\d+\)", arguments):
            arguments = arguments.split(",")
        else:
            arguments = matrix_arguments(arguments)
            # if the argument is not valid we do nothing
            if len(arguments) == 0:
                logger.error(f"Invalid argument {arguments}")
                return

        # we check if the library support the task
        run_script_path = Path(taskPath) / libraryName / "run.py"
        run_script_exist = run_script_path.exists() and run_script_path.is_file()
        if not run_script_exist:
            self.TaskNotSupported(libraryName, taskName, arguments)
            return

        logger.info(f"Run task '{taskName}' for library '{libraryName}'")

        # we check if there is a before run script
        before_script_path = Path(taskPath) / libraryName / "before.py"
        before_script_exist = (
            before_script_path.exists() and before_script_path.is_file()
        )

        # we check if there is a after run script
        evaluation_scripts = self.task_config[taskName].get("evaluation_scripts", None)
        if evaluation_scripts is not None:
            # if the script is not None we get the path to the scripts
            evaluation_scripts = evaluation_scripts.split(" ")
            evaluation_scripts = [
                Path(taskPath) / script for script in evaluation_scripts
            ]

            # we remove the script that does not exist
            evaluation_scripts = [
                script
                for script in evaluation_scripts
                if script.exists() and script.is_file()
            ]
            logger.debug(
                f"Script for evaluate results :{[script.name for script in evaluation_scripts]}"
            )

        # if there are evaluation scripts we check if the repository output exist if not we create it
        if evaluation_scripts is not None:
            output_directory = Path(taskPath) / "output"
            if not output_directory.exists():
                logger.warning(
                    f"Output directory don't exist, so we created {output_directory}"
                )
            output_directory.mkdir(exist_ok=True)

        stop_after_x_timeout = int(
            self.task_config[taskName].get(
                "stop_after_x_timeout", Benchmark.DEFAULT_STOP_AFTER_X_TIMEOUT
            )
        )
        stop_after_x_timeout = (
            float("inf") if stop_after_x_timeout <= 0 else stop_after_x_timeout
        )
        cpt_timeout = 0

        # runnning the task for each argument and the number of runs
        for arg in arguments:
            before_run_list_time = []
            listTime = []

            # number total of run for the task
            total_run = int(
                self.task_config[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS)
            )

            for cpt_run in range(total_run):
                logger.debug(
                    f"Run {cpt_run + 1} of {total_run} for {taskName}. At {cpt_timeout} timeout"
                )

                # BEFORE RUN SCRIPT
                if before_script_exist:
                    if cpt_timeout >= stop_after_x_timeout:
                        resultProcess = Benchmark.TIMEOUT_VALUE
                    else:
                        command = f"python {before_script_path} {arg}"

                        resultProcess = self.run_command(
                            command=command, timeout=timeout
                        )

                    before_run_list_time.append(resultProcess)
                    self.progressBar.update(1)
                    # if the before run script fail we don't run the task
                    # as the task is suposed to be an extension of the before run script
                    # if isinstance(resultProcess, str):
                    #     listTime.append(resultProcess)
                    # self.progressBar.update((total_run - cpt_run) * 2 - 1)
                    # self.progressBar.update(1)
                    # cpt_timeout += 1 if resultProcess == Benchmark.TIMEOUT_VALUE and cpt_run < stop_after_x_timeout else 0
                    # continue

                # RUN SCRIPT
                if cpt_timeout >= stop_after_x_timeout:
                    resultProcess = Benchmark.TIMEOUT_VALUE
                else:
                    command = f"python {run_script_path} {arg}"

                    resultProcess, generated_file_path = self.run_command(
                        command=command,
                        timeout=(
                            timeout + resultProcess
                            if before_script_exist
                            and not isinstance(resultProcess, str)
                            else timeout
                        ),
                        getOutput=True,
                    )
                    logger.debug(f"{resultProcess = }")

                listTime.append(resultProcess)
                self.progressBar.update(1)
                # if the run script fail we just continue to the next run
                if isinstance(resultProcess, str):
                    #     # self.progressBar.update((total_run - nb_run - 1) * 2)
                    cpt_timeout += (
                        1
                        if resultProcess == Benchmark.TIMEOUT_VALUE
                        and cpt_run < stop_after_x_timeout
                        else 0
                    )
                #     continue

                # pass if in debug mode
                if Benchmark.DEBUG:
                    continue

                # AFTER RUN SCRIPT
                if evaluation_scripts is not None:
                    # we run the evaluation function
                    # if the task has been run successfuly we run the evaluation function
                    # we also check if we create the right file to evaluate the task
                    # generated_file_path = Path(taskPath) / "output" / f"{libraryName}_{arg}.bif"
                    generated_file_path = Path(generated_file_path)
                    # print(generated_file_path)
                    # print(generated_file_path.exists())
                    if (
                        not isinstance(resultProcess, str)
                        and generated_file_path.exists()
                    ):
                        valueEvaluation = self.evalution_task(
                            taskName,
                            generated_file_path,
                            *evaluation_scripts,
                        )
                        logger.debug(f"{valueEvaluation = }")
                    # if not we add the value ERROR_VALUE to the evaluation function
                    else:
                        valueEvaluation = [Benchmark.ERROR_VALUE] * len(
                            evaluation_scripts
                        )
                    evaluation_result = self.results[libraryName][taskName]["results"][
                        arg
                    ].get("evaluation", {})

                    scoring_title = self.task_config[taskName].get(
                        "evaluation_function", None
                    )
                    if scoring_title is not None:
                        scoring_title = scoring_title.split(" ")
                    if scoring_title is None or len(scoring_title) != len(
                        evaluation_scripts
                    ):
                        logger.info(
                            f"scoring_title is not valid for {taskName}, we use default value"
                        )
                        scoring_title = [
                            f"scoring_{i}" for i in range(len(evaluation_scripts))
                        ]
                    for i, script in enumerate(evaluation_scripts):
                        element = evaluation_result.get(scoring_title[i], [])
                        evaluation_result = {
                            **evaluation_result,
                            scoring_title[i]: element + [valueEvaluation[i]],
                        }
                    self.results[libraryName][taskName]["results"][arg][
                        "evaluation"
                    ] = evaluation_result

            self.results[libraryName][taskName]["results"][arg]["runtime"].extend(
                [b, t] for b, t in zip(before_run_list_time, listTime)
            )

        logger.info(f"End task '{taskName}' for library '{libraryName}'")

    def calculate_number_interations(self):
        """
        Calculate the number of iteration for the progress bar
        """
        nbIteration = 0
        for taskName in self.taskNames:
            nbIteration += (
                int(
                    self.task_config[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS)
                )
                * len(self.task_config[taskName].get("arguments").split(","))
                * 2
                * len(self.libraryNames)
            )  # Nb runs * nb arguments * 2 (before run and after run) * nb libraries

        logger.info(f"Number of commands : {nbIteration}")
        return nbIteration

    def result_to_json(self, outputFileName="results.json"):
        """
        convert the result to a json file
        """
        with open(outputFileName, "w") as file:
            json.dump(self.results, file, indent=4)
        logger.info(f"Result saved in {outputFileName}")

    def run(self):
        """
        Run the benchmark
        """
        # we collect the global variables from the config file of the project
        self.setup_global_variables()
        # we initialize the progress bar
        self.progressBar = tqdm(
            total=self.calculate_number_interations(),
            desc="Initialization",
            ncols=125,
            position=0,
        )
        # we install or upgrade the targets libraries
        if not Benchmark.DEBUG:
            self.install_upgrade_targets()

        logger.info("=======Begining of the benchmark=======")
        for taskName in self.taskNames:
            self.RunTask(taskName)
        logger.info("=======End of the benchmark=======")


def matrix_arguments(raw_arg: str):
    # the argument cant come in a matrix form
    arg_list = []
    # get the first part and the second part of the argument
    first_part, second_part = raw_arg.split("*")
    # get arg_list from first_part
    arg_list = [int(i) for i in re.findall(r"\d+", first_part)]
    # get the list of step from second_part
    step_list = [int(i) for i in re.findall(r"\d+", second_part)]
    step_list = [i for i in range(step_list[0], step_list[1] + 1, step_list[2])]
    # check if the step_list is valid
    if len(step_list) == 0:
        return arg_list
    # if the step_list has only one element we use it for all the arguments
    if len(step_list) == 1:
        step_list = step_list * len(arg_list)
    arg_list = np.vstack(arg_list) * np.array(step_list)
    return list(set(arg_list.ravel()))


if __name__ == "__main__":
    currentDirectory = Path().cwd()
    outputPath = currentDirectory
    result_file = currentDirectory / "results.json"
    if result_file.exists():
        bcm = Benchmark(
            pathToInfrastructure=currentDirectory / "repository",
            baseResult=result_file.absolute(),
        )
    else:
        bcm = Benchmark(pathToInfrastructure=currentDirectory / "repository")

    # run = Benchmark(pathToInfrastructure=currentDirectory / "repository")
    bcm.run()

    # print(run.results)
    bcm.result_to_json(result_file.absolute())
