"""Docstring for json_to_python_object.py.

This module contains the function to read a json file and create the python object.

"""
import json
from .library import Library
from .task import Task
from .logger import logger
from .structure_test import get_task_config


def FileReaderJson(filename: str, structure_test_path: str) -> None:
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
    taskConfig = get_task_config(structure_test_path)

    for libName, libInfo in data.items():
        library = Library(libName)
        for taskName, taskInfo in libInfo.items():
            task = (
                Task(taskName, taskInfo["theme"])
                if taskName not in Task.GetAllTaskName()
                else Task.GetTaskByName(taskName)
            )
            if task.name not in taskConfig:
                logger.error(f"Task {task.name} not found in the task.ini file, maybe an errer in the naming of the files")
                continue
            logger.info(f"Task {taskName} with {libName} library")
            logger.debug(f"arguments: {len(taskInfo['results'].keys())}")

            task.arguments_label = [argument for argument in taskInfo["results"].keys()]
            # transform the argument label into a list of index to be able to use the LexMax algorithm
            task.arguments.extend(TokenizeArguments(task.arguments_label))

            runtime = [
                taskInfo["results"].get(argument).get("runtime")
                for argument in task.arguments_label
            ]
            evaluation = [
                taskInfo["results"].get(argument).get("evaluation")
                for argument in task.arguments_label
            ]
            if evaluation[0] is None:
                evaluation = None

            task.runtime[libName] = runtime
            task.evaluation[libName] = evaluation
            evaluation_function_name = taskConfig[task.name].get("evaluation_titles")
            if evaluation_function_name:
                task.evaluation_function_name = evaluation_function_name.split(",")
                task.evaluation_sort_order = taskConfig[task.name].get(
                    "evaluation_sort_order"
                )
                if task.evaluation_sort_order:
                    task.evaluation_sort_order = task.evaluation_sort_order.split(",")
                else:
                    task.evaluation_sort_order = [
                        "desc" for _ in range(len(task.evaluation_function_name))
                    ]

            library.tasks.append(task)


def TokenizeArguments(arguments: list[str]) -> list[int]:
    return [index for index, _ in enumerate(arguments)]


def readJsonFile(filename: str):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        data = None

    return data


def count_test():
    # we tak a task at random
    task = Task.allTasks[0]
    # we take a library at random
    library = Library.allLibrary[0]
    # we take the first runtime of the task
    runtime = task.runtime[library.name][0]
    return len(runtime)


if __name__ == "__main__":
    FileReaderJson("results.json")
    # FileReaderJson("essais.json")

    # print(Task.GetAllTaskName())

    # print(list(Library.GetAllLibraryName()))

    tasks = Task.allTasks
    for task in tasks:
        # print(task.name)
        # print(task.get_calculated_runtime("pgmpy"))
        # print(task.mean_runtime('pgmpy'))
        # print(task.get_calculated_evaluation("pyAgrum"))
        # print(task.get_calculated_evaluation("pgmpy"))
        # print(task.get_standard_deviation(task.runtime["pgmpy"]))
        # print(task.get_runtime("pgmpy"))
        # print(task.standard_deviation("pgmpy"))
        # print(task.standard_deviation_evaluation("pgmpy"))

        # task.mean_runtime('pyAgrum')
        # print(task.get_evaluation("pyAgrum"))
        # print(task.mean_evaluation("pyAgrum"))
        # print(task.standard_deviation_evaluation("pyAgrum"))
        # print(task.mean_evaluation("pyAgrum"))

        # print(task.standard_deviation_evaluation("pyAgrum"))
        # print(task.standard_deviation_evaluation("pyAgrum"))
        # print(task.standard_deviation_evaluation("pyAgrum"))
        pass
