"""Docstring for Ranking.py module.

This module contains the differents ranking function to rank the library by task, by theme or globaly

"""

import numpy as np

from task import Task
from library import Library

def RankingLibraryByTask(threshold = 0.0, isResultList = True) -> dict[str:list[str]]:
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
    dictionaryTaskLibraryResults = {}
    for taskName in Task.GetAllTaskName():
        dictionaryTaskLibraryResults[taskName] = {}
        for library in Library.GetLibraryByTaskName(taskName):
            dictionaryTaskLibraryResults[taskName][library.name] = library.GetTaskByName(taskName).results
    
    for taskName in dictionaryTaskLibraryResults.keys():
        dictionaryTaskLibraryResults[taskName] = LexMaxWithThreshold(dictionaryTaskLibraryResults[taskName],Task.GetTaskByName(taskName).arguments,threshold)

    if isResultList:
        for taskName in dictionaryTaskLibraryResults.keys():
            dictionaryTaskLibraryResults[taskName] = list(dictionaryTaskLibraryResults[taskName].keys())
    
    return dictionaryTaskLibraryResults


def RankingLibraryByTheme(threshold = 0, isResultList=True) -> dict[str:list[str]]:
    """ Rank all the Library by their results for each theme.

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
            classementLibrary[libraryName] = [rankLibraryByTask[taskName][libraryName] for taskName in listTaskNameForCurrentTheme]
        rankLibraryByTheme[theme] = LexMax(classementLibrary)

    if isResultList:
        for theme in rankLibraryByTheme.keys():
            rankLibraryByTheme[theme] = list(rankLibraryByTheme[theme].keys())

    return rankLibraryByTheme


def RankingLibraryGlobal(threshold = 0, isResultList=True) -> list[str]:
    """ Rank all the Library by their results for each theme.

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
                    classementLibrary[libraryName].append(rankLibraryByTask[taskName][libraryName])

    classementLibrary = LexMax(classementLibrary)

    if isResultList:
        classementLibrary = list(classementLibrary.keys())

    return classementLibrary


def LexMax(dictionnary:dict[str, list[float]]) -> list[str]:
    r""" LexMax algorithm.

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
        rankMatrix[:,column] = [sorted(rankMatrix[:,column].tolist()).index(element) for element in rankMatrix[:,column].tolist()]
    
    # we now sort the rank of each element to have a list of rank for each element sorted
    VectorLibrary = {}
    for i, key in enumerate(dictionnary.keys()):
        VectorLibrary[key] = sorted(rankMatrix[i,:].tolist())
    
    # we can now compare the element by their list of rank
    sortedListRank = sorted(VectorLibrary.items(), key=lambda item: item[1])
    rk = 0
    elementRank = {}
    for i in range (len(sortedListRank)):
        elementRank[sortedListRank[i][0]] = rk
        # if the next element is the same, they share the same rank as the element are equivelent
        if i < len(sortedListRank)-1 and sortedListRank[i][1] != sortedListRank[i+1][1]:
            rk += 1
        
    return elementRank


def LexMaxWithThreshold(dictionaryResults, argumentsList=list(), threshold = 0) -> list:
    """ LexMax algorithm with a threshold.

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
        return LexMax(dictionaryResults)
    
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
        return LexMax(dictionaryResults)

    for key in dictionaryResults.keys():
        dictionaryResults[key] = dictionaryResults[key][iterationLimit:]
    
    return LexMax(dictionaryResults)

if __name__ == "__main__":
    from json_to_python_object import FileReaderJson

    _ = FileReaderJson("result.json")

    print(f"RankingLibraryByTask : {RankingLibraryByTask(threshold=50)}")
    print(f"RankingLibraryByTheme : {RankingLibraryByTheme(threshold=50)}")
    print(f"RankingLibraryGlobal : {RankingLibraryGlobal(threshold=0)}")