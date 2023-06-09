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
        # if outputPath is None:
        #     outputPath = pathToInfrastructure

        # self.SaveInJson(os.path.join(outputPath, "code.json"))

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
            
        return code

    def TransfomCodeInHTML(self):
        for target, value in self.taskPath.items():
            for taskName, path in value.items():
                html = None
                if path != None:
                    with open(path, "r") as f:
                        code = f.read()
                        formatter = HtmlFormatter(
                            linenos=True,
                            cssclass="zenburn",
                            noclasses=True,
                            style="zenburn",
                        )
                        html = highlight(code, PythonLexer(), formatter)

                self.CodeHTML[target][taskName] = html

    def SaveInJson(self, outputPath: str):
        with open(outputPath, "w") as file:
            json.dump(self.CodeHTML, file)
        
    def get_code_HTML(self, target, task):
        return self.CodeHTML[target][task]


if __name__ == "__main__":
    # pathToInfrastructure = os.path.dirname(os.path.abspath(__file__))
    pathToInfrastructure = "C:/Users/jules/Documents/Git/BenchSite/repository"

    collectCode = CollectCode(pathToInfrastructure)
    # collectCode.TransfomCodeInHTML()
    # collectCode.SaveInJson(os.path.join(pathToInfrastructure,"code.json"))
