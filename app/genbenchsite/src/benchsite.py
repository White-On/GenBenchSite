from genbenchsite.src.static_site_generator import StaticSiteGenerator
from genbenchsite.src.structure_test import StructureTest
import os
from pathlib import Path

from genbenchsite.src.logger import logger
from genbenchsite.src.json_to_python_object import FileReaderJson
from genbenchsite.src.library import Library
from genbenchsite.src.task import Task
from genbenchsite.src.ranking import (
    RankingLibraryGlobal,
    RankingLibraryByTask,
    RankingLibraryByTheme,
)
from shutil import copyfile
from genbenchsite.src.collectCode import CollectCode
from genbenchsite.src.getMachineData import GetRunMachineMetadata

RemoveUnderscoreAndDash = lambda string: string.replace("_", " ").replace("-", " ")

ABOUT_URL = "https://white-on.github.io/BenchSite/"


class BenchSite:
    LEXMAX_THRESHOLD = 0
    DEFAULT_LOGO = "question.svg"
    DEFAULT_TASK_SCALE = "auto"
    DEFAULT_POST_TASK_SCALE = "auto"

    def __init__(
        self, inputFilename: str, outputPath="pages", structureTestPath="repository"
    ) -> None:
        logger.info("=======Creating BenchSite=======")

        FileReaderJson(inputFilename, structureTestPath)
        self.inputFilename = inputFilename
        self.outputPath = outputPath
        self.structureTestPath = structureTestPath

        logger.debug(f"inputFilename : {inputFilename}")
        logger.debug(f"outputPath : {outputPath}")
        logger.debug(f"structureTestPath : {structureTestPath}")

        # création du site statique
        # relative path to the script, assets and website folder
        self.staticSiteGenerator = StaticSiteGenerator(
            output_website_path=outputPath,
        )

        self.machineData = GetRunMachineMetadata()
        self.siteConfig = self.get_site_config()
        self.benchmarkConfig = self.GetBenchmarkConfig()
        self.setup_global_variables()

    def setup_global_variables(self):
        BenchSite.LEXMAX_THRESHOLD = int(
            self.siteConfig.get("threshold", BenchSite.LEXMAX_THRESHOLD)
        )
        BenchSite.DEFAULT_LOGO = self.siteConfig.get(
            "default_logo", BenchSite.DEFAULT_LOGO
        )
        BenchSite.DEFAULT_TASK_SCALE = self.siteConfig.get(
            "default_task_scale", BenchSite.DEFAULT_TASK_SCALE
        )

    def get_library_config(self):
        strtest = StructureTest()
        libraryConfig = strtest.read_config(
            *strtest.find_config_file(os.path.join(self.structureTestPath, "targets"))
        )
        return libraryConfig

    def get_task_config(self):
        strtest = StructureTest()
        taskConfig = strtest.read_config(
            *strtest.find_config_file(os.path.join(self.structureTestPath, "themes"))
        )
        return taskConfig

    def get_theme_config(self):
        strtest = StructureTest()
        themeConfig = strtest.read_config(
            *strtest.find_config_file(
                os.path.join(self.structureTestPath, "themes"), name="theme.ini"
            )
        )
        return themeConfig

    def get_site_config(self):
        strtest = StructureTest()
        siteConfig = strtest.read_config(
            *strtest.find_config_file(os.path.join(self.structureTestPath, "config")),
            listSection=["site"],
        )
        return siteConfig["config"]

    def GetBenchmarkConfig(self):
        """
        get the benchmark config from the config.ini file in the root folder
        """
        strTest = StructureTest()
        listBenchmarkpath = strTest.find_config_file(
            os.path.join(self.structureTestPath, "config"), name="config.ini"
        )
        benchmarkConfig = strTest.read_config(
            *listBenchmarkpath, listSection=["benchmark"]
        )
        return benchmarkConfig["config"]

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
                    self.staticSiteGenerator.assetsFilePath, BenchSite.DEFAULT_LOGO
                )

        return logo

    def GenerateHTMLBestLibraryGlobal(self):
        contentfilePath = (
            os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        )
        HTMLGlobalRanking = "<div id='global-rank' class='card'>\
                                <h1>Libraries</h1>\
                                <p>Current order for all libraries with all tasks take into account</p>\
                            <div class='grid'>"
        RankGlobal = RankingLibraryGlobal(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )
        HTMLGlobalRanking += "".join(
            # [f"<div class='global-card'><p>{BenchSite.RankSubTitle(rank+1)} : {BenchSite.MakeLink(library)}</p></div>" for rank, library in enumerate(RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD))])
            [
                f'<div class="global-card rank-arrow" data-rank="{RankGlobal}">{library}</div>'
                # f"<div class='global-card'><p>{BenchSite.MakeLink(contentfilePath + library,library)}</p></div>"
                for library in RankGlobal
            ]
        )
        HTMLGlobalRanking += "</div>\
                            </div>"
        return HTMLGlobalRanking

    @staticmethod
    def GenerateHTMLRankingAllTheme():
        HTMLThemeRanking = "<div id='theme-rank'>\
            <h1>Theme Ranking</h1>\
            <p>The best libraries for each theme</p>\
                <div class=\"grid\">"
        rankLibraryInTheme = RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
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
        rankLibraryByTheme = RankingLibraryByTheme(threshold=BenchSite.LEXMAX_THRESHOLD)
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
            <h1>Per Theme</h1>\
            <p>The best libraries for each theme</p>\
                <div class=\"grid\">"
        rankLibraryInTheme = RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD,
            isResultList=False,
        )
        # # On trie le dictionnaire par nom de thème pour avoir un classement par ordre alphabétique
        # rankLibraryInTheme = {
        #     k: v
        #     for k, v in sorted(rankLibraryInTheme.items(), key=lambda item: item[0])
        # }
        for themeName in rankLibraryInTheme.keys():
            HTMLBestTheme += f"<div class='theme-card'><h2>{BenchSite.MakeLink(contentfilePath + themeName,themeName)}</h2><p>({', '.join(BenchSite.MakeLink(contentfilePath + taskName , taskName) for taskName in Task.GetTaskNameByThemeName(themeName))})</p>"
            HTMLBestTheme += f'<p class="rankBar" data-bar="{rankLibraryInTheme[themeName]}"></p></div>'
        HTMLBestTheme += "</div></div>"
        return HTMLBestTheme

    def GenerateHTMLMachineInfo(self):
        HTMLMachineInfo = (
            "<div class ='card' id='machine_info'><h1>Machine Informations</h1>"
        )
        machineData = self.machineData
        if machineData is None:
            HTMLMachineInfo += "<p>No machine informations available</p>"
        else:
            HTMLMachineInfo += "<ul>"
            for key in machineData.keys():
                HTMLMachineInfo += f"<li>{' '.join(key.split('_')[1:]).upper()} : <b>{machineData[key]}</b></li>"
            HTMLMachineInfo += "</ul>"
        HTMLMachineInfo += "</div>"
        return HTMLMachineInfo

    def GenerateHTMLBestLibraryByTask(self):
        contentfilePath = (
            os.path.basename(self.staticSiteGenerator.contentFilePath) + "/"
        )
        HTMLTask = (
            "<div id='task-rank' class='card'><h1>Per Task</h1><div class=\"grid\">"
        )
        rankLibraryInTask = RankingLibraryByTask(
            threshold=BenchSite.LEXMAX_THRESHOLD,
            isResultList=False,
        )
        for taskName in rankLibraryInTask.keys():
            HTMLTask += f'<div class="task-card rankBar" data-bar="{rankLibraryInTask[taskName]}"><h2>{BenchSite.MakeLink(contentfilePath + taskName, taskName)}</h2></div>'
            # HTMLTask += f"<div class='task-card'><h2>{BenchSite.MakeLink(contentfilePath + taskName, taskName)}</h2><p>{BenchSite.MakeLink(contentfilePath + highLightedLibrary, highLightedLibrary)}<p></div>"
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
            "download": "results.json",
        }

        libraryConfig = self.get_library_config()
        taskConfig = self.get_task_config()
        themeConfig = self.get_theme_config()
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
            data=f"{RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD,isResultList = False)}",
            scriptFilePath=f"./{staticSiteGenerator.scriptFilePath}/",
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
            "download": "../results.json",
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

        taskRankDico = RankingLibraryByTask(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for taskName in Task.GetAllTaskName():
            HTMLTaskRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"{taskRankDico[taskName]}",
                dataGenerationDate=self.machineData["execution_date"],
                scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/",
            )

            # CLASSEMENT DES LIBRAIRIES PAR TACHES

            # importedData = [task for task in Task.GetAllTaskByName(taskName)]
            # importedData = [[{"arg":r, "res":c} for r,c in zip(task.arguments,task.results)] for task in Task.GetAllTaskByName(taskName)]
            task = Task.GetTaskByName(taskName)
            importedRuntime = sum(
                [
                    [
                        {
                            "arguments": int(arg) if arg.isnumeric() else arg,
                            "runTime": runtime
                            if runtime != float("inf") and runtime > 0
                            else "error",
                            "libraryName": library.name,
                            "std": std if std != float("inf") and std > 0 else "error",
                        }
                        for arg, runtime, std in zip(
                            task.arguments_label,
                            task.mean_runtime(library.name),
                            task.standard_deviation_runtime(library.name),
                        )
                        # if runtime != float("inf")
                    ]
                    for library in Library.GetAllLibrary()
                ],
                [],
            )

            logger.debug(f"{importedRuntime = }")

            functionEvaluation = taskConfig[taskName].get("evaluation_function", None)
            if functionEvaluation is not None:
                functionEvaluation = functionEvaluation.split(" ")
            else:
                functionEvaluation = []

            task = Task.GetTaskByName(taskName)
            importedEvaluation = {
                function: sum(
                    [
                        [
                            {
                                "arguments": int(arg) if arg.isnumeric() else arg,
                                "runTime": res.get(function, 0)
                                if res.get(function, 0) != float("inf")
                                else "error",
                                "libraryName": library.name,
                                "std": std.get(function, 0)
                                if res.get(function, 0) != float("inf")
                                else "error",
                            }
                            for arg, res, std in zip(
                                task.arguments_label,
                                task.mean_evaluation(library.name),
                                task.standard_deviation_evaluation(library.name),
                            )
                            # if res.get(function) != float("inf")
                        ]
                        for library in Library.GetAllLibrary()
                    ],
                    [],
                )
                for function in functionEvaluation
            }

            logger.debug(f"{importedEvaluation = }")

            chartData = {}
            chartData["runtime"] = {
                "data": importedRuntime,
                "display": taskConfig[taskName].get("task_display", "groupedBar"),
                "label": "Runtime",
                "title": taskConfig[taskName].get("task_title", "Title"),
                "XLabel": taskConfig[taskName].get("task_xlabel", "X-axis"),
                "YLabel": taskConfig[taskName].get("task_ylabel", "Y-axis"),
                "scale": taskConfig[taskName].get("task_scale", "auto"),
                "timeout": taskConfig[taskName].get("timeout"),
            }
            for i, function in enumerate(functionEvaluation):
                xlabel = taskConfig[taskName].get("post_task_xlabel", "X-axis")
                ylabel = (
                    taskConfig[taskName].get("post_task_ylabel", "Y-axis").split(" ")
                )
                scale = taskConfig[taskName].get("post_task_scale", "auto").split(" ")
                title = taskConfig[taskName].get("post_task_title", "Title").split(",")
                chartData[function] = {
                    "data": importedEvaluation[function],
                    "display": taskConfig[taskName].get(
                        "post_task_display", "groupedBar"
                    ),
                    "label": function.capitalize(),
                    "title": title[i] if i < len(title) else title[0],
                    "XLabel": xlabel,
                    "YLabel": ylabel[i] if i < len(ylabel) else ylabel[0],
                    "scale": scale[i] if i < len(scale) else scale[0],
                }
            complementary_description = taskConfig[taskName].get(
                "extra_description", ""
            )
            # we're also adding information relevant to the task in the description
            complementary_description += "<br><br>"
            complementary_description += f"<p>Timeout : {taskConfig[taskName].get('timeout',self.benchmarkConfig.get('default_timeout','No timeout configured'))} (seconds)</p>"
            complementary_description += f"<p>Number of iteration : {taskConfig[taskName].get('nb_runs',self.benchmarkConfig.get('default_nb_runs','No number of iteration configured'))}</p>"
            complementary_description += f"<p>The task is interrupted if the number of timeout reached {self.benchmarkConfig.get('default_stop_after_x_timeout','No number of timeout configured')}</p>"

            HTMLExtra = taskConfig[taskName].get("extra_html_element", None)
            if HTMLExtra is not None:
                try:
                    HTMLExtra = list(
                        Path(self.structureTestPath).glob(f"**/{HTMLExtra}")
                    )[0].read_text()
                # if there is a typo in the extra html element
                except IndexError:
                    HTMLExtra = ""
                    logger.warning(
                        f"Extra HTML element {HTMLExtra} not found in the repository"
                    )
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
                    RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD)[taskName]
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
                extra_description=complementary_description,
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

        themeRankDico = RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for themeName in Task.GetAllThemeName():
            # CLASSEMENT DES LIBRAIRIES PAR TACHES BAR
            HTMLThemeRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"{themeRankDico[themeName]}",
                dataGenerationDate=self.machineData["execution_date"],
                scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/",
            )

            importedRuntime = sum(
                [
                    [
                        {
                            "taskName": taskName,
                            "libraryName": t,
                            "results": RankingLibraryByTask(
                                threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
                            )[taskName][t],
                        }
                        for t in RankingLibraryByTask(
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
            importedRuntime = summaryData + importedRuntime

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
                    content=f"const importedData = {importedRuntime};"
                ),
                description=themeConfig.get(themeName, {}).get(
                    "description", "No description attributed"
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

        libraryDico = RankingLibraryGlobal(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )
        # RANKING BAR GLOBALE
        HTMLGlobalRankingBar = staticSiteGenerator.CreateHTMLComponent(
            "rankBar.html",
            contentFolderPath=contentFilePath,
            data=f"{libraryDico}",
            dataGenerationDate=self.machineData["execution_date"],
            scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/",
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

            importedRuntime = {
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
                            task.mean_runtime(libraryName),
                        )
                        if res >= 0 and res != float("inf")
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
                    content=f"const importedData = {importedRuntime};"
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

        logger.info("=======Static site generated successfully=======")


if __name__ == "__main__":
    # création du site statique
    current_path = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()
    benchSite = BenchSite("results.json")
    pagePath = "pages"
    benchSite.get_library_config()
    benchSite.get_task_config()
    benchSite.GenerateStaticSite()
    benchSite.get_theme_config()
