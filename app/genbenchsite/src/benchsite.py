from .static_site_generator import StaticSiteGenerator
from .structure_test import (
    get_benchmark_config,
    get_target_config,
    get_theme_config,
    get_task_config,
    get_site_config,
)
import os
from pathlib import Path

from .logger import logger
from .json_to_python_object import FileReaderJson
from .library import Library
from .task import Task
from .ranking import (
    RankingLibraryGlobal,
    RankingLibraryByTask,
    RankingLibraryByTheme,
)
from shutil import copyfile
from .collectCode import CodeReader
from .getMachineData import GetRunMachineMetadata

RemoveUnderscoreAndDash = lambda string: string.replace("_", " ").replace("-", " ")

ABOUT_URL = "https://white-on.github.io/GenBenchSite/"


class BenchSite:
    LEXMAX_THRESHOLD = 0
    DEFAULT_LOGO = "question.svg"
    DEFAULT_TASK_SCALE = "auto"
    DEFAULT_POST_TASK_SCALE = "auto"

    def __init__(
        self, inputFilename: str, outputPath="pages", structureTestPath="repository"
    ) -> None:
        logger.info("=======Creating BenchSite=======")

        if Path(inputFilename).exists() is False:
            logger.error(f"The file containing the results doesn't seems to exist or hasn't been found : File {inputFilename} not found")
            exit(1)
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

        self.machine_data = GetRunMachineMetadata()
        self.site_config = get_site_config(self.structureTestPath)
        self.benchmark_config = get_benchmark_config(self.structureTestPath)
        self.target_config = get_target_config(self.structureTestPath)
        self.theme_config = get_theme_config(self.structureTestPath)
        self.task_config = get_task_config(self.structureTestPath)
        self.setup_global_variables()

    def setup_global_variables(self):
        BenchSite.LEXMAX_THRESHOLD = int(
            self.site_config.get("threshold", BenchSite.LEXMAX_THRESHOLD)
        )
        BenchSite.DEFAULT_LOGO = self.site_config.get(
            "default_logo", BenchSite.DEFAULT_LOGO
        )
        BenchSite.DEFAULT_TASK_SCALE = self.site_config.get(
            "default_task_scale", BenchSite.DEFAULT_TASK_SCALE
        )

    def get_target_logo(self):
        logo = {}
        for libraryName in Library.GetAllLibraryName():
            # if the logo is present we copy it in the assets folder
            # else we just use the default logo
            logo_name = self.target_config.get(libraryName, {}).get("logo", None)
            logo_path = (
                Path(self.structureTestPath) / "res" / logo_name
                if logo_name is not None
                else None
            )
            if logo_path is not None and Path(logo_path).exists():
                # copy the logo in the assets folder
                self.get_new_asset(logo_path)
                logo[libraryName] = (
                    Path(self.staticSiteGenerator.assetsFilePath) / Path(logo_path).name
                )
            else:
                logger.warning(
                    f"Logo for {libraryName} not found at {logo_path}, using default logo"
                )
                logo[libraryName] = (
                    Path(self.staticSiteGenerator.assetsFilePath)
                    / BenchSite.DEFAULT_LOGO
                )
        return logo

    def get_new_asset(self, new_asset_path):
        # check if the new asset exists
        Path(new_asset_path).exists()
        # check if the new asset is a file or a folder
        if Path(new_asset_path).is_dir():
            # if it's a folder we copy all the files in the folder
            for file in Path(new_asset_path).glob("**/*"):
                copyfile(
                    file,
                    Path(self.outputPath)
                    / self.staticSiteGenerator.assetsFilePath
                    / Path(file).name,
                )
        else:
            # if it's a file we copy it in the assets folder
            copyfile(
                new_asset_path,
                Path(self.outputPath)
                / self.staticSiteGenerator.assetsFilePath
                / Path(new_asset_path).name,
            )

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
        machineData = self.machine_data
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

        target_logo = self.get_target_logo()

        logger.info("Generate HTML Home Page")
        logger.debug(f"library config : {self.target_config}")
        logger.debug(f"task config : {self.task_config}")
        logger.debug(f"logo library : {target_logo}")

        social_media_config = self.site_config.get("social_media", {})
        if social_media_config == {}:
            logger.warning("No social media configured in the configuration file of the project")
            social_media = []
        else:
            social_media = list(
                map(
                    lambda x: tuple(x.split(" ")),
                    social_media_config.split(","),
                )
            )
        for element in social_media:
            if len(element) != 2:
                logger.warning(
                    f"Social media element {element} is not in the form 'name url' check the configuration file of the project"
                )
                social_media.remove(element)
        codeLibrary = CodeReader(pathToInfrastructure=self.structureTestPath)

        # GOOGLEANALYTICS
        HTMLGoogleAnalytics = staticSiteGenerator.CreateHTMLComponent(
            "googleAnalytics.html",
            googleAnalyticsID=self.site_config.get("googleAnalyticsID", ""),
        )

        # HEADER
        HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
            "header.html",
            styleFilePath=f"{staticSiteGenerator.styleFilePath}/{styleFilePath}",
            assetsFilePath=f"{staticSiteGenerator.assetsFilePath}",
            linkTo=linkTo,
            siteName=self.site_config.get("name", "No name attributed"),
            socialMediaList=social_media,
        )
        # NAVIGATION
        HTMLNavigation = staticSiteGenerator.CreateHTMLComponent(
            "navigation.html",
            TaskClassifiedByTheme={
                BenchSite.MakeLink(
                    contentFilePath + theme,
                    self.theme_config.get(theme,{}).get("title", theme),
                    f"{theme}-nav",
                ): [
                    BenchSite.MakeLink(
                        contentFilePath + taskName,
                        self.task_config.get(taskName,{}).get("title", taskName),
                        f"{taskName}-nav",
                    )
                    for taskName in Task.GetTaskNameByThemeName(theme)
                ]
                for theme in Task.GetAllThemeName()
            },
            librarylist=[
                "<li class='menu-item'>"
                + BenchSite.MakeLink(
                    contentFilePath + libraryName,
                    strElement=f"<img src='{target_logo[libraryName]}' alt='{libraryName}' class='logo'>{self.target_config[libraryName].get('title',libraryName)}",
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
            dataGenerationDate=self.machine_data.get("execution_date", "No date"),
            data=f"{RankingLibraryGlobal(threshold=BenchSite.LEXMAX_THRESHOLD,isResultList = False)}",
            scriptFilePath=f"./{staticSiteGenerator.scriptFilePath}/",
        )

        # PRESENTATION DE L'OUTIL
        HTMLPresentation = staticSiteGenerator.CreateHTMLComponent(
            "presentation.html",
            siteName=self.site_config.get("name", "No name attributed"),
            siteDescription=self.site_config.get("description", "No description"),
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
            # manualOutputPath=os.path.split(staticSiteGenerator.contentFilePath)[0],
            manualOutputPath=Path(self.outputPath),
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
                BenchSite.MakeLink(
                    theme, self.theme_config.get(theme,{}).get("title", theme), f"{theme}-nav"
                ): [
                    BenchSite.MakeLink(
                        taskName,
                        self.task_config.get(taskName,{}).get("title", taskName),
                        a_balise_id=f"{taskName}-nav",
                    )
                    for taskName in Task.GetTaskNameByThemeName(theme)
                ]
                for theme in Task.GetAllThemeName()
            },
            librarylist=[
                "<li class='menu-item'>"
                + BenchSite.MakeLink(
                    libraryName,
                    strElement=f"<img src='../{target_logo[libraryName]}' alt='{libraryName}' class='logo'>{self.target_config[libraryName].get('title',libraryName)}",
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
            siteName=self.site_config.get("name", "No name attributed"),
            socialMediaList=social_media,
        )

        taskRankDico = RankingLibraryByTask(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for taskName in Task.GetAllTaskName():
            HTMLTaskRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"{taskRankDico.get(taskName, {})}",
                dataGenerationDate=self.machine_data.get("execution_date", "No date"),
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

            scoring_title = self.task_config.get(taskName,{}).get("evaluation_titles", None)
            # evaluation_scripts = self.task_config[taskName].get("evaluation_scripts", None)
            if scoring_title is not None:
                scoring_title = scoring_title.split(",")
            else:
                scoring_title = []

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
                for function in scoring_title
            }

            logger.debug(f"{importedEvaluation = }")

            configuration_task = self.task_config.get(taskName, {})
            if configuration_task == {}:
                logger.warning(
                    f"No configuration found for task {taskName}, using default configuration"
                )

            chartData = {}
            chartData["runtime"] = {
                "data": importedRuntime,
                "display": configuration_task.get("task_display", "groupedBar"),
                "label": "Runtime",
                "title": configuration_task.get("task_title", "Title"),
                "XLabel": configuration_task.get("task_xlabel", "X-axis"),
                "YLabel": configuration_task.get("task_ylabel", "Y-axis"),
                "scale": configuration_task.get("task_scale", "auto"),
                "timeout": configuration_task.get("timeout"),
            }
            for i, function in enumerate(scoring_title):
                xlabel = configuration_task.get("post_task_xlabel", "X-axis")
                ylabel = (
                    configuration_task
                    .get("post_task_ylabel", "Y-axis")
                    .split(" ")
                )
                scale = (
                    configuration_task.get("post_task_scale", "auto").split(" ")
                )
                title = (
                    configuration_task
                    .get("post_task_title", "Title")
                    .split(",")
                )
                chartData[function] = {
                    "data": importedEvaluation.get(function, []),
                    "display": configuration_task.get(
                        "post_task_display", "groupedBar"
                    ),
                    "label": function.capitalize(),
                    "title": title[i] if i < len(title) else title[0],
                    "XLabel": xlabel,
                    "YLabel": ylabel[i] if i < len(ylabel) else ylabel[0],
                    "scale": scale[i] if i < len(scale) else scale[0],
                }
            complementary_description = configuration_task.get(
                "extra_description", ""
            )
            # we're also adding information relevant to the task in the description
            complementary_description += "<br><br>"
            complementary_description += f"<p>Timeout : {configuration_task.get('timeout',self.benchmark_config.get('default_timeout','No timeout configured'))} (seconds)</p>"
            complementary_description += f"<p>Number of iteration : {configuration_task.get('nb_runs',self.benchmark_config.get('default_nb_runs','No number of iteration configured'))}</p>"
            complementary_description += f"<p>The task is interrupted if the number of timeout reached {self.benchmark_config.get('default_stop_after_x_timeout','No number of timeout configured')}</p>"

            HTMLExtra = configuration_task.get("extra_html_element", None)
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
                taskName=self.task_config.get(taskName,{}).get("title", taskName),
                taskNamePage=BenchSite.CreateScriptBalise(
                    content=f"const TaskName = '{taskName}';"
                ),
                scriptFilePath=BenchSite.CreateScriptBalise(
                    scriptName=f"../{staticSiteGenerator.scriptFilePath}/{scriptFilePath}",
                    module=True,
                ),
                libraryOrdered=BenchSite.OrderedList(
                    RankingLibraryByTask(threshold=BenchSite.LEXMAX_THRESHOLD).get(taskName, [])
                ),
                scriptData=BenchSite.CreateScriptBalise(
                    content=f"const importedData = {chartData};"
                ),
                code=templateTask,
                taskDescritpion=self.task_config.get(taskName,{}).get(
                    "description", "No description"
                ),
                argumentsDescription=BenchSite.CreateScriptBalise(
                    content=f"const argDescription = '{self.task_config.get(taskName,{}).get('arguments_description', 'No description')}';"
                ),
                displayScale=BenchSite.CreateScriptBalise(
                    content=f"const displayScale = '{self.task_config.get(taskName,{}).get('display_scale', 'linear')}';"
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
            siteName=self.site_config.get("name", "No name attributed"),
            socialMediaList=social_media,
        )

        themeRankDico = RankingLibraryByTheme(
            threshold=BenchSite.LEXMAX_THRESHOLD, isResultList=False
        )

        for themeName in Task.GetAllThemeName():
            # CLASSEMENT DES LIBRAIRIES PAR TACHES BAR
            HTMLThemeRankingBar = staticSiteGenerator.CreateHTMLComponent(
                "rankBar.html",
                data=f"{themeRankDico.get(themeName, {})}",
                dataGenerationDate=self.machine_data.get("execution_date", "No date"),
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
                        ).get(taskName, [])
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
                themeName=self.theme_config[themeName].get("title", themeName),
                themeNamePage=BenchSite.CreateScriptBalise(
                    content=f"const themeName = '{themeName}';"
                ),
                taskNameList=", ".join(
                    BenchSite.MakeLink(
                        taskName, self.task_config[taskName].get("title", taskName)
                    )
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
                description=self.theme_config.get(themeName, {}).get(
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
            dataGenerationDate=self.machine_data["execution_date"],
            scriptFilePath=f"../{staticSiteGenerator.scriptFilePath}/",
        )

        for libraryName in Library.GetAllLibraryName():
            # HEADER
            HTMLHeader = staticSiteGenerator.CreateHTMLComponent(
                "header.html",
                styleFilePath=f"../{staticSiteGenerator.styleFilePath}/{styleFilePath}",
                assetsFilePath=f"../{staticSiteGenerator.assetsFilePath}",
                linkTo=linkTo,
                siteName=self.site_config.get("name", "No name attributed"),
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
                taskDescription=self.target_config[libraryName].get(
                    "description", "No Description Attributed"
                ),
                logoLibrary=f"<img src='../{target_logo[libraryName]}' alt='{libraryName}' width='50' height='50'>"
                if target_logo[libraryName] != None
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
    benchSite.GenerateStaticSite()
