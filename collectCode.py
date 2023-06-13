import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import json
from pathlib import Path
from logger import logger


class CollectCode:
    def __init__(self, pathToInfrastructure: str, outputPath=None):
        logger.info("Collecting the code")
        logger.debug(f"Path to infrastructure : {pathToInfrastructure}")
        self.pathToInfrastructure = Path(pathToInfrastructure)

        self.taskNames = []

        self.targets = [path.name for path in self.pathToInfrastructure.glob("targets/*")]

        self.taskPath = list(self.pathToInfrastructure.glob("**/*_run.py"))
        
        
        logger.debug(f"Task path : {self.taskPath}")
        logger.debug(f"Targets : {self.targets}")

        self.pure_code_str = self.RetreiveCode(*self.taskPath)

        self.CodeHTML = {target: {} for target in self.targets}

        self.TransfomCodeInHTML()

    def RetreiveCode(self, *code_path):
        if len(code_path) == 0:
            logger.warning("No path given")
            return {}

        code = {target: {} for target in self.targets}
        for path in code_path:
            # we check if there is a before in the pathName
            # maybe change strategy in the future to be more flexible
            if path.name.split("_")[1] == "before":
                continue
            taskName = path.parent.name
            targetName =path.name.split("_")[0]
            logger.debug(f"Reading code file in {path.absolute()}")
            with open(path.absolute(), "r") as f:
                code[targetName][taskName] = f.read()
        
        logger.info("Code retreived")
            
        return code

    def TransfomCodeInHTML(self):
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

    def SaveInJson(self, outputPath: str):
        with open(outputPath, "w") as file:
            json.dump(self.CodeHTML, file)
        
    def get_code_HTML(self, target, task):
        return self.CodeHTML[target].get(task,"No code found")


if __name__ == "__main__":
    pathToInfrastructure = "C:/Users/jules/Documents/Git/BenchSite/repository"

    collectCode = CollectCode(pathToInfrastructure)
