"""Docstring for Library.py module.

This module contains the class Library and the differents function to manipulate the Library class.

"""

from dataclasses import dataclass, field
from typing import ClassVar

from .task import Task


@dataclass
class Library:
    """Store all the information about all the libraries created.

    Attributes
    ----------
    name : str
        The name of the library.
    tasks : list of Task
        The list of the tasks of the library.
    allLibrary : list of Library
        Class Attribute ! The list of all the libraries created.

    """

    name: str
    tasks: list[Task] = field(default_factory=list)
    allLibrary: ClassVar[list["Library"]] = []

    def __post_init__(self) -> None:
        self.allLibrary.append(self)

    def __repr__(self) -> str:
        return f"Library({self.name})"

    @classmethod
    def GetAllLibrary(cls) -> list["Library"]:
        """Getter for all the libraries created.

        Returns
        -------
        list of Library
            The list of all the libraries created.
        """
        return cls.allLibrary

    @classmethod
    def GetAllLibraryName(cls):
        """Getter for all the libraries name created.

        Returns
        -------
        list of str
            The list of all the libraries name created.
        """
        return (library.name for library in cls.allLibrary)

    @classmethod
    def GetLibraryByTaskName(cls, taskName: str) -> list["Library"]:
        """Getter for all the libraries that contains a task with the name taskName.

        Parameters
        ----------
        taskName : str
            The name of the task to search.

        Returns
        -------
        list of Library
            The list of all the libraries that contains a task with the name taskName.
        """
        libraryList = []
        for library in cls.GetAllLibrary():
            libraryList.extend(
                [library for task in library.tasks if task.name == taskName]
            )
        return libraryList

    @classmethod
    def GetLibraryByName(cls, libraryName: str) -> "Library":
        """Getter for the library with the name libraryName.

        Parameters
        ----------
        libraryName : str
            The name of the library to search.

        Returns
        -------
        Library
            The library with the name libraryName.
        """
        for library in cls.allLibrary:
            if library.name == libraryName:
                return library
        return None

    def GetTaskByName(self, taskName: str) -> Task:
        """Getter for the task with the name taskName in the library.

        Parameters
        ----------
        taskName : str
            The name of the task to search.

        Returns
        -------
        Task
            The task with the name taskName in the library.
        """
        for task in self.tasks:
            if task.name == taskName:
                return task
        return None

    @classmethod
    def GetTaskByLibraryNameAndTaskName(cls, libraryName: str, taskName: str) -> "Task":
        """Getter for the task for a specific name of library and name of task.

        Parameters
        ----------
        libraryName : str
            The name of the library to search.
        taskName : str
            The name of the task to search.

        Returns
        -------
        Task
            The task with the name `taskName` in the library with the name `libraryName`.
        """
        return cls.GetLibraryByName(libraryName).GetTaskByName(taskName)

    @classmethod
    def GetResultsByTaskName(cls, taskName: str) -> dict[str, list[float]]:
        """Getter for the results of all the tasks with the name `taskName`.

        Parameters
        ----------
        taskName : str
            The name of the task to search.

        Returns
        -------
        dict of str and list of float
            The results of all the tasks with the name `taskName`. The key is the name of the library and the value is the list of the results.
        """
        dico = {}
        for library in cls.GetAllLibrary():
            task = library.GetTaskByName(taskName)
            dico[library.name] = task.get_calculated_runtime(library.name)
        return dico

    @classmethod
    def GetArgumentsByTaskName(cls, taskName: str) -> dict[str, list[float]]:
        """Getter for the arguments of all the tasks with the name `taskName`.

        Parameters
        ----------
        taskName : str
            The name of the task to search.

        Returns
        -------
        dict of str and list of float
            The arguments of all the tasks with the name `taskName`. The key is the name of the library and the value is the list of the arguments.
        """
        dico = {}
        for library in cls.GetAllLibrary():
            task = library.GetTaskByName(taskName)
            dico[library.name] = task.arguments
        return dico
