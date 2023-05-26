from configparser import ConfigParser
import os
import sys
from logger import logger


class StructureTest:
    def __init__(self) -> None:
        pass

    def readConfig(self, *pathConfig, listSection=[]):
        logger.info("Reading config file")
        logger.debug(f"Path config : {pathConfig}")
        if len(pathConfig) == 0:
            logger.warning("No path given")

        for path in pathConfig:
            if not self.checkPath(path):
                sys.exit(1)

        config = {}
        for path in pathConfig:
            logger.debug(f"Reading config file in {path}")
            configParser = ConfigParser()
            configParser.read(os.path.join(path, "config.ini"))
            sections = configParser.sections() if len(listSection) == 0 else listSection
            logger.debug(f"Sections : {sections}")
            refElement = os.path.basename(path)
            logger.debug(f"Ref element : {refElement}")
            try:
                config[refElement] = {
                    key: configParser.get(section, key)
                    for section in sections
                    for key in configParser.options(section)
                }
            except Exception as e:
                logger.error(f"Error while reading config file : {e}")
                sys.exit(1)
        if len(pathConfig) == 1:
            config = config[refElement]

        logger.info("Config file read")
        logger.debug(f"Config file : {config}")
        return config

    def checkPath(self, path):
        if os.path.exists(path):
            logger.info(f"Path {path} exists")
            if not os.path.exists(os.path.join(path, "config.ini")):
                logger.warning(f"Config file doesn't exist in {path}")
            return True
        else:
            logger.error(f"Path {path} doesn't exist")
            return False

    def findConfigFile(self, path):
        config_files = []

        for root, _, files in os.walk(path):
            for file in files:
                if file == "config.ini":
                    config_files.append(root.replace("\\", "/"))

        return config_files


if __name__ == "__main__":
    pathConfig = "C:/Users/jules/Documents/Git/BenchSite/repository/site"
    listPathConfig = [
        "C:/Users/jules/Documents/Git/BenchSite/repository/targets/bnlearn",
        "C:/Users/jules/Documents/Git/BenchSite/repository/targets/pgmpy",
        "C:/Users/jules/Documents/Git/BenchSite/repository/targets/pyAgrum",
    ]
    test = StructureTest()
    test.readConfig(pathConfig)

    test = StructureTest()
    test.readConfig(*listPathConfig)
