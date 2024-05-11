from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pathlib import Path
from .logger import logger


class CodeReader:
    """
    The goal of this class is to read the code of the test infrastructure and transform it in HTML
    """

    noTaskFoundMessage = "Task not found"
    noCodeFoundMessage = "Code not found"

    def __init__(self, pathToInfrastructure: str):
        logger.info("Reading the code from the test infrastructure")
        logger.debug(f"Path to infrastructure : {pathToInfrastructure}")
        self.pathToInfrastructure = Path(pathToInfrastructure)

        themesPath = self.pathToInfrastructure / "themes"
        individualThemePath = [theme for theme in themesPath.iterdir() if theme.is_dir()]
        self.tasksPath = []
        for theme in individualThemePath:
            tasksPath = [task for task in theme.iterdir() if task.is_dir()]
            self.tasksPath.extend(tasksPath)

        self.tasksPath = {task.name: task for task in self.tasksPath}

        logger.debug(f"Task path : {self.tasksPath}")


    def pure_code_to_html(self, code: str):
        formatter = HtmlFormatter(
            linenos=True,
            cssclass="zenburn",
            noclasses=True,
            style="zenburn",
        )
        return highlight(code, PythonLexer(), formatter)

    def get_code_HTML(self, target : str, task :str):
        """
        Get the code of a task in HTML format
        """
        task_path = self.tasksPath.get(task, None)
        task_path_exists = task_path is not None
        if not task_path_exists:
            return CodeReader.noTaskFoundMessage
        
        target_code_path = task_path / target / "run.py"
        target_code_path_exists = target_code_path.exists()
        if not target_code_path_exists:
            return CodeReader.noCodeFoundMessage
        
        with open(target_code_path, "r") as f:
            logger.info(f"Reading code file in {target_code_path.absolute()}")
            code = f.read()

        return self.pure_code_to_html(code)


if __name__ == "__main__":
    pathToInfrastructure = "D:/Jules_Scolaire/Master_Androide_M1/BenchSite/repository"

    collectCode = CodeReader(pathToInfrastructure)
