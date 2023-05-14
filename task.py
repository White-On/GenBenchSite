"""Docstring for task.py module.

This module contains the class Task and the differents function to manipulate the Task class.


"""

from dataclasses import dataclass, field
from typing import ClassVar


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
    results: list[float] = field(default_factory=list)
    resultsValue: list[float] = field(default_factory=list)
    arguments_label: list[str] = field(default_factory=list)
    status: str = "NotRun"
    allTasks: ClassVar[list["Task"]] = []

    def __post_init__(self) -> None:
        self.allTasks.append(self)

    def __repr__(self) -> str:
        return f"Task({self.name})-> status: {self.status}"

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
    def GetTaskByName(cls, taskName: str) -> "Task":
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
    def GetAllTaskByName(cls, taskName: str) -> list["Task"]:
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
    def GetAllThemeName(cls) -> list[str]:
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
    def GetTaskByThemeName(cls, themeName: str) -> list["Task"]:
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
