from configparser import ConfigParser
import os
import sys
import subprocess
import time
import json
import numpy as np
import ast
from tqdm import tqdm


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

    def __init__(self, pathToInfrastructure: str) -> None:
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
        LibraryConfigReader : ConfigParser
            ConfigParser that will read the config files of the library
        TaskConfigReader : ConfigParser
            ConfigParser that will read the config files of the task

        """

        self.pathToInfrastructure = pathToInfrastructure

        self.LibraryConfigReader = ConfigParser()
        self.TaskConfigReader = ConfigParser()

        targetDirectory = os.path.join(self.pathToInfrastructure, "targets")
        themeDirectory = os.path.join(self.pathToInfrastructure, "themes")

        self.libraryNames = [
            f
            for f in os.listdir(targetDirectory)
            if os.path.isdir(os.path.join(targetDirectory, f))
        ]
        self.themeNames = [
            f
            for f in os.listdir(themeDirectory)
            if os.path.isdir(os.path.join(themeDirectory, f))
        ]

        self.results = {libraryName: {} for libraryName in self.libraryNames}

        self.taskNames = []
        self.dictionaryTaskInTheme = {}
        self.dictonaryThemeInTask = {}

        # We read the config file of each library and task
        # with ConfigParser we can read multiple config file and get the value of a specific section and key
        for libraryName in self.libraryNames:
            self.LibraryConfigReader.read(
                os.path.join(
                    self.pathToInfrastructure, "targets", libraryName, "config.ini"
                )
            )

        # We read the config file of each library and task
        # we also create a dictionary that associate a theme to a list of task and a dictionary that associate a task to a theme
        for themeName in self.themeNames:
            self.taskNames += os.listdir(
                os.path.join(self.pathToInfrastructure, "themes", themeName)
            )
            self.dictionaryTaskInTheme[themeName] = os.listdir(
                os.path.join(self.pathToInfrastructure, "themes", themeName)
            )
            for taskName in self.dictionaryTaskInTheme[themeName]:
                self.TaskConfigReader.read(
                    os.path.join(
                        self.pathToInfrastructure,
                        "themes",
                        themeName,
                        taskName,
                        "config.ini",
                    )
                )
                self.dictonaryThemeInTask[taskName] = themeName

        print(f"Library found {self.LibraryConfigReader.sections()}")
        print(f"Task found {self.TaskConfigReader.sections()}\n")

    def BeforeBuildLibrary(self):
        """
        run the beforeBuild command of each library

        """

        print("Before build library")
        for libraryName in self.libraryNames:
            process = subprocess.run(
                self.LibraryConfigReader.get(libraryName, "before_build"),
                shell=True,
                capture_output=True,
            )

            if process.returncode != 0:
                print(f"Error in the beforeBuild command of {libraryName}")
                print(process.stderr)
                sys.exit(1)
            else:
                print(f"Before build of {libraryName} done")

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
        # We check if the before task command/script exist if not we do nothing
        beforeTaskCommand = self.TaskConfigReader.get(
            taskName, "before_task", fallback=None
        )
        if beforeTaskCommand is not None:
            # the beforetask might have some arguments
            before_task_arguments = self.TaskConfigReader.get(
                taskName, "before_task_arguments", fallback=""
            )
            # We split the command/script and the arguments in oder
            beforeTaskCommand = beforeTaskCommand.split(" ")

            process = subprocess.run(
                [
                    beforeTaskCommand[0],
                    os.path.join(taskPath, beforeTaskCommand[1]),
                    before_task_arguments,
                ],
                shell=True,
                capture_output=True,
            )
            if process.returncode != 0:
                print(f"Error in the beforeBuild command of {taskName}\n")
                print(process.stderr)
                # print(process.stdout)
                # print(process.returncode)
                sys.exit(1)
            else:
                # print(process.stdout)
                # print(f"Before task of {taskName} done")
                # read the config file again because it can be modified by the before task command/script
                self.ReadTaskConfigFile(taskName)

    def ReadTaskConfigFile(self, taskName: str):
        """
        Read the config file of the task and return a dictionary with the config
        """
        self.TaskConfigReader.read(
            os.path.join(
                self.pathToInfrastructure,
                "themes",
                self.dictonaryThemeInTask[taskName],
                taskName,
                "config.ini",
            )
        )

    # def RunProcess(self, command, printOut, timeout):

    #     start = time.perf_counter()

    #     process = subprocess.Popen(command,shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #     # print(f"\nTimeout expired for the {command} command")

    #     # Create an event to signal the timeout
    #     event = threading.Event()

    #     # Start a timer to set the event after the timeout
    #     timer = threading.Timer(timeout, event.set)
    #     timer.start()

    #     # Wait for the subprocess to finish or the timeout to occur
    #     while process.poll() is None and not event.is_set():
    #         # The subprocess is still running and the timeout has not occurred
    #         pass

    #     # Check if the subprocess is still running
    #     if process.poll() is None:
    #         # The subprocess is still running, so we need to kill it
    #         process.kill()
    #         return Benchmark.TIMEOUT_VALUE

    #     # Cancel the timer
    #     timer.cancel()

    #     end = time.perf_counter()
    #     if process.returncode == 1:
    #         # print(f"\nError in the {command} command")
    #         # print(process.stderr)
    #         return Benchmark.ERROR_VALUE

    #     elif process.returncode == 2:
    #         # print(f"\nCan't run this task because the library doesn't support it")
    #         # print(process.stderr)
    #         return Benchmark.NOT_RUN_VALUE

    #     if printOut:
    #         print(process.stdout)

    #     return end-start

    def RunProcess(self, command, printOut, timeout, getOutput=False):
        start = time.perf_counter()
        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            # print(f"\nTimeout expired for the {command} command")
            return Benchmark.TIMEOUT_VALUE
        end = time.perf_counter()

        if printOut:
            print(process.stdout)
            print(process.stderr)

        if process.returncode == 1:
            # print(f"\nError in the {command} command")
            # print(process.stderr)
            return Benchmark.ERROR_VALUE

        elif process.returncode == 2:
            # print(f"\nCan't run this task because the library doesn't support it")
            # print(process.stderr)
            return Benchmark.NOT_RUN_VALUE
        
        if getOutput:
            return process.stdout

        return end - start

    def CreateScriptName(self, libraryName: str, nameComplement="") -> str:
        """
        Create the name of the script that will be run for each library and task
        """
        suffix = {"python": "py", "java": "java", "c": "c", "c++": "cpp"}
        return f"{libraryName}{nameComplement}.{suffix[self.LibraryConfigReader.get(libraryName,'language')]}"

    def ScriptExist(self, scriptPath: str, scriptName: str) -> bool:
        """
        Check if the script exist in the path
        """
        return os.path.exists(os.path.join(scriptPath, scriptName))

    def RunTask(self, taskName: str):
        """
        Run the task for each library and save the results in the results dictionary
        """
        path = os.path.join(
            self.pathToInfrastructure,
            "themes",
            self.dictonaryThemeInTask[taskName],
            taskName,
        )

        # TEMPORAIRE
        self.BeforeTask(path, taskName)

        # The timeout of the task is the timeout in the config file or the default timeout
        # the timeout is in seconds
        taskTimeout = self.TaskConfigReader.getint(
            taskName, "timeout", fallback=Benchmark.DEFAULT_TIMEOUT
        )

        for libraryName in self.libraryNames:
            self.results[libraryName][taskName] = {}
            self.results[libraryName][taskName]["theme"] = self.dictonaryThemeInTask[
                taskName
            ]
            self.results[libraryName][taskName]["results"] = {}

            self.progressBar.set_description(
                f"Run task {taskName} for library {libraryName}"
            )

            self.RunTaskForLibrary(libraryName, taskName, path, timeout=taskTimeout)

    def RunTaskForLibrary(
        self, libraryName: str, taskName: str, taskPath: str, timeout: int
    ):
        arguments = self.TaskConfigReader.get(taskName, "arguments").split(",")

        # we check if the library support the task
        if not self.ScriptExist(taskPath, self.CreateScriptName(libraryName, "_run")):
            self.results[libraryName][taskName]["results"] = {
                arg: (Benchmark.NOT_RUN_VALUE, None) for arg in arguments
            }
            self.progressBar.update(
                self.TaskConfigReader.getint(taskName, "nb_runs") * len(arguments) * 2
            )  # *2 because we have before and after run script
            return

        # we check if there is a before run script
        beforeRunScriptExist = self.ScriptExist(
            taskPath, self.CreateScriptName(libraryName, "_before_run")
        )
        if not beforeRunScriptExist:
            beforeRunListTime = [0]

        # we check if there is a after run script
        afterRunScript = self.TaskConfigReader.get(taskName, "evaluation_script",fallback=None)
        if afterRunScript is not None:
            afterRunScript = afterRunScript.split(",")

        for arg in arguments:
            # print(f"Run task {conf.get('task_properties','name')} of library {libraryName} with argument {arg}")

            listTime = []
            if beforeRunScriptExist:
                beforeRunListTime = []

            numberRun = self.TaskConfigReader.getint(taskName, "nb_runs")

            for nb_run in range(numberRun):
                # Before run script
                if beforeRunScriptExist:
                    command = f"{self.LibraryConfigReader.get(libraryName,'language')} {os.path.join(taskPath,self.CreateScriptName(libraryName,'_before_run'))} {arg}"
                    resultProcess = self.RunProcess(
                        command=command, printOut=False, timeout=timeout
                    )
                    beforeRunListTime.append(resultProcess)
                    self.progressBar.update(1)
                    if isinstance(resultProcess, str):
                        listTime.append(resultProcess)
                        self.progressBar.update((numberRun - nb_run) * 2 - 1)
                        break

                # Run script
                scriptName = self.CreateScriptName(libraryName, "_run")
                language = self.LibraryConfigReader.get(libraryName, "language")

                command = f"{language} {os.path.join(taskPath,scriptName)} {arg}"

                resultProcess = self.RunProcess(
                    command=command, printOut=False, timeout=timeout
                )
                listTime.append(resultProcess)
                self.progressBar.update(1)
                if isinstance(resultProcess, str):
                    self.progressBar.update((numberRun - nb_run - 1) * 2)
                    break

            valueEvaluation = None
            # After run script
            if afterRunScript is not None:
                # if the script is not None, then it should be a script name or a list of script name
                valueEvaluation = []
                for script in afterRunScript:
                    command = f"{self.TaskConfigReader.get(taskName,'evaluation_language')} {os.path.join(taskPath,script)} {libraryName} {arg}"
                    output = self.RunProcess(command=command, printOut=False, timeout=20, getOutput=True)
                    if(output in [Benchmark.NOT_RUN_VALUE, Benchmark.ERROR_VALUE, Benchmark.DEFAULT_VALUE, Benchmark.TIMEOUT_VALUE]):
                        output = "None"
                    valueEvaluation.append(ast.literal_eval(output))                
                    

            # we remove the error and timeout values to calculate the mean
            filteredListTime = [
                x for x in listTime if isinstance(x, float) or isinstance(x, int)
            ]
            filteredListBeforeRunTime = [
                x
                for x in beforeRunListTime
                if isinstance(x, float) or isinstance(x, int)
            ]
            # If there is no value in the list, we take the first value even if it is an error or a timeout
            if len(filteredListTime) != 0:
                # TEMPORAIRE
                self.results[libraryName][taskName]["results"][arg] = (
                    np.mean(filteredListTime) - np.mean(filteredListBeforeRunTime),
                    valueEvaluation,
                )
                # self.results[libraryName][taskName]["results"][arg] = np.mean(filteredListTime) - np.mean(filteredListBeforeRunTime)
            else:
                self.results[libraryName][taskName]["results"][arg] = (
                    listTime[0],
                    valueEvaluation,
                )

            # # print(f"{valueResult = }")
            # # print(f"{valueBeforeRun = }")

    def CalculNumberIteration(self):
        """
        Calculate the number of iteration for the progress bar
        """
        nbIteration = 0
        for taskName in self.TaskConfigReader.sections():
            nbIteration += (
                self.TaskConfigReader.getint(taskName, "nb_runs")
                * len(self.TaskConfigReader.get(taskName, "arguments").split(","))
                * 2
                * len(self.libraryNames)
            )  # Nb runs * nb arguments * 2 (before run and after run) * nb libraries
            # print(f"{len(self.TaskConfigReader.get(taskName,'arguments').split(',')) = }")
            # print(f"{nbIteration = }")
        return nbIteration

    def ConvertResultToJson(
        self, outputPath: str = None, outputFileName: str = "results"
    ):
        """
        convert the result to a json file
        """
        if outputPath is None:
            outputPath = self.pathToInfrastructure

        with open(outputFileName, "w") as file:
            json.dump(self.results, file, indent=4)

    def StartAllProcedure(self):
        self.BeforeBuildLibrary()

        self.progressBar = tqdm(
            total=self.CalculNumberIteration(), desc="Initialization", ncols=100
        )
        for taskName in self.taskNames:
            self.RunTask(taskName)


if __name__ == "__main__":
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    outputPath = currentDirectory
    run = Benchmark(pathToInfrastructure=os.path.join(currentDirectory, "repository"))
    run.StartAllProcedure()

    print(run.results)
    run.ConvertResultToJson(outputPath=outputPath)
