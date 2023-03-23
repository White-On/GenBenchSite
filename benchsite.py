import numpy as np
from static_site_generator import StaticSiteGenerator

# Here you can import you're own FileReader if the format of the Json/file is different
from json_to_python_object import FileReaderJson
from library import Library
from task import Task
import ranking as rk


class BenchSite:
    LEXMAX_THRESHOLD = 50
    def __init__(self, filename: str)->None:
        # Here to change you'r own FileReader
        self.libraryList, self.tasksList = FileReaderJson(filename)

    @staticmethod
    def GenerateHTMLBestLibraryGlobal():
        HTMLGlobalRanking = "<div class=\"card \" id='global'>\
                                <h1>Best Library</h1>\
                            <div class='grid'>"
        HTMLGlobalRanking += "".join(
            [f"<div>{BenchSite.MakeLink(library)}</div>" for library in rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD)])
        HTMLGlobalRanking += "</div>\
                            </div>"
        return HTMLGlobalRanking
    
    @staticmethod
    def GenerateHTMLRankingAllTheme():
        HTMLThemeRanking = "<div id='theme'><h1>Theme Ranking</h1><div class=\"grid\">"
        rankLibraryInTheme = rk.RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
        # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        rankLibraryInTheme = {k: v for k, v in sorted(
            rankLibraryInTheme.items(), key=lambda item: item[0])}
        for theme in rankLibraryInTheme.keys():
            HTMLThemeRanking += f"<div class=\"card theme\"><h2>{theme}</h2><h3>{' '.join(taskName for taskName in Task.GetTaskNameByThemeName(theme))}</h3><ol>"
            HTMLThemeRanking += "".join(
                [f"<li>{library}</li>" for library in rankLibraryInTheme[theme]])
            HTMLThemeRanking += "</ol></div>"
        HTMLThemeRanking += "</div></div>"
        return HTMLThemeRanking

    @staticmethod
    def GenerateHTMLRankingPerThemeName(themeName):
        HTMLThemeRanking = ""
        rankLibraryByTheme = rk.RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
        HTMLThemeRanking += f"<div class=\"card theme\"><h2>{themeName}</h2><h3>{' '.join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName))}</h3><ol>"
        HTMLThemeRanking += "".join(
            [f"<li>{BenchSite.MakeLink(library)}</li>" for library in rankLibraryByTheme[themeName]])
        HTMLThemeRanking += "</ol></div>"
        return HTMLThemeRanking

    @staticmethod
    def GenerateHTMLBestLibraryByTheme():
        HTMLBestTheme = "<div id='theme'><h1>Best Library Per Theme</h1><div class=\"grid\">"
        rankLibraryInTheme = rk.RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
        # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        rankLibraryInTheme = {k: v for k, v in sorted(
            rankLibraryInTheme.items(), key=lambda item: item[0])}
        for themeName in rankLibraryInTheme.keys():
            HTMLBestTheme += f"<div><h2>{BenchSite.MakeLink(themeName)}</h2><h3>{' '.join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName))}</h3>"
            HTMLBestTheme += f"<p>{BenchSite.MakeLink(rankLibraryInTheme[themeName][0])}<p></div>"
        HTMLBestTheme += "</div></div>"
        return HTMLBestTheme

    @staticmethod
    def GenerateHTMLRankingPerTask():
        # Classement des Librairies par tâche
        HTMLTaskRanking = "<div><h1>Task Ranking</h1>"
        rankLibraryInTask = rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)
        for taskName in rankLibraryInTask.keys():
            # On crée le graphique en fonction de tache
            benchSite.CreateGraphics(taskName, Library.GetLibraryByTaskName(taskName), "img")
            # On crée le tableau de classement
            HTMLTaskRanking += f"<h2>{taskName}</h2><div class=\"table-graph\"><table><tr><th>Library</th><th>Value (Run Time or Rank)</th></tr>"
            # Les librairies présentes dans la tâche
            LibraryNameList = rankLibraryInTask[taskName]
            # On crée un dictionnaire avec comme clé le nom de la librairie et comme valeur le score
            DictionaryLibraryResult = {}
            for library in LibraryNameList:
                DictionaryLibraryResult[library] = Library.GetLibraryByName(library).GetTaskByName(taskName).results
            HTMLTaskRanking += "".join(
                [f"<tr><td>{BenchSite.MakeLink(library)}</td><td>{value:.3f}</td></tr>" for library, value in DictionaryLibraryResult.items()])
            HTMLTaskRanking += "</table>"
            HTMLTaskRanking += f"<img src=\"../img/{taskName}.png\" alt=\"{taskName}\"></img></div>"
        HTMLTaskRanking += "</div>"
    
        return HTMLTaskRanking

    @staticmethod
    def GenerateHTMLBestLibraryByTask():
        HTMLTask = "<div id='task'><h1>Best Library Per Task</h1><div class=\"grid\">"
        rankLibraryInTask = rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)
        for taskName in rankLibraryInTask.keys():
            HTMLTask += f"<div><h2>{BenchSite.MakeLink(taskName)}</h2><p>{BenchSite.MakeLink(rankLibraryInTask[taskName][0])}<p></div>"
        HTMLTask += "</div>"
        return HTMLTask

    @staticmethod
    def MakeLink(nameElement:str) -> str:
        return f"<a href='{nameElement}.html'>{nameElement}</a>"

