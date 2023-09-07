"""Docstring for Ranking.py module.

This module contains the differents ranking function to rank the library by task, by theme or globaly

"""

import numpy as np

from .task import Task
from .library import Library
from pprint import pprint


def RankingMethod(*args, **kwargs):
    return LexMaxWithThreshold(*args, **kwargs)


def RankingLibraryByTask(threshold=0.0, isResultList=True) -> dict[str, list[str]]:
    r"""Rank all the Library by their results for each task.

    Each library has a list of result for each task. For each result we apply the LexMax algorithm
    on the argument of the task. The result is a list of library name sorted by their rank compiled inside a
    dictionary with the task name as key. The threshold is used to remove the result with an argument that are under the threshold.

    Parameters
    ----------
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    isResultList : bool, default=True
        If True, the result will be a list of library name sorted by their rank. If False, the result will be a dictionary with the library name as key and their rank as value.

    Returns
    -------
    dictionaryTaskLibraryResults : dict of str and list of str
        A dictionary with the task name as key and a list of library name sorted by their rank as value.

    See Also
    --------
    LexMax : The LexMax algorithm.
    LexMaxWithThreshold : The LexMax algorithm with a threshold.

    Examples
    --------
    >>> from task import Task
    >>> from library import Library
    >>> from json_to_python_object import FileReaderJson
    >>> libraryList, taskList = FileReaderJson("data.json")
    >>> print(RankingLibraryByTask())
    {'Task1': ['Library1', 'Library2', 'Library3'], 'Task2': ['Library1', 'Library2', 'Library3'], 'Task3': ['Library1', 'Library2', 'Library3']}
    """
    rank_over_all_aspect = {}
    # we collect the ranking by runtime and by eval
    rank_task_runtime = RankingLibraryByTaskRuntime(threshold, isResultList=False)
    rank_task_eval = RankingLibraryByTaskEval(threshold, isResultList=False)
    # we merge the two ranking to be able to lexmax them
    for taskName in Task.GetAllTaskName():
        dictionaryTaskLibraryResults = []
        rank_over_all_aspect[taskName] = {}
        # we only add the eval ranking if there is an eval function for the task
        dictionaryTaskLibraryResults.append(rank_task_eval[taskName]) if len(
            rank_task_eval[taskName]
        ) > 0 else None
        dictionaryTaskLibraryResults.append(rank_task_runtime[taskName])
        tmp = {}
        for library in Library.GetAllLibraryName():
            tmp[library] = [
                ranking[library]
                for ranking in dictionaryTaskLibraryResults
                if library in ranking.keys()
            ]

        rank_over_all_aspect[taskName] = RankingMethod(tmp, [], threshold=threshold)

    # we convert the result to a list if needed
    if isResultList:
        for taskName in rank_over_all_aspect.keys():
            rank_over_all_aspect[taskName] = list(rank_over_all_aspect[taskName].keys())

    return rank_over_all_aspect


def RankingLibraryByTaskRuntime(
    threshold=0.0, isResultList=True
) -> dict[str, list[str]]:
    r"""Rank all the Library by their results for each task.

    Each library has a list of result for each task. For each result we apply the LexMax algorithm
    on the argument of the task. The result is a list of library name sorted by their rank compiled inside a
    dictionary with the task name as key. The threshold is used to remove the result with an argument that are under the threshold.

    Parameters
    ----------
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    Returns
    -------
    dictionaryTaskLibraryResults : dict of str and list of str
        A dictionary with the task name as key and a list of library name sorted by their rank as value.

    See Also
    --------
    LexMax : The LexMax algorithm.
    LexMaxWithThreshold : The LexMax algorithm with a threshold.

    Examples
    --------
    >>> from task import Task
    >>> from library import Library
    >>> from json_to_python_object import FileReaderJson
    >>> libraryList, taskList = FileReaderJson("data.json")
    >>> print(RankingLibraryByTask())
    {'Task1': ['Library1', 'Library2', 'Library3'], 'Task2': ['Library1', 'Library2', 'Library3'], 'Task3': ['Library1', 'Library2', 'Library3']}
    """
    # the goal here is to create a dictionary with the runtime of each library for each task
    dictionaryTaskLibraryRuntime = {}
    for taskName in Task.GetAllTaskName():
        dictionaryTaskLibraryRuntime[taskName] = {}
        for library in Library.GetLibraryByTaskName(taskName):
            dictionaryTaskLibraryRuntime[taskName][
                library.name
            ] = library.GetTaskByName(taskName).mean_runtime(library.name)

    # we apply the ranking method on the runtime
    for taskName in dictionaryTaskLibraryRuntime.keys():
        dictionaryTaskLibraryRuntime[taskName] = RankingMethod(
            dictionaryTaskLibraryRuntime[taskName],
            Task.GetTaskByName(taskName).arguments,
            threshold,
        )

    # we convert the result to a list if needed
    if isResultList:
        for taskName in dictionaryTaskLibraryRuntime.keys():
            dictionaryTaskLibraryRuntime[taskName] = list(
                dictionaryTaskLibraryRuntime[taskName].keys()
            )

    return dictionaryTaskLibraryRuntime


