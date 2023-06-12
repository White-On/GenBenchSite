"""Docstring for json_to_python_object.py.

This module contains the function to read a json file and create the python object.

"""

import json
from library import Library
from task import Task
from logger import logger

def FileReaderJson(filename: str) -> None:
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
    data = readJsonFile(filename)

    for libName, libInfo in data.items():
        library = Library(libName)
        for taskName, taskInfo in libInfo.items():
            task = Task(taskName, taskInfo["theme"]) if taskName not in Task.GetAllTaskName() else Task.GetTaskByName(taskName)
            logger.info(f"Task {taskName} with {libName} library")
            logger.debug(f"arguments: {len(taskInfo['results'].keys())}")

            task.arguments_label = [argument for argument in taskInfo["results"].keys()]
            # transform the argument label into a list of index to be able to use the LexMax algorithm
            task.arguments.extend(TokenizeArguments(task.arguments_label))

            runtime = [taskInfo['results'].get(argument).get('runtime') for argument in task.arguments_label]
            evaluation = [taskInfo['results'].get(argument).get('evaluation')for argument in task.arguments_label]
            
            task.runtime[libName] = runtime
            task.evaluation[libName] = evaluation
            
            library.tasks.append(task)


def TokenizeArguments(arguments: list[str]) -> list[int]:
    return [index for index, _ in enumerate(arguments)]


def readJsonFile(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)

    return data


if __name__ == "__main__":

    FileReaderJson("results.json")

    print(Task.GetAllTaskName())

    print(list(Library.GetAllLibraryName()))

    task = Task.allTasks[0]
    print(task.name)    
    print(task.get_calculated_runtime("pyAgrum"))
   