if __name__ == "__main__":
    # création du site statique 
    benchSite = BenchSite("data.json")
    staticSiteGenerator = StaticSiteGenerator(
        "img", "htmlTemplate", "assets", "output", "style")
    
    # HOME PAGE
    # HEADER
    HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",styleFilePath=f"../{staticSiteGenerator.styleFilePath}/indexStyle.css"
                                                                      ,assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}")

    # CLASSEMENT GLOBAL
    HTMLGlobalRanking = benchSite.GenerateHTMLBestLibraryGlobal()

    # CLASSEMENT DES MEILLEURS LIBRAIRIES PAR THEME
    HTMLThemeRanking = benchSite.GenerateHTMLBestLibraryByTheme()

    # CLASSEMENT DES LIBRAIRIES PAR TACHES
    HTMLTaskRanking = benchSite.GenerateHTMLBestLibraryByTask()

    # FOOTER
    HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")

    staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLGlobalRanking, HTMLThemeRanking, HTMLTaskRanking, HTMLFooter], "index.html")

    # # TACHES PAGES
    # for taskName in Task.ListAllTaskName():
    #     # HEADER
    #     HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",CSSFileName="taskStyle.css")

    #     # CLASSEMENT DES LIBRAIRIES PAR TACHES
    #     HTMLTaskRanking = staticSiteGenerator.CreateHTMLComponent("task.html", taskName=taskName)


    #     # FOOTER
    #     HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")

    #     staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLTaskRanking, HTMLFooter], f"{taskName}.html")

    # # THEME PAGES
    # for themeName in Task.ListAllThemeName():
    #     # HEADER
    #     HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",CSSFileName="themeStyle.css")

    #     # CLASSEMENT DES LIBRAIRIES PAR TACHES
    #     HTMLThemeRanking = staticSiteGenerator.CreateHTMLComponent("theme.html", themeName=themeName,\
    #                                                                 taskNameList=" ".join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName)),
    #                                                                 results = benchSite.GenerateHTMLRankingPerThemeName(themeName))   


    #     # FOOTER
    #     HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")

    #     staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLThemeRanking, HTMLFooter], f"{themeName}.html")
    
    # # LIBRAIRIES PAGES
    # for libraryName in Library.ListAllLibraryName():
    #     # HEADER
    #     HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",CSSFileName="libraryStyle.css")

    #     # CLASSEMENT DES LIBRAIRIES PAR TACHES
    #     # TODO faire sans lien d'abord
    #     HTMLLibraryRanking = staticSiteGenerator.CreateHTMLComponent("library.html", libraryName=libraryName, taskNameList=[taskName for taskName in Task.ListAllTaskName()])
    #     # FOOTER
    #     HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")

    #     staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLLibraryRanking, HTMLFooter], f"{libraryName}.html")