def RankingLibraryByTaskEval(threshold=0.0, isResultList=True) -> dict[str, list[str]]:
    rank_task_eval = {}
    for taskName in Task.GetAllTaskName():
        dictionaryTaskLibraryResults = []
        rank_task_eval[taskName] = {}
        eval_function = Task.GetTaskByName(taskName).evaluation_function_name
        # if there is no evaluation function for the task, we skip it
        if len(eval_function) == 0:
            continue
        # we apply the ranking method on each evaluation function according to the sort order ( asc or desc )
        # can be changed in the config file of the task
        for function_name, sort_order in zip(
            eval_function, Task.GetTaskByName(taskName).evaluation_sort_order
        ):
            dictionaryTaskLibraryResults.append(
                RankingLibraryByEvaluation(
                    taskName, function_name, threshold, sort_order
                )
            )

        # we merge the ranking of each evaluation function
        # so we have a dictionary with the library name as key and a list of rank for each evaluation function
        rank_task_eval[taskName] = RankingMethod(
            {
                library: [ranking[library] for ranking in dictionaryTaskLibraryResults]
                for library in Library.GetAllLibraryName()
            },
            [],
            threshold=threshold,
        )

    # we convert the result to a list if needed
    if isResultList:
        for taskName in rank_task_eval.keys():
            rank_task_eval[taskName] = list(rank_task_eval[taskName].keys())

    return rank_task_eval


def RankingLibraryByEvaluation(
    task_name, function_name, threshold=0, sort_order="desc"
) -> dict[str, list[str]]:
    """Rank all the Library by their results for each task.

    Each library has a list of result for each task. For each result we apply the LexMax algorithm
    on the argument of the task. The result is a list of library name sorted by their rank compiled inside a
    dictionary with the task name as key. The threshold is used to remove the result with an argument that are under the threshold.

    Parameters
    ----------
    task_name : str
        The name of the task.
    function_name : str
        The name of the evaluation function.
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    Returns
    -------
    dictionaryTaskLibraryResults : dict of str and list of str
        A dictionary with the task name as key and a list of library name sorted by their rank as value.

    See Also
    --------
    LexMax : The LexMax algorithm.
    LexMaxWithThreshold : The LexMax algorithm with a threshold.

    Examples
    --------
    >>> from task import Task
    >>> from library import Library
    >>> from json_to_python_object import FileReaderJson
    >>> libraryList, taskList = FileReaderJson("data.json")


    """
    rank_task_function = {}
    # we check if the task exists and if it has an evaluation function
    if task_name not in Task.GetAllTaskName():
        return rank_task_function
    eval_function = Task.GetTaskByName(task_name).evaluation_function_name
    # if there is no evaluation function for the task, we skip it
    if len(eval_function) == 0 or function_name not in eval_function:
        return rank_task_function

    for library in Library.GetLibraryByTaskName(task_name):
        # we apply the ranking method on each evaluation function according to the sort order ( asc or desc )
        results = library.GetTaskByName(task_name).mean_evaluation(library.name)
        # if the task has not been evaluated, we set the rank to inf
        if all([r == float("inf") for r in results]):
            rank_task_function[library.name] = [float("inf") for r in results]
        else:
            rank_task_function[library.name] = [r.get(function_name) for r in results]
    rank_task_function = RankingMethod(
        rank_task_function,
        Task.GetTaskByName(task_name).arguments,
        threshold=threshold,
        reverse=sort_order == "asc",
    )
    return rank_task_function


