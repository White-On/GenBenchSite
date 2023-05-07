import numpy as np
from static_site_generator import StaticSiteGenerator
import os

# Here you can import you're own FileReader if the format of the Json/file is different
from json_to_python_object import FileReaderJson, GetMachineData
from library import Library
from task import Task
import ranking as rk
from configparser import ConfigParser
import shutil

class BenchSite:
    LEXMAX_THRESHOLD = 0
    def __init__(self, inputFilename: str, outputPath="pages", structureTestPath ="repository")->None:
        # Here to change you'r own FileReader
        self.libraryList, self.tasksList = FileReaderJson(inputFilename)
        self.inputFilename = inputFilename
        self.outputPath = outputPath
        self.structureTestPath = structureTestPath

        # création du site statique 
        # relative path to the script, assets and website folder
        self.staticSiteGenerator = StaticSiteGenerator(
            os.path.join(outputPath,"script"),
            "htmlTemplate", 
            os.path.join(outputPath,"assets"), 
            os.path.join(outputPath,"content"), 
            os.path.join(outputPath,"style"))

        self.machineData = GetMachineData("machine.json")
        self.siteConfig = self.GetSiteConfiguatrion()
    
    def GetLibraryDescription(self):
        confparser = ConfigParser()
        description = {}
        for libraryName in Library.GetAllLibraryName():
            confparser.read(os.path.join(self.structureTestPath,"targets",libraryName,"config.ini"))
            description[libraryName] = confparser.get(libraryName,"description",fallback="No description available")
        
        return description
    
    def GetSiteConfiguatrion(self):
        confparser = ConfigParser()
        confparser.read(os.path.join(self.structureTestPath,"site","config.ini"))
        siteConfig = {}
        for option in confparser.options("site"):

            siteConfig[option] = confparser["site"][option]
        
        return siteConfig
    
    def GetTaskDescriptionConfig(self):
        confparser = ConfigParser()
        taskConfig = {}
        # on parcours les themes dans le dossier themes
        for themeName in Task.GetAllThemeName():
            currentTask = os.listdir(os.path.join(self.structureTestPath,"themes",themeName))
            for task in currentTask:
                confparser.read(os.path.join(self.structureTestPath,"themes",themeName,task,"config.ini"))
                taskConfig[task] = {}
                for option in confparser.options(task):
                    taskConfig[task][option] = confparser.get(task,option,fallback=f"No {option} available")
                    # taskConfig[task] = {"description":confparser.get(task,"description",fallback="No description available"),"argumentsDescription":confparser.get(task,"arguments_description",fallback="No description available")}
        return taskConfig

    def GetLibraryLogo(self):
        logo = {}
        for libraryName in Library.GetAllLibraryName():
            # if the logo is present we copy it in the assets folder
            # we copy the logo in the assets folder
            if os.path.exists(os.path.join(self.structureTestPath,"targets",libraryName,"logo.png")):
                shutil.copyfile(os.path.join(self.structureTestPath,"targets",libraryName,"logo.png"),os.path.join(self.outputPath,self.staticSiteGenerator.assetsFilePath,libraryName+".png"))
                logo[libraryName] = os.path.join(self.staticSiteGenerator.assetsFilePath,libraryName+".png")
            
            else:
                # logo[libraryName] = os.path.join(self.staticSiteGenerator.assetsFilePath,"default.png")
                logo[libraryName] = os.path.join(self.staticSiteGenerator.assetsFilePath,"question.svg")
        
        return logo

    
    def GenerateHTMLBestLibraryGlobal(self):
        contentfilePath = os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        HTMLGlobalRanking = "<div id='global-rank' class='card'>\
                                <h1>Library</h1>\
                                <p>Here is the ranking of the best library for each task.</p>\
                            <div class='grid'>"
        HTMLGlobalRanking += "".join(
            # [f"<div class='global-card'><p>{BenchSite.RankSubTitle(rank+1)} : {BenchSite.MakeLink(library)}</p></div>" for rank, library in enumerate(rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD))])
            [f"<div class='global-card'><p>{BenchSite.MakeLink(contentfilePath + library,library)}</p></div>" for rank, library in enumerate(rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD))])
        HTMLGlobalRanking += "</div>\
                            </div>"
        return HTMLGlobalRanking
    
    @staticmethod
    def GenerateHTMLRankingAllTheme():
        HTMLThemeRanking = "<div id='theme-rank'>\
            <h1>Theme Ranking</h1>\
            <p>Here is the ranking of the best library for each theme.</p>\
                <div class=\"grid\">"
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
        # HTMLThemeRanking += f"<div class=\"theme\"><h2>{themeName}</h2><h3>{' '.join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName))}</h3>"
        HTMLThemeRanking += "<div class='grid'>" + "".join(
            # [f"<div class='card'><p>{BenchSite.RankSubTitle(rank)} : {BenchSite.MakeLink(library)}</div>" for rank, library in enumerate(rankLibraryByTheme[themeName])])
            [f"<div class='card'><p>{BenchSite.MakeLink(library)}</div>" for rank, library in enumerate(rankLibraryByTheme[themeName])])
        HTMLThemeRanking += "</div>"
        return HTMLThemeRanking

    def GenerateHTMLBestLibraryByTheme(self):
        contentfilePath = os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        HTMLBestTheme = "<div id='theme-rank' class='card'>\
            <h1>Library Per Theme</h1>\
            <p>Here is the ranking of the best library for each theme.</p>\
                <div class=\"grid\">"
        rankLibraryInTheme = rk.RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
        # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        rankLibraryInTheme = {k: v for k, v in sorted(
            rankLibraryInTheme.items(), key=lambda item: item[0])}
        for themeName in rankLibraryInTheme.keys():
            HTMLBestTheme += f"<div class='theme-card'><h2>{BenchSite.MakeLink(contentfilePath + themeName,themeName)}</h2><p>(made of <b>{' '.join(BenchSite.MakeLink(contentfilePath + taskName , taskName) for taskName in Task.GetTaskNameByThemeName(themeName))})</b></p>"
            highLightedLibrary = rankLibraryInTheme[themeName][0]
            HTMLBestTheme += f"<p><b>{BenchSite.MakeLink(contentfilePath+highLightedLibrary,  highLightedLibrary)}</b></p></div>"
        HTMLBestTheme += "</div></div>"
        return HTMLBestTheme

    
    def GenerateHTMLRankingPerTask(self):
        contentfilePath = os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
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
                [f"<tr><td>{BenchSite.MakeLink(contentfilePath + library, library)}</td><td>{value:.3f}</td></tr>" for library, value in DictionaryLibraryResult.items()])
            HTMLTaskRanking += "</table>"
            HTMLTaskRanking += f"<img src=\"../img/{taskName}.png\" alt=\"{taskName}\"></img></div>"
        HTMLTaskRanking += "</div>"
    
        return HTMLTaskRanking
    
    def GenerateHTMLMachineInfo(self):
        HTMLMachineInfo = "<div class ='card'><h1>Machine Info</h1>"
        machineData = self.machineData
        if machineData is None:
            HTMLMachineInfo += "<p>No machine info available</p>"
        else:
            HTMLMachineInfo += "<ul>"
            for key in machineData.keys():
                HTMLMachineInfo += f"<li>{key.replace('_', ' ')} : {machineData[key]}</li>"
            HTMLMachineInfo += "</ul>"
        HTMLMachineInfo += "</div>"
        return HTMLMachineInfo

    def GenerateHTMLBestLibraryByTask(self):
        contentfilePath = os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        HTMLTask = "<div id='task-rank' class='card'><h1> Library Per Task</h1><div class=\"grid\">"
        rankLibraryInTask = rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)
        for taskName in rankLibraryInTask.keys():
            highLightedLibrary = rankLibraryInTask[taskName][0]
            HTMLTask += f"<div class='task-card'><h2>{BenchSite.MakeLink(contentfilePath + taskName, taskName)}</h2><p>{BenchSite.MakeLink(contentfilePath + highLightedLibrary, highLightedLibrary)}<p></div>"
        HTMLTask += "</div>"
        return HTMLTask

    @staticmethod
    def MakeLink(nameElement:str, strElement = None, a_balise_id = None) -> str:
        strElement = nameElement if strElement is None else strElement
        a_balise_id = f"id='{a_balise_id}'" if a_balise_id is not None else ""
        return f"<a href='{nameElement}.html' {a_balise_id}>{strElement}</a>"
    
    @staticmethod
    def RankSubTitle(rank:float) -> str:
        rank = int(rank)
        subtitle = ["st", "nd", "rd", "th"]
        return f"{rank}{subtitle[rank-1] if rank < 4 else subtitle[3]}"
    
    @staticmethod
    def OrderedList(listElement:list) -> str:
        return "&gt;".join([f"{element}" for element in listElement])

    @staticmethod
    def CreateScriptBalise(content="", scriptName=None, module:bool=False) -> str:
        moduleElement = "type='module'" if module else ""
        scriptFilePath = f"src ='{scriptName}'" if scriptName else ""
        return f"<script defer {moduleElement} {scriptFilePath}>{content}</script>"
    
    def GenerateStaticSite(self):
        staticSiteGenerator = self.staticSiteGenerator

        # HOME PAGE
        styleFilePath = 'indexStyle.css'
        scriptFilePath = ''
        contentFilePath = os.path.basename(staticSiteGenerator.contentFilePath) + "/"
        linkTo = {"home":"index.html","about":f"{contentFilePath}about.html","download":"result.json"}
        

        descriptionLibrary = self.GetLibraryDescription()
        descriptionTask = self.GetTaskDescriptionConfig()
        logoLibrary = self.GetLibraryLogo()

        social_media = list(map(lambda x: tuple(x.split(',')),self.siteConfig.get("social_media",{}).split(" ")))

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html", styleFilePath=f"{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                                                                            assetsFilePath=f"{staticSiteGenerator.assetsFilePath}",
                                                                            linkTo=linkTo,
                                                                            siteName = self.siteConfig.get("name","No name attributed"),
                                                                            socialMediaList = social_media,)
        #NAVIGATION
        HTMLNavigation = staticSiteGenerator.CreateHTMLComponent("navigation.html", TaskClassifiedByTheme = {BenchSite.MakeLink(contentFilePath + theme,"&bull; "+theme, f"{theme}-nav"): [BenchSite.MakeLink(contentFilePath + taskName, taskName, f"{taskName}-nav") for taskName in Task.GetTaskNameByThemeName(theme)] for theme in Task.GetAllThemeName()},
                                                                                    librarylist = ["<li class='menu-item'>" + BenchSite.MakeLink(contentFilePath + libraryName, strElement= f"<img src='{logoLibrary[libraryName]}' alt='{libraryName}' class='logo'>{libraryName}", a_balise_id=f"{libraryName}-nav") + "</li>" for libraryName in Library.GetAllLibraryName()],
                                                                                    assetsFilePath=f"{staticSiteGenerator.assetsFilePath}",)
        
        # RANKING BAR GLOBALE
        HTMLGlobalRankingBar = staticSiteGenerator.CreateHTMLComponent("rankBar.html",  contentFolderPath = contentFilePath,
                                                                                        dataGenerationDate = self.machineData["execution_date"],
                                                                                        data = f"const cls = {rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD,isResultList = False)}",
                                                                                        scriptFilePath = f"./{staticSiteGenerator.scriptFilePath}/rankBar.js")

        # PRESENTATION DE L'OUTIL
        HTMLPresentation = staticSiteGenerator.CreateHTMLComponent("presentation.html",     siteName = self.siteConfig["name"],
                                                                                            siteDescription = self.siteConfig["description"],)

        # INFORMATIONS SUR LA MACHINE
        HTMLMachineInfo = self.GenerateHTMLMachineInfo()

        # CLASSEMENT GLOBAL
        HTMLGlobalRanking = self.GenerateHTMLBestLibraryGlobal()

        # CLASSEMENT DES MEILLEURS LIBRAIRIES PAR THEME
        HTMLThemeRanking = self.GenerateHTMLBestLibraryByTheme()

        # CLASSEMENT DES LIBRAIRIES PAR TACHES
        HTMLTaskRanking = self.GenerateHTMLBestLibraryByTask()
        
        HTMLMainContainer = "<div id='main-container'>" + \
                            "".join([HTMLPresentation,HTMLMachineInfo,HTMLGlobalRanking, HTMLThemeRanking, HTMLTaskRanking])\
                            + "</div>"

        # FOOTER
        HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")
        
        staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLNavigation,  HTMLGlobalRankingBar, HTMLMainContainer, HTMLFooter], "index.html",manualOutputPath=os.path.split(staticSiteGenerator.contentFilePath)[0])

        # TACHES PAGES

        styleFilePath = 'taskStyle.css'
        scriptFilePath = 'taskScript.js'
        linkTo = {"home":"../index.html","about":"about.html","download":"../result.json"}
        contentFilePath = "./"

        #NAVIGATION
        HTMLNavigation = staticSiteGenerator.CreateHTMLComponent("navigation.html", TaskClassifiedByTheme = {BenchSite.MakeLink(theme,theme, f"{theme}-nav"): [BenchSite.MakeLink(taskName, a_balise_id=f"{taskName}-nav") for taskName in Task.GetTaskNameByThemeName(theme)] for theme in Task.GetAllThemeName()},
                                                                                    librarylist = ["<li class='menu-item'>" + BenchSite.MakeLink(libraryName, strElement= f"<img src='../{logoLibrary[libraryName]}' alt='{libraryName}' class='logo'>{libraryName}", a_balise_id=f"{libraryName}-nav") + "</li>" for libraryName in Library.GetAllLibraryName()],
                                                                                    assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                                                                                    )
        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html", styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                                                                            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                                                                            linkTo=linkTo,
                                                                            siteName = self.siteConfig.get("name","No name attributed"),
                                                                            socialMediaList = social_media,)
    
        taskRankDico = rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD, isResultList = False)

        for taskName in Task.GetAllTaskName():
            
            HTMLTaskRankingBar = staticSiteGenerator.CreateHTMLComponent("rankBar.html", 
                                                                                       data = f"const cls = {taskRankDico[taskName]}",
                                                                                       dataGenerationDate = self.machineData["execution_date"],
                                                                                       scriptFilePath = f"../{staticSiteGenerator.scriptFilePath}/rankBar.js")
            
            # CLASSEMENT DES LIBRAIRIES PAR TACHES

            # importedData = [task for task in Task.GetAllTaskByName(taskName)]
            # importedData = [[{"arg":r, "res":c} for r,c in zip(task.arguments,task.results)] for task in Task.GetAllTaskByName(taskName)]
            importedData = sum([[{"arguments":arg, "runTime":res if res>0 else 0, "libraryName":library.name}  for arg,res in zip(library.GetTaskByName(taskName).arguments_label,library.GetTaskByName(taskName).results) if library.GetTaskByName(taskName).status =="Run" and res != float("infinity")] for library in Library.GetAllLibrary()],[])
            # print(importedData)

            # create the template for the code
            templateTask = ""
            for library in Library.GetAllLibrary():
                templateTask += f" <div id='{library.name}'>"
                templateTask += f" <h2>{library.name}</h2>"
                templateTask += f" {library.code[taskName]}"
                templateTask += f" </div>"
            


            HTMLTaskRanking = staticSiteGenerator.CreateHTMLComponent("task.html", taskName = taskName,
                                                                                scriptFilePath = BenchSite.CreateScriptBalise(scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",module=True),
                                                                                libraryOrdered = BenchSite.OrderedList(rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)[taskName]),
                                                                                scriptData = BenchSite.CreateScriptBalise(content=f"const importedData = {importedData};"),
                                                                                #    code = BenchSite.CreateScriptBalise(content=f"const code = {code};"),)
                                                                                code = templateTask,
                                                                                taskDescritpion = descriptionTask[taskName]["description"],
                                                                                argumentsDescription = BenchSite.CreateScriptBalise(content=f"const argDescription = '{descriptionTask[taskName]['arguments_description']}';"),
                                                                                displayScale = BenchSite.CreateScriptBalise(content=f"const displayScale = '{descriptionTask[taskName]['display_scale']}';"),)

            staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLNavigation, HTMLTaskRankingBar, HTMLTaskRanking, HTMLFooter], f"{taskName}.html")

        # THEME PAGES

        styleFilePath = 'themeStyle.css'
        scriptFilePath = 'themeScript.js'

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                                                                            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                                                                            linkTo=linkTo,
                                                                            siteName = self.siteConfig.get("name","No name attributed"),
                                                                            socialMediaList = social_media,)
       
        themeRankDico = rk.RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD, isResultList = False)

        for themeName in Task.GetAllThemeName():
            
            # CLASSEMENT DES LIBRAIRIES PAR TACHES BAR
            HTMLThemeRankingBar = staticSiteGenerator.CreateHTMLComponent("rankBar.html",
                                                                                        data = f"const cls = {themeRankDico[themeName]}",
                                                                                        dataGenerationDate = self.machineData["execution_date"],
                                                                                        scriptFilePath = f"../{staticSiteGenerator.scriptFilePath}/rankBar.js")

            importedData = sum([[{"taskName":taskName,"libraryName":t,"results":rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False)[taskName][t]}for t in rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)[taskName]] for taskName in Task.GetTaskNameByThemeName(themeName)],[])
            summaryData = [{"taskName":themeName, "libraryName":libraryName, "results":themeRankDico[themeName][libraryName]} for libraryName in themeRankDico[themeName].keys()]
            importedData = summaryData  + importedData

            # CLASSEMENT DES LIBRAIRIES PAR TACHES
            HTMLThemeRanking = staticSiteGenerator.CreateHTMLComponent("theme.html", themeName=themeName,\
                                                                        taskNameList=" ".join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName)),
                                                                        results = self.GenerateHTMLRankingPerThemeName(themeName),
                                                                        scriptFilePath=BenchSite.CreateScriptBalise(scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",module=True),
                                                                        scriptData = BenchSite.CreateScriptBalise(content=f"const importedData = {importedData};"),)

            staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLNavigation, HTMLThemeRankingBar, HTMLThemeRanking, HTMLFooter], f"{themeName}.html")
        
        # LIBRAIRIES PAGES
        styleFilePath = 'libraryStyle.css'
        scriptFilePath = 'libraryScript.js'

        libraryDico = rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD,isResultList = False)
         # RANKING BAR GLOBALE
        HTMLGlobalRankingBar = staticSiteGenerator.CreateHTMLComponent("rankBar.html",contentFolderPath = contentFilePath,
                                                                                     data = f"const cls = {libraryDico}", 
                                                                                     dataGenerationDate = self.machineData["execution_date"],
                                                                                     scriptFilePath = f"../{staticSiteGenerator.scriptFilePath}/rankBar.js",)

        for libraryName in Library.GetAllLibraryName():
            # HEADER
            HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                                                                                assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                                                                                linkTo=linkTo,
                                                                                siteName = self.siteConfig.get("name","No name attributed"),
                                                                                socialMediaList = social_media,)

            importedData ={task.name:{"display":"plot" if task.arguments_label[0].isnumeric() else "histo", "status":task.status,"data":[{"arguments":float(arg) if arg.isnumeric() else arg, "resultElement":res if res>=0  and res != float("infinity") else 0, "libraryName":libraryName} for arg,res in zip(task.arguments_label,task.results)]} for task in Library.GetLibraryByName(libraryName).tasks}
            # print(importedData)
            # CLASSEMENT DES LIBRAIRIES PAR TACHES
            HTMLLibraryRanking = staticSiteGenerator.CreateHTMLComponent("library.html", libraryName=libraryName, 
                                                                                        taskNameList=[taskName for taskName in Task.GetAllTaskName()],
                                                                                        scriptFilePath=BenchSite.CreateScriptBalise(scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",module=True),
                                                                                        scriptData = BenchSite.CreateScriptBalise(content=f"const importedData = {importedData};"),
                                                                                        taskDescription=descriptionLibrary[libraryName],
                                                                                        logoLibrary = f"<img src='../{logoLibrary[libraryName]}' alt='{libraryName}' width='50' height='50'>" if logoLibrary[libraryName] != None else '',)

            staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLNavigation, HTMLGlobalRankingBar, HTMLLibraryRanking, HTMLFooter], f"{libraryName}.html")

        # ABOUT PAGE

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent("header.html",styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                                                                            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                                                                            linkTo=linkTo,
                                                                            siteName = self.siteConfig.get("name","No name attributed"),
                                                                            socialMediaList = social_media,)
        # ABOUT

        HTMLAbout = staticSiteGenerator.CreateHTMLComponent("aboutContent.html")

        staticSiteGenerator.CreateHTMLPage([HTMLHeader, HTMLNavigation, HTMLAbout, HTMLFooter], "about.html")



if __name__ == "__main__":
    # création du site statique 
    currentPath = os.path.dirname(os.path.realpath(__file__))
    benchSite = BenchSite(os.path.join(currentPath,"result.json"))
    pagePath = "pages"
    benchSite.GenerateStaticSite()