"""Docstring for task.py module.

This module contains the class Task and the differents function to manipulate the Task class.

"""

from dataclasses import dataclass, field
from typing import ClassVar
import numpy as np
from logger import logger

MIN_RUNTIME_POSSIBLE = 0.0001


@dataclass
class Task:
    """
    Store all the information about all the tasks created.

    Attributes
    ----------
    name : str
        The name of the task.
    theme : str
        The theme of the task.
    arguments : list of float
        The list of the arguments of the task. The index of the argument correspond to the index of the result.
    results : list of float
        The list of the results of the task. The index of the result correspond to the index of the argument.
    allTasks : list of Task
        Class Atribute ! The list of all the tasks created.

    """

    name: str
    theme: str
    arguments: list[float] = field(default_factory=list)
    runtime: dict[str, list[float]] = field(default_factory=dict)
    evaluation: dict[str, list[float]] = field(default_factory=dict)
    evaluation_function_name: list[str] = field(default_factory=list)
    evaluation_sort_order: list[str] = field(default_factory=list)
    arguments_label: list[str] = field(default_factory=list)
    cache_runtime: dict[str, list[float]] = field(default_factory=dict)
    cache_evaluation: dict[str, list[float]] = field(default_factory=dict)
    allTasks: ClassVar[list["Task"]] = []

    def __post_init__(self) -> None:
        logger.debug(f"Task {self.name} created")
        Task.allTasks.append(self)

    def __repr__(self) -> str:
        return f"Task({self.name})-> arguments: {self.arguments_label}"

    @classmethod
    def GetAllTask(cls) -> list["Task"]:
        """Getter for all the tasks created.

        Returns
        -------
        list of Task
            The list of all the tasks created.

        """
        return cls.allTasks

    @classmethod
    def GetAllTaskName(cls) -> list[str]:
        """Getter for all the tasks name created.

        Returns
        -------
        listtaskName : list of str
            The list of all the tasks name created.

        """
        listTaskName = []
        for task in cls.allTasks:
            if task.name not in listTaskName:
                listTaskName.append(task.name)
        return listTaskName

    @classmethod
    def GetTaskByName(cls, taskName: str) -> "Task" or None:
        """Getter for a task by its name.

        Parameters
        ----------
        taskName : str
            The name of the task to get.

        Returns
        -------
        task : Task
            The task with the name given in parameter.

        """
        for task in cls.allTasks:
            if task.name == taskName:
                return task
        return None

    @classmethod
    def GetAllTaskByName(cls, taskName: str):
        """Getter for all the tasks with the same name.

        Parameters
        ----------
        taskName : str
            The name of the task to get.

        Returns
        -------
        list of Task
            The list of all the tasks with the same name.

        """
        return (task for task in cls.allTasks if task.name == taskName)

    @classmethod
    def GetAllThemeName(cls):
        """Getter for all the theme name created.

        Returns
        -------
        listThemeName : list of str
            The list of all the theme name created.

        """
        listThemeName = []
        for task in cls.GetAllTask():
            if task.theme not in listThemeName:
                listThemeName.append(task.theme)
        return listThemeName

    @classmethod
    def GetTaskByThemeName(cls, themeName: str):
        """Getter for all the tasks with the same theme name.

        Parameters
        ----------
        themeName : str
            The name of the theme to get.

        Returns
        -------
        list of Task
            The list of all the tasks with the same theme name.

        """
        return (task for task in cls.GetAllTask() if task.theme == themeName)

    @classmethod
    def GetTaskNameByThemeName(cls, themeName: str) -> list[str]:
        """Getter for all the tasks name with the same theme name.

        Parameters
        ----------
        themeName : str
            The name of the theme to get.

        Returns
        -------
        list of str
            The list of all the tasks name with the same theme name.

        """
        listTaskName = []
        for task in cls.GetTaskByThemeName(themeName):
            if task.name not in listTaskName:
                listTaskName.append(task.name)
        return listTaskName

    @staticmethod
    def str_and_none_to_nan(array: np.ndarray) -> np.ndarray:
        """transform the string and None into np.nan inside an array and transform the array into float64"""

        def is_float(string: str):
            """return True if the string is a float, False otherwise"""
            try:
                float(string)
                return True
            except ValueError:
                return False

        return np.where(
            np.vectorize(lambda x: x is None or not is_float(x))(array), np.nan, array
        ).astype(np.float64)

    def get_runtime(self, target: str) -> list[float]:
        # for element in self.runtime[target]:
        #     print(len(element))
        #     print(element)
        # print(self.runtime[target])
        # we transform the string and None into np.nan and transform the array into float64
        runtime = Task.str_and_none_to_nan(np.array(self.runtime[target]))
        # if there is no runtime for the target, we return a list of np.nan with the same size as the arguments
        if (np.isnan(runtime)).all():
            # problem with the shape of the array
            return np.vstack(runtime).tolist()
            # return np.hstack(runtime).tolist()
        # we inverse the runtime to have the difference between the end and the start (end - start)
        runtime = np.hstack(np.diff(runtime, axis=2)).T
        # we adapt the value if the runtime is negative
        runtime = np.where(runtime <= 0, MIN_RUNTIME_POSSIBLE, runtime)
        logger.debug(f"Runtime for {target} in {self.name} : {runtime}")
        return runtime.tolist()

    def get_evaluation(self, target: str) -> list[float]:
        # if there is no evaluation for the target, we return a list of np.nan with the same size as the arguments
        if len(self.evaluation_function_name) == 0:
            evaluation = [float("inf")] * len(self.arguments_label)
            logger.debug(f"Evaluation for {target} in {self.name} : {evaluation}")
            return evaluation

            # if self.evaluation[target] is None:
            #     # the evaluation is a error message
            #     evaluation = [float("inf")] * len(self.arguments_label)
            #     logger.debug(f"Evaluation for {target} in {self.name} : {evaluation}")
            return evaluation

        evaluation = self.evaluation[target][:]
        for i in range(len(evaluation)):
            for function in evaluation[i].keys():
                # we transform the string and None into np.nan and transform the array into float64 to be able to do computation
                evaluation[i][function] = Task.str_and_none_to_nan(
                    evaluation[i][function]
                )
                # if the evaluation is a list of string or None, that means that all the evaluation failed
                if np.isnan(evaluation[i][function]).all():
                    evaluation[i][function] = float("inf")
                else:
                    evaluation[i][function] = evaluation[i][function].tolist()
        return evaluation

    def mean_runtime(self, target: str) -> list[float]:
        if target in self.cache_runtime:
            logger.debug(
                f"Evaluation already calculated for {target} in {self.name}, using the cached value"
            )
            return self.cache_runtime[target]
        runtime = self.get_runtime(target)
        # print(runtime)
        runtime = np.nanmean(runtime, axis=1)
        runtime[np.isnan(runtime)] = float("inf")
        logger.debug(f"Runtime for {target} in {self.name} : {runtime}")
        # we save the runtime in the cache
        self.cache_runtime[target] = runtime.tolist()
        return runtime.tolist()

    def mean_evaluation(self, target: str) -> list[float]:
        if target in self.cache_evaluation:
            logger.debug(
                f"Evaluation already calculated for {target} in {self.name}, using the cached value"
            )
            return self.cache_evaluation[target]
        evaluation = []
        for element in self.get_evaluation(target):
            if element == float("inf"):
                evaluation.append(element)
                continue
            evaluation.append(element.copy())
        for i in range(len(evaluation)):
            if evaluation[i] == float("inf"):
                continue
            for function in evaluation[i].keys():
                evaluation[i][function] = np.nanmean(evaluation[i][function]).tolist()
                if np.isnan(evaluation[i][function]):
                    evaluation[i][function] = float("inf")
        logger.debug(f"Evaluation for {target} in {self.name} : {evaluation}")
        # we save the evaluation in the cache
        self.cache_evaluation[target] = evaluation
        return evaluation

    def standard_deviation_runtime(self, target) -> list[float]:
        std_runtime = np.nanstd(self.get_runtime(target=target), axis=1)
        std_runtime = np.where(std_runtime <= 0, MIN_RUNTIME_POSSIBLE, std_runtime)
        logger.debug(f"Standard deviation for {target} in {self.name} : {std_runtime}")
        return std_runtime.tolist()

    def standard_deviation_evaluation(self, target) -> list[float]:
        evaluation = []
        for element in self.get_evaluation(target):
            if element == float("inf"):
                evaluation.append(element)
                continue
            evaluation.append(element.copy())
        # evaluation = self.get_evaluation(target)[:]
        for i in range(len(evaluation)):
            if evaluation[i] == float("inf"):
                continue
            for function in evaluation[i].keys():
                evaluation[i][function] = np.nanstd(evaluation[i][function]).tolist()
        return evaluation

    def variance(self, target) -> list[float]:
        return np.nanvar(self.get_runtime(target=target), axis=1).tolist()

    def get_status(self, target: str) -> str:
        """Getter for the status of the task.

        Returns
        -------
        status : str
            The status of the task.

        """
        mean = np.array(self.mean_runtime(target))
        if (mean == float("inf")).all():
            if isinstance(self.runtime[target][0], str):
                # the runtime is a error message
                return self.runtime[target][0]
            else:
                # we want to find the first error message
                return self.runtime[target][0][0][1]
        return "Run"


if __name__ == "__main__":
    from json_to_python_object import FileReaderJson

    FileReaderJson("results.json")

    print(Task.GetAllTaskName())