def RankingLibraryByTheme(threshold=0, isResultList=True) -> dict[str, list[str]]:
    """Rank all the Library by their results for each theme.

    Each library has a list of result for each task. For each result we apply the LexMax algorithm
    on the argument of the task. The result is a list of library name sorted by their rank compiled inside a
    dictionary with the theme name as key. The threshold is used to remove the result with an argument that are under the threshold.

    Parameters
    ----------
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    Returns
    -------
    dictionaryThemeLibraryResults : dict of str and list of str
        A dictionary with the theme name as key and a list of library name sorted by their rank as value.

    See Also
    --------
    LexMax : The LexMax algorithm.
    LexMaxWithThreshold : The LexMax algorithm with a threshold.

    Examples
    --------
    >>> from task import Task
    >>> from library import Library
    >>> from json_to_python_object import FileReaderJson
    >>> libraryList, taskList = FileReaderJson("data.json")
    >>> print(RankingLibraryByTheme())
    {'Theme1': ['Library1', 'Library2', 'Library3'], 'Theme2': ['Library1', 'Library2', 'Library3'], 'Theme3': ['Library1', 'Library2', 'Library3']}

    """
    rankLibraryByTask = RankingLibraryByTask(threshold=threshold, isResultList=False)
    rankLibraryByTheme = {}

    for theme in Task.GetAllThemeName():
        listTaskNameForCurrentTheme = Task.GetTaskNameByThemeName(theme)
        classementLibrary = {}
        for libraryName in Library.GetAllLibraryName():
            classementLibrary[libraryName] = [
                rankLibraryByTask[taskName][libraryName]
                for taskName in listTaskNameForCurrentTheme
            ]
        rankLibraryByTheme[theme] = LexMax(classementLibrary)

    if isResultList:
        for theme in rankLibraryByTheme.keys():
            rankLibraryByTheme[theme] = list(rankLibraryByTheme[theme].keys())

    return rankLibraryByTheme


def RankingLibraryGlobal(threshold=0, isResultList=True) -> list[str]:
    """Rank all the Library by their results for each theme.

    Each library has a list of result for each task. For each result we apply the LexMax algorithm
    on the argument of the task. The result is a list of library name sorted by their rank compiled inside a
    dictionary with the theme name as key. The threshold is used to remove the result with an argument that are under the threshold.

    Parameters
    ----------
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    Returns
    -------
    list of str
        A list of library name sorted by their global rank.

    See Also
    --------
    LexMax : The LexMax algorithm.
    LexMaxWithThreshold : The LexMax algorithm with a threshold.

    """

    rankLibraryByTask = RankingLibraryByTask(threshold=threshold, isResultList=False)
    classementLibrary = {}
    for libraryName in Library.GetAllLibraryName():
        classementLibrary[libraryName] = []
        for taskName in rankLibraryByTask.keys():
            classementLibrary[libraryName].append(
                rankLibraryByTask[taskName][libraryName]
            )

    classementLibrary = LexMax(classementLibrary)

    if isResultList:
        classementLibrary = list(classementLibrary.keys())

    return classementLibrary


