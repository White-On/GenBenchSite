import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import json

class CollectCode:
    def __init__(self,pathToInfrastructure:str,outputPath = None):

        self.pathToInfrastructure = pathToInfrastructure

        self.taskNames = []
        
        self.themeNames = os.listdir(os.path.join(self.pathToInfrastructure,"themes"))
        self.targets = os.listdir(os.path.join(self.pathToInfrastructure,"targets"))

        self.taskPath = {target:{} for target in self.targets}

        self.RetreiveAllPath()

        self.CodeHTML = {target:{} for target in self.targets}

        self.TransfomCodeInHTML()
        if (outputPath is None):
            outputPath = pathToInfrastructure
        
        self.SaveInJson(os.path.join(outputPath,"code.json"))
    
        
    def RetreiveAllPath(self):
        for themeName in self.themeNames:
            currentTask = os.listdir(os.path.join(self.pathToInfrastructure,"themes",themeName))
            self.taskNames += currentTask
            for task in currentTask:
                for target in self.targets:
                    path = None
                    if (os.path.exists(os.path.join(self.pathToInfrastructure,"themes",themeName,task,f"{target}_run.py"))):
                        path = os.path.join(self.pathToInfrastructure,"themes",themeName,task,f"{target}_run.py")
                    self.taskPath[target][task] = path


    def TransfomCodeInHTML(self):
        for target,value in self.taskPath.items():
            for taskName,path in value.items():
                html = None
                if (path != None):
                    with open(path, 'r') as f:
                        code = f.read()
                        formatter = HtmlFormatter(linenos=True, cssclass="zenburn", noclasses=True, style="zenburn")
                        html = highlight(code, PythonLexer(), formatter)

                self.CodeHTML[target][taskName] = html
    
    def SaveInJson(self,outputPath:str):
        with open(outputPath, 'w') as file:
            json.dump(self.CodeHTML, file)
        
if __name__ == "__main__":
    # pathToInfrastructure = os.path.dirname(os.path.abspath(__file__))
    pathToInfrastructure = "C:/Users/jules/Documents/Git/BenchSite-Experiment/Start_Test/interface"
    collectCode = CollectCode(pathToInfrastructure)
    # collectCode.TransfomCodeInHTML()
    # collectCode.SaveInJson(os.path.join(pathToInfrastructure,"code.json"))