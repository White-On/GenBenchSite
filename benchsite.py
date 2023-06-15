from static_site_generator import StaticSiteGenerator
from structure_test import StructureTest
import os
from pathlib import Path

# Here you can import you're own FileReader if the format of the Json/file is different
from logger import logger
from json_to_python_object import FileReaderJson, readJsonFile
from library import Library
from task import Task
import ranking as rk
from shutil import copyfile
from collectCode import CollectCode
from getMachineData import GetRunMachineMetadata

RemoveUnderscoreAndDash = lambda string: string.replace("_", " ").replace("-", " ")

ABOUT_URL = "https://white-on.github.io/BenchSite/"


class BenchSite:
    LEXMAX_THRESHOLD = 0

    def __init__(
        self, inputFilename: str, outputPath="pages", structureTestPath="repository"
    ) -> None:
        logger.info("=======Creating BenchSite=======")
        # Here to change you'r own FileReader
        FileReaderJson(inputFilename)
        self.inputFilename = inputFilename
        self.outputPath = outputPath
        self.structureTestPath = structureTestPath

        logger.debug(f"inputFilename : {inputFilename}")
        logger.debug(f"outputPath : {outputPath}")
        logger.debug(f"structureTestPath : {structureTestPath}")

        # création du site statique
        # relative path to the script, assets and website folder
        self.staticSiteGenerator = StaticSiteGenerator(
            os.path.join(outputPath, "script"),
            "htmlTemplate",
            os.path.join(outputPath, "assets"),
            os.path.join(outputPath, "content"),
            os.path.join(outputPath, "style"),
        )

        self.machineData = GetRunMachineMetadata()
        self.siteConfig = self.GetSiteConfig()

    def GetLibraryConfig(self):
        strtest = StructureTest()
        libraryConfig = strtest.readConfig(
            *strtest.findConfigFile(os.path.join(self.structureTestPath, "targets"))
        )
        return libraryConfig

    def GetTaskConfig(self):
        listTaskpath = []
        strTest = StructureTest()
        listTaskpath = strTest.findConfigFile(
            os.path.join(self.structureTestPath, "themes")
        )
        taskConfig = strTest.readConfig(*listTaskpath)
        return taskConfig

    def GetSiteConfig(self):
        strtest = StructureTest()
        siteConfig = strtest.readConfig(
            *strtest.findConfigFile(os.path.join(self.structureTestPath, "site"))
        )
        return siteConfig

    def GetLibraryLogo(self):
        logo = {}
        for libraryName in Library.GetAllLibraryName():
            # if the logo is present we copy it in the assets folder
            # we copy the logo in the assets folder
            if os.path.exists(
                os.path.join(self.structureTestPath, "targets", libraryName, "logo.png")
            ):
                copyfile(
                    os.path.join(
                        self.structureTestPath, "targets", libraryName, "logo.png"
                    ),
                    os.path.join(
                        self.outputPath,
                        self.staticSiteGenerator.assetsFilePath,
                        libraryName + ".png",
                    ),
                )
                logo[libraryName] = os.path.join(
                    self.staticSiteGenerator.assetsFilePath, libraryName + ".png"
                )

            else:
                # logo[libraryName] = os.path.join(self.staticSiteGenerator.assetsFilePath,"default.png")
                logo[libraryName] = os.path.join(
                    self.staticSiteGenerator.assetsFilePath, "question.svg"
                )

        return logo

    def GenerateHTMLBestLibraryGlobal(self):
        contentfilePath = (
            os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        )
        HTMLGlobalRanking = "<div id='global-rank' class='card'>\
                                <h1>Library</h1>\
                                <p>Here is the ranking of the best library for each task.</p>\
                            <div class='grid'>"
        HTMLGlobalRanking += "".join(
            # [f"<div class='global-card'><p>{BenchSite.RankSubTitle(rank+1)} : {BenchSite.MakeLink(library)}</p></div>" for rank, library in enumerate(rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD))])
            [
                f"<div class='global-card'><p>{BenchSite.MakeLink(contentfilePath + library,library)}</p></div>"
                for rank, library in enumerate(
                    rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD)
                )
            ]
        )
        HTMLGlobalRanking += "</div>\
                            </div>"
        return HTMLGlobalRanking

    @staticmethod
    def GenerateHTMLRankingAllTheme():
        HTMLThemeRanking = "<div id='theme-rank'>\
            <h1>Theme Ranking</h1>\
            <p>Here is the ranking of the best library for each theme.</p>\
                <div class=\"grid\">"
        rankLibraryInTheme = rk.RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD
        )
        # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        rankLibraryInTheme = {
            k: v
            for k, v in sorted(rankLibraryInTheme.items(), key=lambda item: item[0])
        }
        for theme in rankLibraryInTheme.keys():
            HTMLThemeRanking += f"<div class=\"card theme\"><h2>{theme}</h2><h3>{' '.join(taskName for taskName in Task.GetTaskNameByThemeName(theme))}</h3><ol>"
            HTMLThemeRanking += "".join(
                [f"<li>{library}</li>" for library in rankLibraryInTheme[theme]]
            )
            HTMLThemeRanking += "</ol></div>"
        HTMLThemeRanking += "</div></div>"
        return HTMLThemeRanking

    @staticmethod
    def GenerateHTMLRankingPerThemeName(themeName):
        HTMLThemeRanking = ""
        rankLibraryByTheme = rk.RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD
        )
        # HTMLThemeRanking += f"<div class=\"theme\"><h2>{themeName}</h2><h3>{' '.join(BenchSite.MakeLink(taskName) for taskName in Task.GetTaskNameByThemeName(themeName))}</h3>"
        HTMLThemeRanking += "<div class='grid'>" + "".join(
            # [f"<div class='card'><p>{BenchSite.RankSubTitle(rank)} : {BenchSite.MakeLink(library)}</div>" for rank, library in enumerate(rankLibraryByTheme[themeName])])
            [
                f"<div class='card'><p>{BenchSite.MakeLink(library)}</div>"
                for rank, library in enumerate(rankLibraryByTheme[themeName])
            ]
        )
        HTMLThemeRanking += "</div>"
        return HTMLThemeRanking

    def GenerateHTMLBestLibraryByTheme(self):
        contentfilePath = (
            os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        )
        HTMLBestTheme = "<div id='theme-rank' class='card'>\
            <h1>Library Per Theme</h1>\
            <p>Here is the ranking of the best library for each theme.</p>\
                <div class=\"grid\">"
        rankLibraryInTheme = rk.RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD
        )
        # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        rankLibraryInTheme = {
            k: v
            for k, v in sorted(rankLibraryInTheme.items(), key=lambda item: item[0])
        }
        for themeName in rankLibraryInTheme.keys():
            HTMLBestTheme += f"<div class='theme-card'><h2>{BenchSite.MakeLink(contentfilePath + themeName,themeName)}</h2><p>(made of <b>{', '.join(BenchSite.MakeLink(contentfilePath + taskName , taskName) for taskName in Task.GetTaskNameByThemeName(themeName))})</b></p>"
            highLightedLibrary = rankLibraryInTheme[themeName][0]
            HTMLBestTheme += f"<p><b>{BenchSite.MakeLink(contentfilePath+highLightedLibrary,  highLightedLibrary)}</b></p></div>"
        HTMLBestTheme += "</div></div>"
        return HTMLBestTheme

    def GenerateHTMLMachineInfo(self):
        HTMLMachineInfo = "<div class ='card'><h1>Machine Info</h1>"
        machineData = self.machineData
        if machineData is None:
            HTMLMachineInfo += "<p>No machine info available</p>"
        else:
            HTMLMachineInfo += "<ul>"
            for key in machineData.keys():
                HTMLMachineInfo += (
                    f"<li>{key.replace('_', ' ')} : {machineData[key]}</li>"
                )
            HTMLMachineInfo += "</ul>"
        HTMLMachineInfo += "</div>"
        return HTMLMachineInfo

    def GenerateHTMLBestLibraryByTask(self):
        contentfilePath = (
            os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        )
        HTMLTask = "<div id='task-rank' class='card'><h1> Library Per Task</h1><div class=\"grid\">"
        rankLibraryInTask = rk.RankingLibraryByTask(
            threshold=BenchSite.LEXMAX_THRESHOLD
        )
        for taskName in rankLibraryInTask.keys():
            highLightedLibrary = rankLibraryInTask[taskName][0]
            HTMLTask += f"<div class='task-card'><h2>{BenchSite.MakeLink(contentfilePath + taskName, taskName)}</h2><p>{BenchSite.MakeLink(contentfilePath + highLightedLibrary, highLightedLibrary)}<p></div>"
        HTMLTask += "</div>"
        return HTMLTask

    @staticmethod
    def MakeLink(nameElement: str, strElement=None, a_balise_id=None) -> str:
        strElement = nameElement if strElement is None else strElement
        a_balise_id = f"id='{a_balise_id}'" if a_balise_id is not None else ""
        return f"<a href='{nameElement}.html' {a_balise_id}>{RemoveUnderscoreAndDash(strElement)}</a>"

    @staticmethod
    def RankSubTitle(rank: float) -> str:
        rank = int(rank)
        subtitle = ["st", "nd", "rd", "th"]
        return f"{rank}{subtitle[rank-1] if rank < 4 else subtitle[3]}"

    @staticmethod
    def OrderedList(listElement: list) -> str:
        return "&gt;".join([f"{element}" for element in listElement])

    @staticmethod
    def CreateScriptBalise(content="", scriptName=None, module: bool = False) -> str:
        moduleElement = "type='module'" if module else ""
        scriptFilePath = f"src ='{scriptName}'" if scriptName else ""
        return f"<script defer {moduleElement} {scriptFilePath}>{content}</script>"

    def GenerateStaticSite(self):
        staticSiteGenerator = self.staticSiteGenerator

        # ==================================================
        # HOME PAGE
        # ==================================================
        styleFilePath = "indexStyle.css"
        scriptFilePath = ""
        contentFilePath = os.path.basename(staticSiteGenerator.contentFilePath) + "/"
        linkTo = {
            "home": "index.html",
            # "about": f"{contentFilePath}about.html",
            "about": ABOUT_URL,
            "download": "result.json",
        }

        libraryConfig = self.GetLibraryConfig()
        taskConfig = self.GetTaskConfig()
        logoLibrary = self.GetLibraryLogo()

        logger.info("Generate HTML Home Page")
        logger.debug(f"library config : {libraryConfig}")
        logger.debug(f"task config : {taskConfig}")
        logger.debug(f"logo library : {logoLibrary}")

        social_media = list(
            map(
                lambda x: tuple(x.split(",")),
                self.siteConfig.get("social_media", {}).split(" "),
            )
        )

        codeLibrary = CollectCode(pathToInfrastructure=self.structureTestPath)

        # GOOGLEANALYTICS
        HTMLGoogleAnalytics = staticSiteGenerator.CreateHTMLComponent(
            "googleAnalytics.html",
            googleAnalyticsID=self.siteConfig.get("googleAnalyticsID", ""),
        )

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
            "header.html",
            styleFilePath=f"{staticSiteGenerator.styleFilePath}/{styleFilePath}",
            assetsFilePath=f"{staticSiteGenerator.assetsFilePath}",
            linkTo=linkTo,
            siteName=self.siteConfig.get("name", "No name attributed"),
            socialMediaList=social_media,
        )
        # NAVIGATION
        HTMLNavigation = staticSiteGenerator.CreateHTMLComponent(
            "navigation.html",
            TaskClassifiedByTheme={
                BenchSite.MakeLink(contentFilePath + theme, theme, f"{theme}-nav"): [
                    BenchSite.MakeLink(
                        contentFilePath + taskName, taskName, f"{taskName}-nav"
                    )
                    for taskName in Task.GetTaskNameByThemeName(theme)
                ]
                for theme in Task.GetAllThemeName()
            },
            librarylist=[
                "<li class='menu-item'>"
                + BenchSite.MakeLink(
                    contentFilePath + libraryName,
                    strElement=f"<img src='{logoLibrary[libraryName]}' alt='{libraryName}' class='logo'>{libraryName}",
                    a_balise_id=f"{libraryName}-nav",
                )
                + "</li>"
                for libraryName in Library.GetAllLibraryName()
            ],
            assetsFilePath=f"{staticSiteGenerator.assetsFilePath}",
        )

        # RANKING BAR GLOBALE
        HTMLGlobalRankingBar = staticSiteGenerator.CreateHTMLComponent(
            "rankBar.html",
            contentFolderPath=contentFilePath,
            dataGenerationDate=self.machineData["execution_date"],
            data=f"const cls = {rk.RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD,isResultList = False)}",
            scriptFilePath=f"./{staticSiteGenerator.scriptFilePath}/rankBar.js",
        )

        # PRESENTATION DE L'OUTIL
        HTMLPresentation = staticSiteGenerator.CreateHTMLComponent(
            "presentation.html",
            siteName=self.siteConfig["name"],
            siteDescription=self.siteConfig["description"],
        )

        # INFORMATIONS SUR LA MACHINE
        HTMLMachineInfo = self.GenerateHTMLMachineInfo()

        # CLASSEMENT GLOBAL
        HTMLGlobalRanking = self.GenerateHTMLBestLibraryGlobal()

        # CLASSEMENT DES MEILLEURS LIBRAIRIES PAR THEME
        HTMLThemeRanking = self.GenerateHTMLBestLibraryByTheme()

        # CLASSEMENT DES LIBRAIRIES PAR TACHES
        HTMLTaskRanking = self.GenerateHTMLBestLibraryByTask()

        HTMLMainContainer = (
            "<div id='main-container'>"
            + "".join(
                [
                    HTMLPresentation,
                    HTMLMachineInfo,
                    HTMLGlobalRanking,
                    HTMLThemeRanking,
                    HTMLTaskRanking,
                ]
            )
            + "</div>"
        )

        # FOOTER
        HTMLFooter = staticSiteGenerator.CreateHTMLComponent("footer.html")

        staticSiteGenerator.CreateHTMLPage(
            [
                HTMLHeader,
                HTMLNavigation,
                HTMLGlobalRankingBar,
                HTMLMainContainer,
                HTMLGoogleAnalytics,
                HTMLFooter,
            ],
            "index.html",
            manualOutputPath=os.path.split(staticSiteGenerator.contentFilePath)[0],
        )
        # ==================================================
        # TACHES PAGES
        # ==================================================

        styleFilePath = "taskStyle.css"
        scriptFilePath = "taskScript.js"
        linkTo = {
            "home": "../index.html",
            "about": ABOUT_URL,
            "download": "../result.json",
        }
        contentFilePath = "./"

        # NAVIGATION
        HTMLNavigation = staticSiteGenerator.CreateHTMLComponent(
            "navigation.html",
            TaskClassifiedByTheme={
                BenchSite.MakeLink(theme, theme, f"{theme}-nav"): [
                    BenchSite.MakeLink(
                        taskName, taskName, a_balise_id=f"{taskName}-nav"
                    )
                    for taskName in Task.GetTaskNameByThemeName(theme)
                ]
                for theme in Task.GetAllThemeName()
            },
            librarylist=[
                "<li class='menu-item'>"
                + BenchSite.MakeLink(
                    libraryName,
                    strElement=f"<img src='../{logoLibrary[libraryName]}' alt='{libraryName}' class='logo'>{libraryName}",
                    a_balise_id=f"{libraryName}-nav",
                )
                + "</li>"
                for libraryName in Library.GetAllLibraryName()
            ],
            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
        )
        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
            "header.html",
            styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
            linkTo=linkTo,
            siteName=self.siteConfig.get("name", "No name attributed"),
            socialMediaList=social_media,
        )

        taskRankDico = rk.RankingLibraryByTask(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for taskName in Task.GetAllTaskName():
            HTMLTaskRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"const cls = {taskRankDico[taskName]}",
                dataGenerationDate=self.machineData["execution_date"],
                scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/rankBar.js",
            )

            # CLASSEMENT DES LIBRAIRIES PAR TACHES

            # importedData = [task for task in Task.GetAllTaskByName(taskName)]
            # importedData = [[{"arg":r, "res":c} for r,c in zip(task.arguments,task.results)] for task in Task.GetAllTaskByName(taskName)]
            importedData = sum(
                [
                    [
                        {
                            "arguments": int(arg) if arg.isnumeric() else arg,
                            "runTime": res if res > 0 and res != "Error" else 0,
                            "libraryName": library.name,
                        }
                        for arg, res in zip(
                            library.GetTaskByName(taskName).arguments_label,
                            library.GetTaskByName(taskName).get_calculated_runtime(
                                library.name
                            ),
                        )
                        if res != float("infinity")
                    ]
                    for library in Library.GetAllLibrary()
                ],
                [],
            )

            logger.debug(importedData)

            importedResults = sum(
                [
                    [
                        {
                            "arguments": arg,
                            "runTime": res if res > 0 and res != "Error" else 0,
                            "libraryName": library.name,
                        }
                        for arg, res in zip(
                            library.GetTaskByName(taskName).arguments_label,
                            library.GetTaskByName(taskName).get_calculated_runtime(
                                library.name
                            ),
                        )
                        if res != None
                    ]
                    for library in Library.GetAllLibrary()
                ],
                [],
            )

            logger.debug(importedResults)
            chartData = {
                "runtime": {
                    "data": importedData,
                    "display": taskConfig[taskName].get("task_display", "groupedBar"),
                    "title": "Runtime",
                    "XLabel": taskConfig[taskName].get("task_xlabel", "X-axis"),
                    "YLabel": taskConfig[taskName].get("task_ylabel", "Y-axis"),
                    "scale": taskConfig[taskName].get("task_scale", "auto"),
                },
                "eval": {
                    "data": importedResults,
                    "display": taskConfig[taskName].get(
                        "post_task_display", "groupedBar"
                    ),
                    "title": "Evaluation",
                    "XLabel": taskConfig[taskName].get("post_task_xlabel", "X-axis"),
                    "YLabel": taskConfig[taskName].get("post_task_ylabel", "Y-axis"),
                    "scale": taskConfig[taskName].get("post_task_scale", "auto"),
                },
            }

            HTMLExtra = taskConfig[taskName].get("extra_html_element", None)
            if HTMLExtra is not None:
                HTMLExtra = list(Path(self.structureTestPath).glob(f"**/{HTMLExtra}"))[
                    0
                ].read_text()
            else:
                HTMLExtra = ""

            # print(importedResults)
            # create the template for the code
            templateTask = ""
            for library in Library.GetAllLibrary():
                templateTask += f" <code id='{library.name}'>"
                templateTask += f" <h2>{library.name}</h2>"
                templateTask += f" {codeLibrary.get_code_HTML(library.name, taskName)}"
                templateTask += f" </code>"

            HTMLTaskRanking = staticSiteGenerator.CreateHTMLComponent(
                "task.html",
                taskName=RemoveUnderscoreAndDash(taskName),
                taskNamePage=BenchSite.CreateScriptBalise(
                    content=f"const TaskName = '{taskName}';"
                ),
                scriptFilePath=BenchSite.CreateScriptBalise(
                    scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",
                    module=True,
                ),
                libraryOrdered=BenchSite.OrderedList(
                    rk.RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)[
                        taskName
                    ]
                ),
                scriptData=BenchSite.CreateScriptBalise(
                    content=f"const importedData = {chartData};"
                ),
                code=templateTask,
                taskDescritpion=taskConfig[taskName].get(
                    "description", "No description"
                ),
                argumentsDescription=BenchSite.CreateScriptBalise(
                    content=f"const argDescription = '{taskConfig[taskName].get('arguments_description', 'No description')}';"
                ),
                displayScale=BenchSite.CreateScriptBalise(
                    content=f"const displayScale = '{taskConfig[taskName].get('display_scale', 'linear')}';"
                ),
                extra_html_element=HTMLExtra,
                extra_description=taskConfig[taskName].get("extra_description", ""),
            )

            staticSiteGenerator.CreateHTMLPage(
                [
                    HTMLHeader,
                    HTMLNavigation,
                    HTMLTaskRankingBar,
                    HTMLTaskRanking,
                    HTMLGoogleAnalytics,
                    HTMLFooter,
                ],
                f"{taskName}.html",
            )

        # ==================================================
        # THEME PAGES
        # ==================================================

        styleFilePath = "themeStyle.css"
        scriptFilePath = "themeScript.js"

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
            "header.html",
            styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
            linkTo=linkTo,
            siteName=self.siteConfig.get("name", "No name attributed"),
            socialMediaList=social_media,
        )

        themeRankDico = rk.RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for themeName in Task.GetAllThemeName():
            # CLASSEMENT DES LIBRAIRIES PAR TACHES BAR
            HTMLThemeRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"const cls = {themeRankDico[themeName]}",
                dataGenerationDate=self.machineData["execution_date"],
                scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/rankBar.js",
            )

            importedData = sum(
                [
                    [
                        {
                            "taskName": taskName,
                            "libraryName": t,
                            "results": rk.RankingLibraryByTask(
                                threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
                            )[taskName][t],
                        }
                        for t in rk.RankingLibraryByTask(
                            threshold=BenchSite.LEXMAX_THRESHOLD
                        )[taskName]
                    ]
                    for taskName in Task.GetTaskNameByThemeName(themeName)
                ],
                [],
            )
            summaryData = [
                {
                    # we need to consider the theme name as a task name
                    "taskName": themeName,
                    "libraryName": libraryName,
                    "results": themeRankDico[themeName][libraryName],
                }
                for libraryName in themeRankDico[themeName].keys()
            ]
            importedData = summaryData + importedData

            # CLASSEMENT DES LIBRAIRIES PAR TACHES
            HTMLThemeRanking = staticSiteGenerator.CreateHTMLComponent(
                "theme.html",
                themeName=RemoveUnderscoreAndDash(themeName),
                themeNamePage=BenchSite.CreateScriptBalise(
                    content=f"const themeName = '{themeName}';"
                ),
                taskNameList=", ".join(
                    BenchSite.MakeLink(taskName)
                    for taskName in Task.GetTaskNameByThemeName(themeName)
                ),
                results=self.GenerateHTMLRankingPerThemeName(themeName),
                scriptFilePath=BenchSite.CreateScriptBalise(
                    scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",
                    module=True,
                ),
                scriptData=BenchSite.CreateScriptBalise(
                    content=f"const importedData = {importedData};"
                ),
            )

            staticSiteGenerator.CreateHTMLPage(
                [
                    HTMLHeader,
                    HTMLNavigation,
                    HTMLThemeRankingBar,
                    HTMLThemeRanking,
                    HTMLGoogleAnalytics,
                    HTMLFooter,
                ],
                f"{themeName}.html",
            )

        # ==================================================
        # LIBRAIRIES PAGES
        # ==================================================

        styleFilePath = "libraryStyle.css"
        scriptFilePath = "libraryScript.js"

        libraryDico = rk.RankingLibraryGlobal(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )
        # RANKING BAR GLOBALE
        HTMLGlobalRankingBar = staticSiteGenerator.CreateHTMLComponent(
            "rankBar.html",
            contentFolderPath=contentFilePath,
            data=f"const cls = {libraryDico}",
            dataGenerationDate=self.machineData["execution_date"],
            scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/rankBar.js",
        )

        for libraryName in Library.GetAllLibraryName():
            # HEADER
            HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
                "header.html",
                styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                linkTo=linkTo,
                siteName=self.siteConfig.get("name", "No name attributed"),
                socialMediaList=social_media,
            )

            importedData = {
                task.name: {
                    "display": "plot"
                    if task.arguments_label[0].isnumeric()
                    else "histo",
                    "status": task.get_status(target=libraryName),
                    "data": [
                        {
                            "arguments": float(arg) if arg.isnumeric() else arg,
                            "resultElement": res,
                            "libraryName": libraryName,
                        }
                        for arg, res in zip(
                            task.arguments_label,
                            task.get_calculated_runtime(libraryName),
                        )
                        if res >= 0 and res != float("infinity")
                    ],
                }
                for task in Library.GetLibraryByName(libraryName).tasks
            }
            # print(importedData)
            # CLASSEMENT DES LIBRAIRIES PAR TACHES
            HTMLLibraryRanking = staticSiteGenerator.CreateHTMLComponent(
                "library.html",
                libraryName=libraryName,
                taskNameList=[
                    (taskName, RemoveUnderscoreAndDash(taskName))
                    for taskName in Task.GetAllTaskName()
                ],
                scriptFilePath=BenchSite.CreateScriptBalise(
                    scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",
                    module=True,
                ),
                scriptData=BenchSite.CreateScriptBalise(
                    content=f"const importedData = {importedData};"
                ),
                taskDescription=libraryConfig[libraryName].get(
                    "description", "No Description Attributed"
                ),
                logoLibrary=f"<img src='../{logoLibrary[libraryName]}' alt='{libraryName}' width='50' height='50'>"
                if logoLibrary[libraryName] != None
                else "",
            )

            staticSiteGenerator.CreateHTMLPage(
                [
                    HTMLHeader,
                    HTMLNavigation,
                    HTMLGlobalRankingBar,
                    HTMLLibraryRanking,
                    HTMLGoogleAnalytics,
                    HTMLFooter,
                ],
                f"{libraryName}.html",
            )

        # ==================================================
        # ABOUT PAGE
        # ==================================================
        styleFilePath = "aboutStyle.css"

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
            "header.html",
            styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
            assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
            linkTo=linkTo,
            siteName=self.siteConfig.get("name", "No name attributed"),
            socialMediaList=social_media,
        )
        # ABOUT

        HTMLAbout = staticSiteGenerator.CreateHTMLComponent(
            "aboutContent.html",
            assetFolder=f"../{staticSiteGenerator.assetsFilePath}",
        )

        staticSiteGenerator.CreateHTMLPage(
            [HTMLHeader, HTMLNavigation, HTMLAbout, HTMLFooter], "about.html"
        )

        logger.info("=======Static site generated successfully=======")


if __name__ == "__main__":
    # création du site statique
    currentPath = os.path.dirname(os.path.realpath(__file__))
    benchSite = BenchSite(os.path.join(currentPath, "results.json"))
    pagePath = "pages"
    benchSite.GetLibraryConfig()
    benchSite.GetTaskConfig()
    benchSite.GenerateStaticSite()
