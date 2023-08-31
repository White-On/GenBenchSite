import os
import subprocess
import time
import json
import numpy as np
import ast
from tqdm import tqdm
from pathlib import Path

from genbenchsite.src.logger import logger
from genbenchsite.src.structure_test import StructureTest


class Benchmark:
    """
    Benchmark is a class that run process for each library and each task and save the results in a json file

    We expect a very specific infrastucture of file and folder in order to run the test. The infrastucture is the following:
    - pathToInfrastructure
        - targets
            - config.ini
        - tasks
            - task1
                - config.ini
                - [<beforeBuildScript>]
                - [<libraryScript>] *
                - [file(data)]
            - task2
            [...]

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
    DEBUG = True

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
        self.libraryConfig = self.GetLibraryConfig()
        self.taskConfig = self.GetTaskConfig()
        self.themeConfig = self.GetThemeConfig()
        self.benchmark_config = self.GetBenchmarkConfig()

        logger.info(
            f"Library config retrieved: list of library {self.libraryConfig.keys()}"
        )
        logger.info(f"Task config retrieved: list of task {self.taskConfig.keys()}")
        logger.info(f"Theme config retrieved: list of theme {self.themeConfig.keys()}")

        themeDirectory = self.pathToInfrastructure / "themes"

        self.libraryNames = self.libraryConfig.keys()
        self.themeNames = [
            theme.name for theme in themeDirectory.iterdir() if theme.is_dir()
        ]

        self.taskNames = []
        self.dictionaryTaskInTheme = {}
        self.dictonaryThemeInTask = {}

        # create a dictionary that associate a theme to a list of task afnd a dictionary
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
        order = []
        for themeName in self.themeNames:
            theme_config = self.themeConfig.get(themeName)

            if theme_config is None:
                continue

            order_in_theme = theme_config.get("task_order")
            if order_in_theme is None:
                continue
            order_in_theme = order_in_theme.split(",")
            for taskName in order_in_theme:
                order.append(
                    taskName.strip()
                ) if taskName.strip() in self.taskNames else None
        # we add the remaining tasks not yet added to the order
        for taskName in self.taskNames:
            if taskName not in order:
                order.append(taskName)

        self.taskNames = order

        # look for deactivated tasks
        deactivatedTasks = []
        for taskName in self.taskNames:
            if self.taskConfig[taskName].get("active") == "False":
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

        logger.debug(f"{self.dictionaryTaskInTheme = }")
        logger.debug(f"{self.dictonaryThemeInTask = }")

        # logger.debug(f"{self.results = }")
        logger.debug(f"{self.create_base_json() = }")

    def Setup_Global_Variables(self):
        Benchmark.DEBUG = eval(self.benchmark_config.get("debug", Benchmark.DEBUG))
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
            results = json.load(f)

        return results

    def create_base_json(self):
        """
        create the base json file structure if the json file does not exist

        """
        return {
            libraryName: {
                taskName: {
                    "theme": self.dictonaryThemeInTask[taskName],
                    "results": {
                        arg: {"runtime": []}
                        for arg in self.taskConfig[taskName].get("arguments").split(",")
                    },
                }
                for taskName in self.taskNames
            }
            for libraryName in self.libraryNames
        }

    def GetLibraryConfig(self):
        """
        get the library config from the config.ini file in the targets folder
        """
        strtest = StructureTest()
        libraryConfig = strtest.read_config(
            *strtest.find_config_file(self.pathToInfrastructure / "targets")
        )
        return libraryConfig

    def GetTaskConfig(self):
        """
        get the task config from the config.ini file in each task folder
        """
        strTest = StructureTest()
        listTaskpath = strTest.find_config_file(self.pathToInfrastructure / "themes")
        taskConfig = strTest.read_config(*listTaskpath)
        return taskConfig

    def GetThemeConfig(self):
        """
        get the theme config from the config.ini file in each theme folder
        """
        strTest = StructureTest()
        listThemepath = strTest.find_config_file(
            self.pathToInfrastructure / "themes", name="theme.ini"
        )
        themeConfig = strTest.read_config(*listThemepath)
        return themeConfig

    def GetBenchmarkConfig(self):
        """
        get the benchmark config from the config.ini file in the root folder
        """
        strTest = StructureTest()
        listBenchmarkpath = strTest.find_config_file(
            self.pathToInfrastructure / "config", name="config.ini"
        )
        benchmarkConfig = strTest.read_config(
            *listBenchmarkpath, listSection=["benchmark"]
        )
        return benchmarkConfig["config"]

    def BeforeBuildLibrary(self):
        """
        run the beforeBuild command of each library
        ussually used to build or update the library before running the task

        """
        logger.info(
            "Before build library ( we run the beforeBuild command of each library )"
        )
        for libraryName in self.libraryNames:
            process = subprocess.run(
                self.libraryConfig[libraryName].get("before_build"),
                shell=True,
                capture_output=True,
            )

            if process.returncode != 0:
                logger.error(f"Error in the beforeBuild command of {libraryName}")
                logger.debug(f"{process.stderr = }")
                raise Exception(
                    f"Error in the beforeBuild command of {libraryName} : {process.stderr}"
                )
            else:
                logger.info(f"Before build of {libraryName} done")

    def ExecuteFunctionInModule(self, module, funcName, **kwargs):
        """
        Execute a function in a module with the given arguments

        Parameters
        ----------
        module : str
            name of the module
        funcName : str
            name of the function
        kwargs : dict
            arguments of the function

        """
        logger.debug(f"Execute function {funcName} in module {module} with {kwargs}")
        res = None
        # first we check if the module exist
        if not os.path.exists(module.replace(".", os.sep) + ".py"):
            logger.warning(f"Module {module} does not exist")
            return Benchmark.NOT_RUN_VALUE
        try:
            module = __import__(module, fromlist=[funcName])
            func = getattr(module, funcName)
            res = func(**kwargs)
        except Exception as e:
            logger.warning(f"Error in the evaluation function {funcName}")
            logger.debug(f"{e = }")
            res = Benchmark.ERROR_VALUE
        finally:
            return res

    def BeforeTask(self, taskPath: str, taskName: str):
        """
        Run the before task command/script of a task if it exist

        Parameters
        ----------
        taskPath : str
            path to the task
        taskName : str
            name of the task

        """
        # check if the task has a before task command/script
        beforeTaskModule = self.taskConfig[taskName].get("before_script", None)
        # if the task has no before task command/script we do nothing
        if beforeTaskModule is None:
            logger.info(f"No before task command/script for {taskName}")
            return

        logger.info(f"Before task of {taskName}")

        # the before task is a function in a module
        funcName = self.taskConfig[taskName].get("before_function", None)
        logger.debug(f"{funcName = }")
        if funcName is None:
            logger.error(
                f"No function for the before task command/script for {taskName}"
            )
            return

        # the beforetask may have some arguments
        kwargs = self.taskConfig[taskName].get("before_task_arguments", "{}")
        kwargs = ast.literal_eval(kwargs)
        logger.debug(f"{kwargs = }")
        if len(kwargs) == 0:
            logger.warning(
                f"No arguments for the before task command/script for {taskName}"
            )

        # we import the module and run the function
        relativePath = os.path.relpath(
            taskPath, os.path.dirname(os.path.abspath(__file__))
        ).replace(os.sep, ".")

        # relative_module = __import__(f"{relativePath}.{beforeTaskModule}", fromlist=[funcName])
        # func = getattr(module, funcName)

        # logger.debug(f"{module.__name__ = }")
        # logger.debug(f"{func.__name__ = }")

        # try:
        #     func(**kwargs)
        # except Exception as e:
        #     logger.warning(f"Error in the evaluation function {funcName} of {taskName}")
        #     logger.debug(f"{e = }")

        # the before task should'nt return anything
        self.ExecuteFunctionInModule(
            f"{relativePath}.{beforeTaskModule}", funcName, **kwargs
        )

    def EvaluationAfterTask(
        self, moduleEvaluation, taskName: str, taskPath: str, *funcEvaluation, **kwargs
    ):
        """
        Run the evaluation function of a task

        Parameters
        ----------
        moduleEvaluation : str
            name of the module containing the evaluation function
        taskName : str
            name of the task
        taskPath : str
            path to the task
        funcEvaluation : str
            name of the evaluation function
        kwargs : dict
            arguments of the evaluation function

        """
        valueEvaluation = []

        if len(funcEvaluation) == 0:
            logger.warning(f"No evaluation function for {taskName}")
            return valueEvaluation

        # we need a relative path to import the module with os.sep replaced by .
        relativePath = os.path.relpath(
            taskPath, os.path.dirname(os.path.abspath(__file__))
        ).replace(os.sep, ".")

        for funcName in funcEvaluation:
            # command = f"{self.taskConfig[taskName].get('evaluation_language')} {os.path.join(taskPath,script)} {libraryName} {arg}"

            logger.debug(
                f"Run the evaluation function {funcName} of {moduleEvaluation} for {taskName} with {kwargs}"
            )

            # relative_module = __import__(
            #     f"{relativePath}.{moduleEvaluation}", fromlist=[funcName]
            # )
            # try:
            #     logger.debug(f"{module = }")
            #     func = getattr(module, funcName)
            #     logger.debug(f"{func = }")
            #     output = func(**kwargs)
            # except Exception as e:
            #     logger.warning(
            #         f"Error in the evaluation function {funcName} of {taskName}"
            #     )
            #     logger.debug(f"{e = }")
            #     output = Benchmark.ERROR_VALUE
            output = self.ExecuteFunctionInModule(
                f"{relativePath}.{moduleEvaluation}", funcName, **kwargs
            )
            logger.debug(f"{output = }")
            valueEvaluation.append(output)

        return valueEvaluation

    def RunProcess(self, command, timeout, getOutput=False):
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
            return Benchmark.TIMEOUT_VALUE
        end = time.perf_counter()

        logger.debug(f"{process.stdout = }")
        logger.debug(f"{process.stderr = }")
        logger.debug(f"{process.returncode = }")

        if process.returncode == 1:
            logger.warning(f"Error in the command")
            return Benchmark.ERROR_VALUE

        elif process.returncode == 2:
            logger.warning(f"Can't run this command")
            return Benchmark.NOT_RUN_VALUE

        if getOutput:
            return process.stdout

        return end - start

    def CreateScriptName(self, libraryName: str, nameComplement="") -> str:
        """
        Create the name of the script that will be run for each library and task
        """
        suffix = {"python": "py", "java": "java", "c": "c", "c++": "cpp"}
        return f"{libraryName}{nameComplement}.{suffix[self.libraryConfig[libraryName].get('language', 'python')]}"

    def ScriptExist(self, scriptPath: str, scriptName: str) -> bool:
        """
        Check if the script exist in the path
        """
        script = Path(scriptPath) / scriptName
        return script.exists() and script.is_file()

    def RunTask(self, taskName: str):
        """
        Run the task for each library and save the results in the results dictionary
        """
        path = (
            self.pathToInfrastructure
            / "themes"
            / self.dictonaryThemeInTask[taskName]
            / taskName
        )

        #    We check if the before task command/script exist if not we do nothing
        beforeTaskModule = self.taskConfig[taskName].get("before_script", None)
        if beforeTaskModule is not None:
            self.BeforeTask(path, taskName)
        else:
            logger.info(f"No before task command/script for {taskName}")

        # The timeout of the task is the timeout in the config file or the default timeout
        # the timeout is in seconds
        taskTimeout = int(
            self.taskConfig[taskName].get("timeout", Benchmark.DEFAULT_TIMEOUT)
        )

        for libraryName in self.libraryNames:
            self.progressBar.set_description(
                f"Run task {taskName} for library {libraryName}"
            )

            self.RunTaskForLibrary(libraryName, taskName, path, timeout=taskTimeout)

    def TaskNotSupported(self, libraryName: str, taskName: str, arguments: str) -> None:
        # if task not supported by the target,
        # we add the results to the results dictionary with the value NOT_RUN_VALUE
        self.results[libraryName][taskName]["results"] = {
            arg: {"runtime": Benchmark.NOT_RUN_VALUE} for arg in arguments
        }
        # Progress bar update
        self.progressBar.update(
            int(self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS))
            * len(arguments)
            * 2
        )  # *2 because we have before and after run script

    def RunTaskForLibrary(
        self, libraryName: str, taskName: str, taskPath: str, timeout: int
    ):
        arguments = self.taskConfig[taskName].get("arguments").split(",")

        # we check if the library support the task
        if not self.ScriptExist(taskPath, self.CreateScriptName(libraryName, "_run")):
            self.TaskNotSupported(libraryName, taskName, arguments)
            return

        logger.info(f"Run task {taskName} for library {libraryName}")

        # we check if there is a before run script
        before_run_script_exist = self.ScriptExist(
            taskPath, self.CreateScriptName(libraryName, "_before_run")
        )

        # we check if there is a after run script
        after_run_script = self.taskConfig[taskName].get("evaluation_script", None)

        stop_after_x_timeout = int(
            self.taskConfig[taskName].get(
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
                self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS)
            )

            for cpt_run in range(total_run):
                logger.debug(
                    f"Run {cpt_run + 1} of {total_run} for {taskName}. At {cpt_timeout} timeout"
                )

                # Before run script
                if before_run_script_exist:
                    if cpt_timeout >= stop_after_x_timeout:
                        resultProcess = Benchmark.TIMEOUT_VALUE
                    else:
                        language = self.libraryConfig[libraryName].get("language")
                        path_script = Path(
                            taskPath, self.CreateScriptName(libraryName, "_before_run")
                        )
                        command = f"{language} {path_script} {arg}"

                        resultProcess = self.RunProcess(
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

                # Run script
                if cpt_timeout >= stop_after_x_timeout:
                    resultProcess = Benchmark.TIMEOUT_VALUE
                else:
                    scriptName = self.CreateScriptName(libraryName, "_run")
                    language = self.libraryConfig[libraryName].get("language")
                    path_script = Path(taskPath, scriptName)

                    command = f"{language} {path_script} {arg}"

                    resultProcess = self.RunProcess(
                        command=command,
                        timeout=timeout + resultProcess
                        if before_run_script_exist
                        and not isinstance(resultProcess, str)
                        else timeout,
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

                # After run script
                if after_run_script is not None:
                    # if the script is not None, then it should be a script name or a list of script name
                    functionEvaluation = self.taskConfig[taskName].get(
                        "evaluation_function", None
                    )
                    if functionEvaluation is not None:
                        functionEvaluation = functionEvaluation.split(" ")
                    else:
                        functionEvaluation = []

                    logger.debug(f"{functionEvaluation = }")

                    # if the task has  been run successfuly we run the evaluation function
                    if not isinstance(resultProcess, str):
                        valueEvaluation = self.EvaluationAfterTask(
                            after_run_script,
                            taskName,
                            taskPath,
                            *functionEvaluation,
                            libraryName=libraryName,
                            arg=arg,
                            **eval(
                                self.taskConfig[taskName].get(
                                    "evaluation_arguments", {}
                                )
                            ),
                        )
                        logger.debug(f"{valueEvaluation = }")
                    # if not we add the value ERROR_VALUE to the evaluation function
                    else:
                        valueEvaluation = [resultProcess] * len(functionEvaluation)
                    evaluation_result = self.results[libraryName][taskName]["results"][
                        arg
                    ].get("evaluation", {})
                    for i, function in enumerate(functionEvaluation):
                        element = evaluation_result.get(function, [])
                        evaluation_result = {
                            **evaluation_result,
                            function: element + [valueEvaluation[i]],
                        }
                    self.results[libraryName][taskName]["results"][arg][
                        "evaluation"
                    ] = evaluation_result

            self.results[libraryName][taskName]["results"][arg]["runtime"].extend(
                [b, t] for b, t in zip(before_run_list_time, listTime)
            )

        logger.info(f"End task {taskName} for library {libraryName}")

    def CalculNumberIteration(self):
        """
        Calculate the number of iteration for the progress bar
        """
        nbIteration = 0
        for taskName in self.taskNames:
            nbIteration += (
                int(self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS))
                * len(self.taskConfig[taskName].get("arguments").split(","))
                * 2
                * len(self.libraryNames)
            )  # Nb runs * nb arguments * 2 (before run and after run) * nb libraries

        logger.info(f"Number of commands : {nbIteration}")
        return nbIteration

    def ConvertResultToJson(self, outputFileName="results.json"):
        """
        convert the result to a json file
        """
        with open(outputFileName, "w") as file:
            json.dump(self.results, file, indent=4)
        logger.info(f"Result saved in {outputFileName}")

    def StartAllProcedure(self):
        self.Setup_Global_Variables()
        if not Benchmark.DEBUG:
            self.BeforeBuildLibrary()

        self.progressBar = tqdm(
            total=self.CalculNumberIteration(),
            desc="Initialization",
            ncols=150,
            position=0,
        )
        logger.info("=======Begining of the benchmark=======")
        for taskName in self.taskNames:
            self.RunTask(taskName)
        logger.info("=======End of the benchmark=======")


if __name__ == "__main__":
    currentDirectory = Path(__file__).parent.absolute()
    outputPath = currentDirectory
    result_file = currentDirectory / "results.json"
    if result_file.exists():
        run = Benchmark(
            pathToInfrastructure=currentDirectory / "repository",
            baseResult=result_file.absolute(),
        )
    else:
        run = Benchmark(pathToInfrastructure=currentDirectory / "repository")

    # run = Benchmark(pathToInfrastructure=currentDirectory / "repository")
    run.StartAllProcedure()

    # print(run.results)
    run.ConvertResultToJson(result_file.absolute())
