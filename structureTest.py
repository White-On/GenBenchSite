from configparser import ConfigParser
import os
import sys

class StructureTest:
    def __init__(self, pathStructureTest) -> None:
        
        self.taskCongif = {}
        self.targetConfig = {}

        self.pathStructureTest = pathStructureTest

    
    def readConfig(self, pathConfig):
        configParser = ConfigParser()
        configParser.read(os.path.join(pathConfig, "config.ini"))
        section = configParser.sections()[0]
        return {key : configParser.get(section, key) for key in configParser.options(section)}