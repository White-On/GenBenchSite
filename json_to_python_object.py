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
            task.arguments_label.extend([argument for argument in taskInfo["results"].keys()])
            # transform the argument label into a list of index to be able to use the LexMax algorithm
            task.arguments.extend(TokenizeArguments(task.arguments_label))
            # print(taskInfo["results"].values())
            resultsTime = [result[0] for result in taskInfo["results"].values()]
            resultsValue = [result[1] for result in taskInfo["results"].values()]
            task.results.extend([float(result) if isinstance(result, float) or isinstance(result, int) else float("infinity") for result in resultsTime])
            task.resultsValue.extend([float(result) if result is not None else float("infinity") for result in resultsValue])
            task.status = resultsTime[0] if all([r == float("infinity") for r in task.results]) else "Run"
            library.tasks.append(task)
            taskList.append(task)
        libraryList.append(library)
    
    return libraryList, taskList

def TokenizeArguments(arguments: list[str]) -> list [int]:
    return [index  for index, argument in enumerate(arguments)]


if __name__ == "__main__":
    from json_to_python_object import FileReaderJson

    _ = FileReaderJson("data.json")

    print(list(Task.GetTaskNameByThemeName("Theme1")))