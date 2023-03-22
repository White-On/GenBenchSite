"""Docstring for json_to_python_object.py.

This module contains the function to read a json file and create the python object.

"""

import json
from library import Library
from task import Task

def FileReaderJson(filename: str)-> tuple[list[Library], list[Task]]:
    """Read a json file and create the python object.

    Parameters
    ----------
    filename : str
        The name of the json file.

    Returns
    -------
    tuple[list[Library], list[Task]]
        A tuple with a list of library and a list of task.

    """
    with open(filename, "r") as file:
        data = json.load(file)

    libraryList = []
    taskList = []

    for libName, libInfo in data.items():
        library = Library(libName)
        for taskName, taskInfo in libInfo.items():
            task = Task(taskName, taskInfo["theme"])
            task.arguments.extend([float(argument) for argument in taskInfo["results"].keys()])
            task.results.extend(taskInfo["results"].values())
            library.tasks.append(task)
            taskList.append(task)
        libraryList.append(library)
    
    return libraryList, taskList