def LexMax(dictionnary: dict[str, list[float]], reverse=False) -> list[str]:
    r"""LexMax algorithm.

    The LexMax algorithm is used to rank dictionnary of result.

    Parameters
    ----------
    dictionnary : dict of str and list of float
        A dictionary with a value representing the all the results for a experiment.

    Returns
    -------
    list of str
        a list of the element sorted by their rank.

    Examples
    --------

    >>> dictionnary = {'Library1': [52.2, 42.1, 39.4], 'Library2': [45.2, 12.0, 80.2], 'Library3': [34.7, 15.8, 2.42]}
    >>> print(LexMax(dictionnary))
    ['Library3', 'Library2', 'Library1']

    # You can also use it on a dictionary with a list of rank
    >>> dictionnary = {'Library1': [3, 3, 2], 'Library2': [2, 1, 3], 'Library3': [1, 2, 1]}
    >>> print(LexMax(dictionnary))
    ['Library3', 'Library2', 'Library1']
    """
    rankMatrix = np.zeros((len(dictionnary.keys()), len(list(dictionnary.values())[0])))
    # On remplit la matrice avec les valeurs du dictionnaire
    for i, key in enumerate(dictionnary.keys()):
        for j, value in enumerate(dictionnary[key]):
            rankMatrix[i, j] = value

    # for each column we sort the value and we replace the value by their rank
    # the sort here will give a rank no matter the precision of the value
    for column in range(rankMatrix.shape[1]):
        rankMatrix[:, column] = [
            sorted(rankMatrix[:, column].tolist(), reverse=reverse).index(element)
            for element in rankMatrix[:, column].tolist()
        ]
    # print(rankMatrix)
    # we now sort the rank of each element to have a list of rank for each element sorted
    VectorLibrary = {}
    for i, key in enumerate(dictionnary.keys()):
        VectorLibrary[key] = sorted(rankMatrix[i, :].tolist())

    # print(VectorLibrary)
    # we can now compare the element by their list of rank
    sortedListRank = sorted(VectorLibrary.items(), key=lambda item: item[1])
    rk = 0
    elementRank = {}
    for i in range(len(sortedListRank)):
        elementRank[sortedListRank[i][0]] = rk
        # if the next element is the same, they share the same rank as the element are equivelent
        if (
            i < len(sortedListRank) - 1
            and sortedListRank[i][1] != sortedListRank[i + 1][1]
        ):
            rk += 1
    return elementRank


def LexMaxWithThreshold(
    dictionaryResults, argumentsList=list(), threshold=0, reverse=False
) -> list:
    """LexMax algorithm with a threshold.

    The LexMax algorithm is used to rank dictionnary of result. The threshold is used to remove the result with an argument that are strictly under the threshold.

    Parameters
    ----------
    dictionaryResults : dict of str and list of float
        A dictionary with a value representing the all the results for a experiment.
    argumentsList : list of float, default=list()
        A list of argument for each result.
    threshold : float, default=0.0
        The threshold to remove the result with an argument that are under the threshold.

    Returns
    -------
    list of str
        a list of the element sorted by their rank.

    See Also
    --------
    LexMax : The LexMax algorithm.

    Examples
    --------
    >>> dictionnary = {'Library1': [52.2, 42.1, 39.4], 'Library2': [45.2, 12.0, 80.2], 'Library3': [34.7, 15.8, 2.42]}
    >>> argumentsList = [0.1, 0.2, 0.3]
    >>> print(LexMaxWithThreshold(dictionnary, argumentsList, threshold=0.2))
    # Here only the result with an argument greater than 0.2 are used
    ['Library3', 'Library1', 'Library2']
    """
    if threshold == 0 or len(argumentsList) == 0:
        return LexMax(dictionaryResults, reverse=reverse)

    # On cherche la limite d'itération pour ne récuperer que les résultats dont
    # la valeur de l'argument est supérieur au seuil
    iterationLimit = 0
    for argument in argumentsList:
        if argument < threshold:
            iterationLimit += 1
        else:
            break

    # Si la limite d'itération est égale à la taille de la liste des arguments
    # cela veut dire que le seuil est trop élevé et que il n'y a pas de résultat
    if iterationLimit == len(argumentsList):
        # print("The threshold is too high, the LexMax algorithm will return without threshold")
        return LexMax(dictionaryResults, reverse=reverse)

    for key in dictionaryResults.keys():
        dictionaryResults[key] = dictionaryResults[key][iterationLimit:]

    return LexMax(dictionaryResults, reverse=reverse)


if __name__ == "__main__":
    from json_to_python_object import FileReaderJson

    _ = FileReaderJson(
        "results.json", "C:/Users/jules/Documents/Git/BenchSite/repository"
    )
    # _ = FileReaderJson(
    #     "results.json", "D:/Jules_Scolaire/Master_Androide_M1/BenchSite/repository"
    # )

    # print(f"RankingLibraryByTask : {RankingLibraryByTask(threshold=0)}")
    # print(f"RankingLibraryByTheme : {RankingLibraryByTheme(threshold=0)}")
    # print(f"RankingLibraryGlobal : {RankingLibraryGlobal(threshold=0)}")
    # pprint(f"RankingLibraryByTaskEval : {RankingLibraryByTaskEval(threshold=0)}")
    # pprint(f"RankingLibraryByTaskEval : {RankingLibraryByTaskRuntime(threshold=0,isResultList=False)}")
    pprint(f"RankingLibraryByTask : {RankingLibraryByTask(threshold=0)}")
