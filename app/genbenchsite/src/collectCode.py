from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import json
from pathlib import Path
from logger import logger


class CodeReader:
    def __init__(self, pathToInfrastructure: str):
        logger.info("Collecting the code")
        logger.debug(f"Path to infrastructure : {pathToInfrastructure}")
        self.pathToInfrastructure = Path(pathToInfrastructure)

        self.taskNames = []

        self.targets = [
            path.name for path in self.pathToInfrastructure.glob("targets/*")
        ]

        self.taskPath = list(self.pathToInfrastructure.glob("**/run.py"))

        logger.debug(f"Task path : {self.taskPath}")
        logger.debug(f"Targets : {self.targets}")

        self.pure_code_str = self.retreive_code(*self.taskPath)

        self.CodeHTML = {target: {} for target in self.targets}

        self.all_code_to_html()
        logger.info("=======Code collected=======")

    def retreive_code(self, *code_path):
        if len(code_path) == 0:
            logger.warning("No path given")
            return {}

        code = {target: {} for target in self.targets}
        for path in code_path:
            taskName = path.parents[1].name
            targetName = path.parents[0].name
            logger.debug(f"Reading code file in {path.absolute()}")
            with open(path.absolute(), "r") as f:
                code[targetName][taskName] = f.read()

        logger.info("Code retreived")

        return code

    def all_code_to_html(self):
        for target in self.targets:
            for task in self.pure_code_str[target]:
                self.CodeHTML[target][task] = self.pure_code_to_html(
                    self.pure_code_str[target][task]
                )
        logger.info("Code transformed in HTML")
        logger.debug(f"Code HTML : {self.CodeHTML.keys()}")

    def pure_code_to_html(self, code: str):
        formatter = HtmlFormatter(
            linenos=True,
            cssclass="zenburn",
            noclasses=True,
            style="zenburn",
        )
        return highlight(code, PythonLexer(), formatter)

    def save_json(self, outputPath: str):
        with open(outputPath, "w") as file:
            json.dump(self.CodeHTML, file)

    def get_code_HTML(self, target, task):
        return self.CodeHTML[target].get(task, None)


if __name__ == "__main__":
    pathToInfrastructure = "D:/Jules_Scolaire/Master_Androide_M1/BenchSite/repository"

    collectCode = CodeReader(pathToInfrastructure)
    print(collectCode.get_code_HTML("target1", "task1"))
